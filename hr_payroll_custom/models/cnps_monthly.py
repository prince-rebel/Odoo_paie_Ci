# -*- coding:utf-8 -*-

from odoo import api, fields, _, models
from . import cnps_settings
from itertools import groupby
import logging

_logger = logging.getLogger(__name__)


class CnpsMonthly(models.Model):
    _name = "hr_payroll_custom.cnps_monthly"
    _description = "CNPS Mensuel"

    @api.depends("line_ids", "cotisation_ids", "cnps_monthly_line_ids")
    def _get_total(self):
        for rec in self:
            if rec.line_ids:
                total_employee = sum([line.number_of_employees for line in rec.line_ids])
                total_cnps_base = sum([line.retirement_plan for line in rec.line_ids])
                total_other_base = sum([line.other_plan for line in rec.line_ids])
                rec.total_employee = total_employee
                rec.total_cnps_base = total_cnps_base
                rec.total_other_base = total_other_base
            if rec.cotisation_ids:
                total = sum([x.amount_contributed for x in rec.cotisation_ids])
                rec.total_amount_of_contributions = total
            if rec.cnps_monthly_line_ids:
                total_brut = sum([x.gross_salary for x in rec.cnps_monthly_line_ids])
                rec.total_gross_salary = total_brut

    name = fields.Char("Libellé")
    date_from = fields.Date("Date de début")
    date_to = fields.Date("Date de fin")
    slip_ids = fields.Many2many("hr.payslip", 'slip_id', "Bulletins_de_paie")
    slips_count = fields.Integer(compute='_compute_slips_count', string='Nombre de bulletins de paie', store=True)
    company_id = fields.Many2one('res.company', "Société", default=lambda self: self.env.user.company_id.id)
    total_employee = fields.Integer("Nombre total d'employés", compute='_get_total', store=True)
    total_cnps_base = fields.Float("Total assiette CNPS", compute='_get_total', store=True, digits=(12, 0)) #total_assiette_cnps
    total_other_base = fields.Float('Autre total assiette', compute='_get_total', store=True, digits=(12, 0)) #total_assiette_other
    total_amount_of_contributions = fields.Float('Montant total cotisation', compute='_get_total', store=True,
                                                digits=(12, 0)) #total_cotisation_contributed
    total_gross_salary = fields.Float("Total salaires bruts payes", digits=(12, 0), compute='_get_total', store=True) #total_salaire_brut
    line_ids = fields.One2many('hr_payroll_custom.cnps_monthly_category_line', 'cnps_monthly_id', 'Lignes')
    cnps_monthly_line_ids = fields.One2many('hr_payroll_custom.cnps_monthly_line', 'cnps_monthly_id', "Les elements") #other_line_ids
    cotisation_ids = fields.One2many("hr_payroll_custom.cnps_monthly_cotisation_line", "cnps_monthly_id", "Decomptes de cotisations")
    # type_employee = fields.Selection([('h', 'Horaire'), ('j', 'Journalier'), ('m', 'Mensuel'),
    #                                  ('all', 'Tous les employés')], "Livre de paie pour ", default="all")
    @api.onchange('slip_ids')
    def _compute_slips_count(self):
        self.slips_count = len(self.slip_ids)

    def compute(self):
        for rec in self:
            rec.line_ids.unlink()
            rec.cnps_monthly_line_ids.unlink()
            rec.cotisation_ids.unlink()
            res = []
            slip_obj = rec.env['hr.payslip']
            all_slips = slip_obj.search([('date_from', '>=', rec.date_from), ('date_to', '<=', rec.date_to),
                                         ('company_id', '=', rec.company_id.id),
                                         ('state', 'in', ('validated', 'paid'))])
            # if rec.type_employee != 'all':
            #     all_slips = all_slips.filtered(lambda slip: slip.type == rec.type_employee)
            lines = []
            cotisations = []
            type_cnps = rec.env['hr_payroll_custom.cnps_slice'].search([])
            if all_slips:
                rec.env.cr.execute("SELECT distinct(employee_id) FROM hr_payslip WHERE id=ANY(%s)", (all_slips.ids,))
                results = rec.env.cr.fetchall()
                if results:
                    employee_ids = [x[0] for x in results]
                    rec.env.cr.execute(""
                                        "SELECT distinct(employee_id) as employee_id, sum(gross_taxable) as "
                                        "brut_imposable,AVG(base_daily) as base_jour FROM hr_payslip "
                                        "WHERE id=ANY(%s) AND  employee_id=ANY(%s) GROUP BY"
                                        " employee_id", (all_slips.ids, employee_ids))
                    data = rec.env.cr.dictfetchall()
                    if data:
                        for tcnps in type_cnps:
                            l_vals = {
                                'name': tcnps.name,
                                'number_of_employees': 0,
                                'retirement_plan': 0,
                                'other_plan': 0,
                                'cnps_monthly_id': rec.id
                            }
                            for dt in data:
                                found = False
                                employee = rec.env['hr.employee'].browse(dt['employee_id'])
                                if employee:
                                    if tcnps.type != 'm':
                                        if employee.type == tcnps.type:
                                            if tcnps.amount_min < dt['base_jour'] <= tcnps.amount_max:
                                                found = True
                                    else:
                                        if employee.type == tcnps.type:
                                            if tcnps.amount_min < dt['brut_imposable'] <= tcnps.amount_max:
                                                found = True
                                if found:
                                    l_vals['number_of_employees'] += 1
                                    val = {
                                        'employee_id': employee.id,
                                        'type': employee.type,
                                        'gross_salary': dt['brut_imposable'],
                                        'daily_base': dt['base_jour'],
                                        'cnps_slice_id': tcnps.id,
                                        'date_start': rec.date_from,
                                        'date_end': rec.date_to,
                                        'cnps_monthly_id': rec.id
                                    }
                                    if dt['brut_imposable'] < rec.company_id.max_cnps_tax_base:
                                        val['cnps_tax_base'] = dt['brut_imposable']
                                    else:
                                        val['cnps_tax_base'] = rec.company_id.max_cnps_tax_base
                                    l_vals['retirement_plan'] += val['cnps_tax_base']
                                    if dt['brut_imposable'] < rec.company_id.max_other_tax_base:
                                        val['other_tax_base'] = dt['brut_imposable']
                                    else:
                                        val['other_tax_base'] = rec.company_id.max_other_tax_base

                                    val['maternity_insurance_amount'] = round(val['other_tax_base'] * rec.company_id. \
                                        maternity_insurance_rate / 100)
                                    val['family_benefit_amount'] = round(val['other_tax_base'] * rec.company_id. \
                                        family_benefit_rate / 100)
                                    val['work_accident_amount'] = round(val['other_tax_base'] * rec.company_id. \
                                        work_accident_rate / 100)
                                    if employee.nature_employe == 'local':
                                        val['cnps_amount'] = round(val['cnps_tax_base'] * \
                                                                   rec.company_id.local_employee_cnps_rate / 100)
                                    else:
                                        val['cnps_amount'] = round(val['cnps_tax_base'] * \
                                                                   rec.company_id.expatriate_employee_cnps_rate / 100)
                                    val['cnps_amount'] += round(val['cnps_tax_base'] * \
                                                                rec.company_id.employer_cnps_rate / 100)
                                    l_vals['other_plan'] += val['other_tax_base']
                                    res.append(val)
                            lines.append(l_vals)
                if lines:
                    rec.line_ids.create(lines)
                    rec.cnps_monthly_line_ids.create(res)
                    templates = rec.env['hr_payroll_custom.cnps_cotisation_template'].search([('company_id', '=', rec.company_id.id)])
                    if templates:
                        for tpl in templates:
                            tpl_val = {
                                'name': tpl.name,
                                'rate': tpl.rate,
                                'cnps_monthly_id': rec.id
                            }
                            if tpl.type == 'cnps':
                                tpl_val['amount_submitted'] = rec.total_cnps_base
                                _req_amount_contributed = "SELECT sum(total) FROM hr_payslip_line WHERE employee_id=" \
                                                         "ANY(%(employee)s) and slip_id=ANY(%(slip)s) and " \
                                                         "(code='CNPS' or code='CNPS_P')"
                                _params = {
                                    'employee':employee_ids,
                                    'slip': all_slips.ids
                                }

                                rec.env.cr.execute(_req_amount_contributed, _params)
                                amount_contributed = rec.env.cr.fetchall()
                                tpl_val['amount_contributed'] = amount_contributed[0][0]

                            else:
                                tpl_val['amount_submitted'] = rec.total_other_base
                                tpl_val['amount_contributed'] = round(tpl_val['amount_submitted'] * tpl.rate / 100)
                            cotisations.append(tpl_val)
                        rec.cotisation_ids.create(cotisations)

        return True

    def export_xls(self):
        for rec in self:
            context = self._context
            rec.ensure_one()
            data = {}
            data['ids'] = rec.id
            data['model'] = rec._name
            return self.env.ref('hr_payroll_custom.action_list_contributors_xls').report_action(self, data=data)


class CnpsMonthlyLine(models.Model):
    _name = 'hr_payroll_custom.cnps_monthly_line'
    _description = "Ligne CNPS mensuel"
    _order = "employee_id"

    name = fields.Char('Matricule', related="employee_id.registration_number", store=True)
    employee_id = fields.Many2one('hr.employee', 'Employé')
    type = fields.Selection(cnps_settings.Type_employee, 'Type', default=False)
    cnps_slice_id = fields.Many2one('hr_payroll_custom.cnps_slice', 'Tranche') #tranche_id
    gross_salary = fields.Float("Salaire brut", digits=(12, 0)) #amount_brut
    cnps_tax_base = fields.Float("Assiette CNPS", digits=(12, 0)) #assiette_cnps
    other_tax_base = fields.Float("Assiette pour autres prélèvements", digits=(12, 0)) #assiette_other
    daily_base = fields.Float("Base journalière", digits=(12, 0)) #daily_basis
    cnps_amount = fields.Float("Montant CNPS", digits=(12, 0))
    maternity_insurance_amount = fields.Float("Montant Assurance maternité", digits=(12, 0)) #assurance_maternite_amount
    family_benefit_amount = fields.Float("Montant Prestation familiale", digits=(12, 0)) #prestation_family_amount
    work_accident_amount = fields.Float("Montant Accident de travail", digits=(12, 0)) #accident_travail_amount
    cnps_monthly_id = fields.Many2one("hr_payroll_custom.cnps_monthly", "CPNS mensuel")
    date_start = fields.Date("Date de début")
    date_end = fields.Date("Date de fin") #date_to


class CnpsMonthlyCategoryLine(models.Model):
    _name = "hr_payroll_custom.cnps_monthly_category_line"
    _description = "Ligne catégorie CNPS mensuel"

    name = fields.Char("Designation")
    number_of_employees = fields.Integer("Nombre de salaries") #salaries_number
    retirement_plan = fields.Float("Regime de retraite", digits=(12, 0)) #regime_retraite
    other_plan = fields.Float("Autre regime", digits=(12, 0)) #regime_autre
    cnps_monthly_id = fields.Many2one("hr_payroll_custom.cnps_monthly", "CNPS Mensuel")


class CnpsCotisationLine(models.Model):
    _name = "hr_payroll_custom.cnps_monthly_cotisation_line"
    _description = "ligne cotisation CNPS mensuel"

    name = fields.Char("Designation")
    amount_submitted = fields.Float("salaires soumis à cotisation", digits=(12, 0))
    rate = fields.Float("Taux") #taux
    amount_contributed = fields.Float("Montant", digits=(12, 0))
    cnps_monthly_id = fields.Many2one("hr_payroll_custom.cnps_monthly", "CNPS Mensuel")
