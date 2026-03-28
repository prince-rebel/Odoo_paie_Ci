# -*- coding:utf-8 -*-

from odoo import fields, models, api, _, tools
from odoo.exceptions import ValidationError


class PayrollByPost(models.TransientModel):
    _name = 'hr_payroll_custom.payroll_by_post'
    _description = "Etat des rubriques de paie par poste et periode"

    date_from = fields.Date('Date de début')
    date_to = fields.Date('Date de fin')
    rule_id = fields.Many2one('hr.salary.rule', 'Règle', domain="[('appears_on_payroll','=',True)]")
    company_id = fields.Many2one('res.company', 'Compagnie', default=lambda self: self.env.user.company_id.id)

    def compute_cumulative_amount(self):
        for rec in self:
            code = rec.rule_id.code
            date_from = rec.date_from
            date_to = rec.date_to
            if not (code and date_to and date_to):
                raise ValidationError(_("Vous devez définir les différentes dates et la société pour générer le rapport."))
            employees = self.env['hr.employee'].search([('active', 'in', (True, False))])
            payslip = self.env['hr.payslip']
            res = []
            if not rec.rule_id.imputation_type:
                raise ValidationError(_("Cette règle n'est pas considérée comme un gain ou une retenue. Merci de le spécifier "
                                "dans les paramètres des règles salariales."))
            verif = []
            verif_count = 0
            for employee in employees:
                number_payslips = self.env['hr.payslip'].search_count([('date_from', '>=', date_from),
                                                                       ('date_to', '<=', date_to),
                                                                       ('employee_id', '=', employee.id)])
                if number_payslips >= 1:
                    rate = number_payslips
                else:
                    continue
                cumulative_rule_amount = payslip.getCumulDataByCode(employee.id, code, date_from, date_to, 'amount')
                if cumulative_rule_amount != 0:
                    cumulative_rule_total_amount = payslip.getCumulDataByCode(employee.id, code, date_from, date_to, 'total')
                    if cumulative_rule_total_amount != 0:
                        verif_count += 1
                        vals = {
                            'id_employee': employee.identification_id,
                            'amount': cumulative_rule_total_amount
                        }
                        verif.append(vals)
                    else:
                        continue
                    cumulative_rule_quantity = payslip.getCumulDataByCode(employee.id, code, date_from, date_to, 'quantity')
                    cumulative_rule_rate = payslip.getCumulDataByCode(employee.id, code, date_from, date_to, 'rate')
                    vals = {
                        'matricule': employee.identification_id,
                        'full_name': employee.name + ' ' + employee.first_name if employee.first_name else employee.name,
                        'base': cumulative_rule_amount,
                        'quantity': cumulative_rule_quantity,
                        'taux': cumulative_rule_rate / rate,
                        'amount': cumulative_rule_total_amount,
                        'imputation_type': rec.rule_id.imputation_type
                    }
                    res.append(vals)
                else:
                    continue
            return res

    def get_period_print_report(self):
        for rec in self:
            detail = []
            vals = {
                'date_from': rec.date_from.strftime('%d/%m/%Y'),
                'date_to': rec.date_to.strftime('%d/%m/%Y'),
                'rubrique': rec.rule_id.sequence,
                'rule_id': rec.rule_id.name,
            }
            detail.append(vals)
            return detail

    def print_report_pdf(self):
        for rec in self:
            data = {
                'model': rec._name,
                'form': rec.read(),
                'res': rec.compute_cumulative_amount(),
                'details_report': rec.get_period_print_report(),
            }
            return self.env.ref('hr_payroll_custom.action_payroll_by_post_pdf').report_action(rec, data=data)

    def print_report_xls(self):
        for rec in self:
            data = {
                'model': rec._name,
                'form': rec.read(),
                'res': rec.compute_cumulative_amount(),
                'details_report': rec.get_period_print_report()
            }
            return self.env.ref('hr_payroll_custom.action_payroll_by_post_xls').report_action(rec, data=data)
