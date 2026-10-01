# -*- coding:utf-8 -*-
"""État résumé des cotisations mensuel.

Synthèse, par rubrique de cotisation (impôts, CNPS, FDFP...), des taux,
assiettes, bases, montants salariaux / patronaux et effectifs H/F sur une
période donnée. Les rubriques sont paramétrables (Configuration > Déclaration
Fiscale/Sociale > Rubriques état résumé) et pointent vers des codes de règles
salariales, ce qui les rend indépendantes de la structure salariale utilisée.
"""

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ContributionSummaryGroup(models.Model):
    _name = 'hr_payroll_custom.contribution_summary_group'
    _description = "Groupe de rubriques - état résumé des cotisations"
    _order = 'sequence, id'

    name = fields.Char("Libellé du total", required=True, help="Ex. : IMPOT, C.N.P.S, F D F P")
    sequence = fields.Integer("Séquence", default=10)
    active = fields.Boolean(default=True)
    rubric_ids = fields.One2many('hr_payroll_custom.contribution_summary_rubric', 'group_id', "Rubriques")


class ContributionSummaryRubric(models.Model):
    _name = 'hr_payroll_custom.contribution_summary_rubric'
    _description = "Rubrique - état résumé des cotisations"
    _order = 'group_sequence, sequence, code, id'

    sequence = fields.Integer("Séquence", default=10)
    code = fields.Char("N° rubrique", required=True)
    name = fields.Char("Libellé", required=True)
    group_id = fields.Many2one('hr_payroll_custom.contribution_summary_group', "Groupe", required=True,
                               ondelete='restrict')
    group_sequence = fields.Integer(related='group_id.sequence', store=True, string="Séquence du groupe")
    employee_rule_code = fields.Char(
        "Code règle part salariale",
        help="Code de la règle salariale portant la retenue salariale (ex. : CNPS, ITS, CMU).")
    employer_rule_code = fields.Char(
        "Code règle part patronale",
        help="Code de la règle salariale portant la charge patronale (ex. : CNPS_P, PF, TAXEFP).")
    assiette_code = fields.Char(
        "Code règle assiette", default='BRUT', required=True,
        help="Code de la règle dont le total constitue l'assiette de cotisation (par défaut : BRUT).")
    rate_employee = fields.Float("Taux salarial (%)", digits=(5, 2), compute='_compute_rates', store=True,
                                 readonly=False)
    rate_employer = fields.Float("Taux patronal (%)", digits=(5, 2), compute='_compute_rates', store=True,
                                 readonly=False)
    company_id = fields.Many2one('res.company', "Société", help="Laisser vide pour toutes les sociétés.")
    active = fields.Boolean(default=True)

    @api.model
    def _find_percentage_rule(self, code):
        if not code:
            return self.env['hr.salary.rule']
        return self.env['hr.salary.rule'].search(
            [('code', '=', code), ('amount_select', '=', 'percentage')], limit=1)

    @api.depends('employee_rule_code', 'employer_rule_code')
    def _compute_rates(self):
        """Taux repris de la règle salariale quand elle est en pourcentage ;
        sinon (règle en code Python, ex. CMU) le taux saisi est conservé."""
        for rubric in self:
            for code_field, rate_field in (('employee_rule_code', 'rate_employee'),
                                           ('employer_rule_code', 'rate_employer')):
                code = rubric[code_field]
                rule = rubric._find_percentage_rule(code)
                if rule:
                    rubric[rate_field] = rule.amount_percentage
                elif not code:
                    rubric[rate_field] = 0.0
                else:
                    rubric[rate_field] = rubric[rate_field] or 0.0

    @api.constrains('employee_rule_code', 'employer_rule_code')
    def _check_rule_codes(self):
        for rubric in self:
            if not rubric.employee_rule_code and not rubric.employer_rule_code:
                raise ValidationError(_("La rubrique %s doit avoir au moins un code de règle (salariale ou patronale).",
                                  rubric.display_name))

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for rubric in self:
            rubric.display_name = f"{rubric.code} {rubric.name}" if rubric.code else rubric.name


class ContributionSummary(models.Model):
    _name = 'hr_payroll_custom.contribution_summary'
    _description = "État résumé des cotisations"
    _order = 'date_from desc, id desc'

    name = fields.Char("Libellé", required=True)
    date_from = fields.Date("Date de début", required=True)
    date_to = fields.Date("Date de fin", required=True)
    company_id = fields.Many2one('res.company', "Société", required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    closure_mode = fields.Selection(
        [('after', "Après clôture mensuelle"), ('before', "Avant clôture mensuelle")],
        string="Bulletins pris en compte", required=True, default='after',
        help="Après clôture : uniquement les bulletins validés ou payés.\n"
             "Avant clôture : tous les bulletins non annulés (brouillons compris), pour contrôle avant validation.")
    employee_ids = fields.Many2many('hr.employee', string="Salariés",
                                    help="Laisser vide pour tous les salariés de la société.")
    line_ids = fields.One2many('hr_payroll_custom.contribution_summary_line', 'summary_id', "Lignes")
    payslip_count = fields.Integer("Nombre de bulletins", readonly=True)
    total_employee = fields.Float("Total salarial", digits=(16, 0), compute='_compute_totals', store=True)
    total_employer = fields.Float("Total patronal", digits=(16, 0), compute='_compute_totals', store=True)
    total_global = fields.Float("Total global", digits=(16, 0), compute='_compute_totals', store=True)
    compute_date = fields.Datetime("Calculé le", readonly=True)

    @api.depends('line_ids.amount_employee', 'line_ids.amount_employer')
    def _compute_totals(self):
        for rec in self:
            rec.total_employee = sum(rec.line_ids.mapped('amount_employee'))
            rec.total_employer = sum(rec.line_ids.mapped('amount_employer'))
            rec.total_global = rec.total_employee + rec.total_employer

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(_("La date de début doit être antérieure à la date de fin."))

    # ------------------------------------------------------------------
    # Calcul
    # ------------------------------------------------------------------
    def _get_payslips(self):
        self.ensure_one()
        domain = [('company_id', '=', self.company_id.id),
                  ('date_from', '>=', self.date_from),
                  ('date_to', '<=', self.date_to)]
        if self.closure_mode == 'after':
            domain.append(('state', 'in', ('validated', 'paid')))
        else:
            domain.append(('state', '!=', 'cancel'))
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        return self.env['hr.payslip'].search(domain)

    def _get_rubrics(self):
        self.ensure_one()
        return self.env['hr_payroll_custom.contribution_summary_rubric'].search(
            [('group_id.active', '=', True), '|', ('company_id', '=', False),
             ('company_id', '=', self.company_id.id)])

    @api.model
    def _get_employee_sex(self, employee):
        """Odoo 19 : champ `sex` ; versions antérieures : `gender`."""
        for fname in ('sex', 'gender'):
            if fname in employee._fields:
                return employee[fname]
        return False

    def action_compute(self):
        Line = self.env['hr_payroll_custom.contribution_summary_line']
        for rec in self:
            rec.line_ids.unlink()
            slips = rec._get_payslips()
            rubrics = rec._get_rubrics()
            if not rubrics:
                raise UserError(_("Aucune rubrique n'est paramétrée pour l'état résumé des cotisations."))

            codes = set()
            for rubric in rubrics:
                codes.update(c for c in (rubric.employee_rule_code, rubric.employer_rule_code,
                                         rubric.assiette_code) if c)

            # data[slip_id][code] = (somme des bases `amount`, somme des `total`)
            data = defaultdict(dict)
            slip_employee = {}
            if slips:
                self.env.cr.execute("""
                    SELECT l.slip_id, s.employee_id, l.code,
                           COALESCE(SUM(l.amount), 0) AS amount, COALESCE(SUM(l.total), 0) AS total
                      FROM hr_payslip_line l
                      JOIN hr_payslip s ON s.id = l.slip_id
                     WHERE l.slip_id = ANY(%s) AND l.code = ANY(%s)
                  GROUP BY l.slip_id, s.employee_id, l.code
                """, (slips.ids, list(codes)))
                for row in self.env.cr.dictfetchall():
                    data[row['slip_id']][row['code']] = (row['amount'], row['total'])
                    slip_employee[row['slip_id']] = row['employee_id']

            employees = self.env['hr.employee'].browse(set(slip_employee.values()))
            sex_by_employee = {emp.id: rec._get_employee_sex(emp) for emp in employees}
            percentage_codes = {code for code in codes if Line._is_percentage_code(code)}

            vals_list = []
            for rubric in rubrics:
                emp_code, pat_code = rubric.employee_rule_code, rubric.employer_rule_code
                base_code = pat_code if pat_code in percentage_codes else (
                    emp_code if emp_code in percentage_codes else False)
                assiette = base = amount_employee = amount_employer = 0.0
                males, females = set(), set()
                for slip_id, slip_data in data.items():
                    emp_total = slip_data.get(emp_code, (0.0, 0.0))[1] if emp_code else 0.0
                    pat_total = slip_data.get(pat_code, (0.0, 0.0))[1] if pat_code else 0.0
                    if not emp_total and not pat_total:
                        continue
                    amount_employee += emp_total
                    amount_employer += pat_total
                    assiette += slip_data.get(rubric.assiette_code, (0.0, 0.0))[1]
                    if base_code:
                        base += slip_data.get(base_code, (0.0, 0.0))[0]
                    employee_id = slip_employee[slip_id]
                    if sex_by_employee.get(employee_id) == 'female':
                        females.add(employee_id)
                    else:
                        males.add(employee_id)
                vals_list.append({
                    'summary_id': rec.id,
                    'rubric_id': rubric.id,
                    'group_id': rubric.group_id.id,
                    'sequence': rubric.sequence,
                    'code': rubric.code,
                    'name': rubric.name,
                    'rate_employee': rubric.rate_employee,
                    'rate_employer': rubric.rate_employer,
                    'assiette': assiette,
                    'base': base,
                    'amount_employee': amount_employee,
                    'amount_employer': amount_employer,
                    'headcount_male': len(males),
                    'headcount_female': len(females),
                })
            Line.create(vals_list)
            rec.payslip_count = len(slips)
            rec.compute_date = fields.Datetime.now()
        return True

    # ------------------------------------------------------------------
    # Aides pour les rapports PDF / XLSX
    # ------------------------------------------------------------------
    def _get_report_groups(self):
        """Lignes regroupées par groupe avec sous-totaux, dans l'ordre d'affichage."""
        self.ensure_one()
        groups = []
        for group in self.line_ids.mapped('group_id').sorted(lambda g: (g.sequence, g.id)):
            lines = self.line_ids.filtered(lambda l, g=group: l.group_id == g).sorted(
                lambda l: (l.sequence, l.code or '', l.id))
            groups.append({
                'name': group.name,
                'lines': lines,
                'total_employee': sum(lines.mapped('amount_employee')),
                'total_employer': sum(lines.mapped('amount_employer')),
                'total_global': sum(lines.mapped('amount_total')),
            })
        return groups

    @api.model
    def _fmt_amount(self, value, blank_zero=True):
        if blank_zero and not value:
            return ''
        return f"{round(value or 0):,.0f}".replace(',', '\u00a0')

    @api.model
    def _fmt_rate(self, value):
        return f"{value or 0:.2f}"


class ContributionSummaryLine(models.Model):
    _name = 'hr_payroll_custom.contribution_summary_line'
    _description = "Ligne - état résumé des cotisations"
    _order = 'group_sequence, sequence, code, id'

    summary_id = fields.Many2one('hr_payroll_custom.contribution_summary', "État", required=True,
                                 ondelete='cascade')
    rubric_id = fields.Many2one('hr_payroll_custom.contribution_summary_rubric', "Rubrique", ondelete='set null')
    group_id = fields.Many2one('hr_payroll_custom.contribution_summary_group', "Groupe", ondelete='restrict')
    group_sequence = fields.Integer(related='group_id.sequence', store=True, string="Séquence du groupe")
    sequence = fields.Integer("Séquence")
    code = fields.Char("N°")
    name = fields.Char("Rubrique de cotisation")
    rate_employee = fields.Float("Taux salarial", digits=(5, 2))
    rate_employer = fields.Float("Taux patronal", digits=(5, 2))
    rate_total = fields.Float("Taux global", digits=(5, 2), compute='_compute_amounts', store=True)
    assiette = fields.Float("Assiette de cotisation", digits=(16, 0))
    base = fields.Float("Base", digits=(16, 0))
    amount_employee = fields.Float("Montant salarial", digits=(16, 0))
    amount_employer = fields.Float("Montant patronal", digits=(16, 0))
    amount_total = fields.Float("Montant global", digits=(16, 0), compute='_compute_amounts', store=True)
    headcount_male = fields.Integer("Effectif H")
    headcount_female = fields.Integer("Effectif F")

    @api.depends('rate_employee', 'rate_employer', 'amount_employee', 'amount_employer')
    def _compute_amounts(self):
        for line in self:
            line.rate_total = line.rate_employee + line.rate_employer
            line.amount_total = line.amount_employee + line.amount_employer

    @api.model
    def _is_percentage_code(self, code):
        return bool(self.env['hr_payroll_custom.contribution_summary_rubric']._find_percentage_rule(code))
