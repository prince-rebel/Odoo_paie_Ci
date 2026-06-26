# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PrimeType(models.Model):
    _name = 'hr_payroll_custom.prime_type'
    _description = 'Type de prime / rubrique salariale'
    _order = 'name'

    name = fields.Char('Libellé', required=True)
    code = fields.Char('Code', required=True, size=10,
                        help="Code unique de la rubrique (ex: LOG, RESP_DIR, PROD). "
                             "Max 10 caractères, sans espaces.")
    is_taxable = fields.Boolean(
        'Imposable', default=True,
        help="Coché = prime imposable (entre dans le Brut, soumise à ITS et CNPS).\n"
             "Décoché = prime non imposable (ex: transport, logement NI — ajoutée au Brut Total uniquement)."
    )
    appears_on_payslip = fields.Boolean('Visible sur bulletin', default=True)
    description = fields.Char('Description')
    active = fields.Boolean(default=True)

    # Rubrique gérée par le système (TRSP, ASM, CMU) : pas de règle auto-créée
    is_system = fields.Boolean('Rubrique système', default=False, readonly=True,
                                help="Les rubriques système sont gérées par le module. "
                                     "Leur règle salariale est définie dans le code et ne peut pas être supprimée.")

    salary_rule_id = fields.Many2one(
        'hr.salary.rule', 'Règle salariale (auto)', readonly=True, ondelete='set null'
    )
    input_type_id = fields.Many2one(
        'hr.payslip.input.type', "Type d'entrée (auto)", readonly=True, ondelete='set null'
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Ce code est déjà utilisé. Choisissez un code unique.')
    ]

    @api.constrains('code')
    def _check_code(self):
        for rec in self:
            if not rec.code.isidentifier():
                raise ValidationError(
                    f"Le code '{rec.code}' est invalide. Utilisez uniquement des lettres, chiffres et '_', "
                    f"sans espaces ni caractères spéciaux."
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._setup_salary_infrastructure()
        return records

    def write(self, vals):
        res = super().write(vals)
        # Cascade name/visibility changes to the auto-created rule and input type.
        # Internal linking fields and is_system are excluded from triggering cascade.
        if set(vals.keys()) - {'salary_rule_id', 'input_type_id', 'active', 'is_system'}:
            for rec in self:
                if rec.is_system:
                    continue  # System primes: don't cascade name to shared rules/input_types
                update = {}
                if 'name' in vals:
                    update['name'] = rec.name
                if 'appears_on_payslip' in vals:
                    update['appears_on_payslip'] = rec.appears_on_payslip
                if update:
                    if rec.salary_rule_id:
                        rec.salary_rule_id.write(update)
                    if rec.input_type_id and 'name' in update:
                        rec.input_type_id.write({'name': rec.name})
        return res

    def unlink(self):
        for rec in self:
            if rec.is_system:
                raise ValidationError(
                    f"La rubrique '{rec.name}' est une rubrique système et ne peut pas être supprimée."
                )
            if rec.salary_rule_id:
                rec.salary_rule_id.write({'active': False})
            if rec.input_type_id:
                rec.input_type_id.write({'active': False})
        return super().unlink()

    def action_migrate_legacy_premiums(self):
        """
        Migrate FixedPremiums lines that use input_type_id directly (TRSP, ASM, CMU)
        to the corresponding prime_type_id. Safe to run multiple times.
        """
        if not self.env.user.has_group('hr_payroll.group_hr_payroll_manager'):
            raise ValidationError("Seuls les gestionnaires de paie peuvent effectuer cette migration.")
        prime_types = self.env['hr_payroll_custom.prime_type'].search([
            ('input_type_id', '!=', False)
        ])
        prime_by_input_id = {pt.input_type_id.id: pt.id for pt in prime_types}

        if not prime_by_input_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Migration',
                    'message': "Aucun type de prime avec type d'entrée trouvé.",
                    'type': 'warning',
                },
            }

        lines = self.env['hr_payroll_custom.fixed_premiums'].search([
            ('prime_type_id', '=', False),
            ('input_type_id', 'in', list(prime_by_input_id.keys())),
        ])
        count = 0
        for line in lines:
            pt_id = prime_by_input_id.get(line.input_type_id.id)
            if pt_id:
                line.write({'prime_type_id': pt_id})
                count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Migration terminée',
                'message': f"{count} ligne(s) de primes migrée(s) avec succès.",
                'type': 'success',
                'sticky': False,
            },
        }

    def _setup_salary_infrastructure(self):
        """Find or create hr.payslip.input.type and hr.salary.rule for this prime type."""
        self.ensure_one()

        # 1. Find or create input type — never create a duplicate by code
        input_type = self.env['hr.payslip.input.type'].search(
            [('code', '=', self.code)], limit=1
        )
        if not input_type:
            input_type = self.env['hr.payslip.input.type'].create({
                'name': self.name,
                'code': self.code,
            })

        # 2. System primes reuse existing infrastructure — no new rule created
        if self.is_system:
            self.write({'input_type_id': input_type.id})
            return

        # 3. Locate the payroll structure
        structure = self.env.ref('hr_payroll_custom.structure_cdi_cdd', raise_if_not_found=False)
        if not structure:
            self.write({'input_type_id': input_type.id})
            return

        # 4. Choose category: PRIM (imposable) or INDMNI (non-imposable)
        if self.is_taxable:
            category = self.env.ref('hr_payroll_custom.cat_prim', raise_if_not_found=False)
            seq_start = 130  # after PANC(102), before BRUT(300)
        else:
            category = self.env.ref('hr_payroll_custom.cat_indmni', raise_if_not_found=False)
            seq_start = 520  # after TRSP(501)

        if not category:
            self.write({'input_type_id': input_type.id})
            return

        # 4. Find a free sequence in this structure
        used_seqs = set(
            self.env['hr.salary.rule']
            .search([('struct_id', '=', structure.id)])
            .mapped('sequence')
        )
        seq = seq_start
        while seq in used_seqs:
            seq += 1

        # 5. Build Python formulas with the actual code
        code = self.code
        condition = f"result = inputs.get('{code}')"
        formula = f"result = inputs['{code}'].amount"

        # 6. Create the salary rule
        rule = self.env['hr.salary.rule'].create({
            'name': self.name,
            'code': code,
            'sequence': seq,
            'struct_id': structure.id,
            'category_id': category.id,
            'condition_select': 'python',
            'condition_python': condition,
            'amount_select': 'code',
            'amount_python_compute': formula,
            'appears_on_payslip': self.appears_on_payslip,
        })

        # Link back (goes through write() but 'salary_rule_id'/'input_type_id' are excluded from cascade)
        self.write({
            'salary_rule_id': rule.id,
            'input_type_id': input_type.id,
        })
