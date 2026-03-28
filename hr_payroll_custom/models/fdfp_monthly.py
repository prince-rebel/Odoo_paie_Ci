# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class FdfpMonthly(models.Model):
    _name = 'hr_payroll_custom.fdfp_monthly'
    _description = "Cotisation FDFP Mensuelle"

    name = fields.Char('Nom')
    date_from = fields.Date('Date de début')
    date_to = fields.Date('Date de fin')
    company_id = fields.Many2one('res.company', 'Compagnie', default=lambda self: self.env.user.company_id.id)
    line_ids = fields.One2many('hr_payroll_custom.fdfp_monthly_line', 'fdfp_monthly_id', "lignes")
    headcount_by_category_ids = fields.One2many("hr_payroll_custom.headcount_by_category", 'fdfp_monthly_id', 'Effectif par catégorie')
    salaries_number = fields.Integer("Effectif des salariés")
    amount_total_contributed = fields.Float("Montant total à payer", default=0.0, digits=(12, 0))
    executive_number = fields.Integer('Cadre', default=0)
    agent_control_number = fields.Integer('Maitrise', default=0)
    employee_number = fields.Integer('Employés', default=0)
    worker_number = fields.Integer('Ouvrier', default=0)
    cumulative_amount_fpc = fields.Float('Cumul à ce jour (FPC', default=0.0)

    def get_cumul_by_code(self, code, date_from, date_to, company_id):
        payslips = self.env['hr.payslip'].search([('date_from', '>=', date_from), ('date_to', '<=', date_to),
                                                  ('company_id', '=', company_id),
                                                  ('state', 'in', ('validated', 'paid'))])

        if payslips:
            self.env.cr.execute("SELECT sum(total) as cumul FROM hr_payslip_line WHERE slip_id=ANY(%s) AND "
                                "code = %s", (payslips.ids, code))
            results = self.env.cr.dictfetchone()
            if results:
                return results['cumul']
            else:
                return False
        else:
            return False

    def compute(self):
        for rec in self:
            rec.line_ids.unlink()
            slip_obj = rec.env['hr.payslip']
            all_slips = slip_obj.search([('date_from', '>=', rec.date_from), ('date_to', '<=', rec.date_to),
                                         ('company_id', '=', rec.company_id.id),
                                         ('state', 'in', ('validated', 'paid'))])
            lines = []
            amount = 0
            salaries_number = 0
            if all_slips:

                fdfp_config = rec.env['hr_payroll_custom.fdfp_settings'].search([])
                if fdfp_config:
                    for fdfp in fdfp_config:
                        self.env.cr.execute(
                            "SELECT salary_rule_id as salary_rule,sum(amount) as amount, sum(total) as total"
                            " FROM hr_payslip_line WHERE salary_rule_id = %s AND slip_id=ANY(%s) GROUP BY "
                            "salary_rule_id", (fdfp.rule_id.id, all_slips.ids,))
                        results = self.env.cr.dictfetchone()
                        if results:
                            vals = {
                                'rule_id': fdfp.rule_id.id,
                                'rate': fdfp.rate,
                                'gross_salary': results['amount'],
                                'monthly_amount': results['total'],
                                'fdfp_monthly_id': rec.id
                            }
                            amount += vals['monthly_amount']
                            lines.append(vals)
                        self.env.cr.execute("SELECT count(*) as salaries_number FROM hr_payslip_line WHERE salary_rule_id "
                                            "= %s AND slip_id=ANY(%s)", (fdfp.rule_id.id, all_slips.ids,))
                        results = self.env.cr.dictfetchone()
                        salaries_number = results['salaries_number']
            rec.salaries_number = salaries_number
            employees_cat = rec.env['hr_custom.employee_category'].search([])
            headcount_cat = []
            id_employee = []
            if all_slips:
                for slip in all_slips:
                    if slip.employee_id and slip.employee_id.type != 'p':
                        id_employee.append(slip.employee_id.id)
                    else:
                        pass

            if employees_cat and id_employee:
                for cat in employees_cat:
                    rec.env.cr.execute("SELECT COUNT(DISTINCT(id)) as effective FROM hr_employee WHERE id=ANY(%s) AND "
                                        "employee_category_id = %s", (id_employee, cat.id))
                    result = rec.env.cr.dictfetchone()
                    if result:
                        headcount_vals = {
                            'name': cat.name,
                            'employee_category_id': cat.id,
                            'effective': int(result['effective']),
                            'fdfp_monthly_id': rec.id
                        }
                        headcount_cat.append(headcount_vals)
            rec.line_ids.create(lines)
            rec.amount_total_contributed = amount
            rec.headcount_by_category_ids.unlink()
            rec.headcount_by_category_ids.create(headcount_cat)
            rec.get_headcount_by_category()
            code = 'TAXEFP'
            date_from = str(rec.date_from.year) + '-01-01'
            date_to = rec.date_to
            rec.cumulative_amount_fpc = rec.get_cumul_by_code(code, date_from, date_to, rec.company_id.id)

    def get_headcount_by_category(self):
        if self.headcount_by_category_ids:
            self.executive_number = 0
            self.agent_control_number = 0
            self.employee_number = 0
            self.worker_number = 0
            for line in self.headcount_by_category_ids:
                if line.employee_category_id.code == 'CS' or line.employee_category_id.code == 'CA':
                    self.executive_number += line.effective
                if line.employee_category_id.code == 'AM':
                    self.agent_control_number = line.effective
                if line.employee_category_id.code == 'EM':
                    self.employee_number = line.effective
                if line.employee_category_id.code == 'OU':
                    self.worker_number = line.effective


class FdfpMonthlyLine(models.Model):
    _name = 'hr_payroll_custom.fdfp_monthly_line'
    _description = "Ligne cotisation FDFP mensuelle"

    rule_id = fields.Many2one('hr.salary.rule', "Règle salariale")
    gross_salary = fields.Float("Salaire brut", digits=(12, 0)) #brut_total
    rate = fields.Float("Taux", digits=(12, 2)) #taux
    monthly_amount = fields.Float("Montant mensuel", digits=(12, 0)) #amount_contributed
    fdfp_monthly_id = fields.Many2one("hr_payroll_custom.fdfp_monthly", "Déclaration FDFP", required=False) #fdfp_id


class hrFDFPHeadcountByCategory(models.Model):
    _name = 'hr_payroll_custom.headcount_by_category'
    _description = "Effectif par categorie"

    name = fields.Char("Categorie")
    employee_category_id = fields.Many2one('hr_custom.employee_category', "Catégorie employé")
    effective = fields.Integer("Effectif")
    fdfp_monthly_id = fields.Many2one("hr_payroll_custom.fdfp_monthly", "FDFP")
