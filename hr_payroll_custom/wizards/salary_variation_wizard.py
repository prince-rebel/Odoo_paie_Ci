# -*- coding:utf-8 -*-

from odoo import api, fields, _, models
from odoo.exceptions import ValidationError
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class SalaryVariation(models.TransientModel):
    _name = 'hr_payroll_custom.salary_variation'
    _description = "Variation des salaires"

    date_from = fields.Date(string='Début (encours)')
    date_to = fields.Date(string='Fin (encours)')
    old_date_from = fields.Date(string='Début (passé)', compute='getOldPeriodes', store=True)
    old_date_to = fields.Date(string='Fin (passé)', compute='getOldPeriodes', store=True)
    rule_ids = fields.Many2many('hr.salary.rule', string="Règle salariale", domain="[('appears_on_payroll','=',True)]")
    company_id = fields.Many2one("res.company", "Société", default=lambda self: self.env.user.company_id.id)

    @api.depends('date_from')
    def getOldPeriodes(self):
        for rec in self:
            if rec.date_from:
                date_from = str(fields.Date.from_string(rec.date_from) + relativedelta(day=1, months=-1))
                date_to = str(fields.Date.from_string(rec.date_from) + relativedelta(days=-1))
                rec.old_date_from = date_from
                rec.old_date_to = date_to

    def getCodes(self):
        if self.rule_ids:
            _query = "SELECT code, name FROM hr_salary_rule where id IN %(id_rules)s ORDER BY sequence"
            _params = {
                'id_rules': tuple(self.rule_ids.ids),
            }
            self.env.cr.execute(_query, _params)
        else:
            self.env.cr.execute("SELECT code, name FROM hr_salary_rule where appears_on_payroll is True ORDER BY "
                                "sequence")

        codes = {x[0]: x[1] for x in self.env.cr.fetchall()}
        return codes

    def getpayslipLinesForPeriode(self, id_employee, code, date_from, date_to):
        select_query = """
            SELECT code, sum(total) as amount FROM hr_payslip_line pl
            INNER JOIN hr_payslip p ON p.id = pl.slip_id
            WHERE pl.date_from >= %(date_from)s AND pl.date_to <= %(date_to)s
            AND pl.code = %(code)s AND pl.employee_id = %(id_employee)s
            AND p.company_id = %(company_id)s
            GROUP BY code
        """

        params_query = {
            'date_from': date_from,
            'date_to': date_to,
            'company_id': self.company_id.id,
            'code': code,
            'id_employee': id_employee
        }
        self.env.cr.execute(select_query, params_query)
        lines = self.env.cr.dictfetchall()
        return lines

    def getVariationByRule(self, codes):
        res = []

        select_query = """
                SELECT  SUM(line.total)
                FROM hr_payslip_line AS line
                INNER JOIN hr_payslip p ON p.id = line.slip_id
                WHERE line.date_from >= %(date_from)s AND line.date_to <= %(date_to)s AND p.company_id = %(company_id)s
                 AND line.code = %(code)s                
                """

        for code in codes:
            rule = self.env['hr.salary.rule'].search([('code', '=', code)], limit=1)
            if rule:
                params_query = {
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'code': code,
                    'company_id': self.company_id.id
                }

                params_query_2 = {
                    'date_from': self.old_date_from,
                    'date_to': self.old_date_to,
                    'code': code,
                    'company_id': self.company_id.id
                }

                self.env.cr.execute(select_query, params_query)
                new_amount = self.env.cr.dictfetchall()
                if not new_amount[0]['sum']:
                    new_amount = 0
                else:
                    new_amount = new_amount[0]['sum']

                self.env.cr.execute(select_query, params_query_2)
                old_amount = self.env.cr.dictfetchall()
                if not old_amount[0]['sum']:
                    old_amount = 0
                else:
                    old_amount = old_amount[0]['sum']
                ecart = new_amount - old_amount

                val = {
                    'code': rule.code,
                    'name': rule.name,
                    'old_amount': old_amount,
                    'new_amount': new_amount,
                    'ecart': ecart
                }
                res.append(val)
            else:
                raise ValidationError(_("Aucune règle n'a été configuré pour l'édition de ce rapport. Merci de vous adresser "
                                "à votre administrateur"))
        return res

    def compute_data(self, codes):
        res = []
        select_query = """
                SELECT DISTINCT employee_id FROM hr_payslip 
                WHERE date_from >= %(old_date_from)s AND date_to <= %(date_to)s                
                AND company_id = %(company_id)s
                """

        params_query = {
            'old_date_from': self.old_date_from,
            'date_to': self.date_to,
            'company_id': self.company_id.id
        }
        self.env.cr.execute(select_query, params_query)
        payslip_rec = self.env.cr.dictfetchall()
        if payslip_rec:
            payslip_id = []
            for rec in payslip_rec:
                payslip_id.append(rec['employee_id'])
            employees = self.env['hr.employee'].search(
                ['|', '&', ('id', 'in', payslip_id), ('active', '=', True), ('active', '=', False)],
                order='identification_id')
        else:
            raise ValidationError(_("Vous n'avez pas de bulletin de salaire pour cette période. la génération du rapport "
                            "n'est donc pas possible. Merci de choisir une autre période"))
        if employees:
            for employee in employees:
                data = []
                for code in codes:
                    last_payslips_line = self.getpayslipLinesForPeriode(employee.id, code, self.old_date_from,
                                                                        self.old_date_to)
                    inprogress_payslips_line = self.getpayslipLinesForPeriode(employee.id, code, self.date_from,
                                                                              self.date_to)
                    vals_data = {
                        'code': code,
                        'last_month': last_payslips_line[0]['amount'] if last_payslips_line else 0,
                        'current_month': inprogress_payslips_line[0]['amount'] if inprogress_payslips_line else 0,
                        'comment': ''
                    }

                    if code == 'NET':
                        # fonction qui recevra en entrée l'id de l'employee et les dates
                        # et enverra en sortie, les rubriques dont la valeur a changé sur les 2 mois
                        vals_data['comment'] = self.get_rules_changed(employee.id, self.date_from, self.date_to,
                                                                      self.old_date_from, self.old_date_to)

                    data.append(vals_data)
                vals = {
                    'identification_id': employee.identification_id,
                    'name': employee.name,
                    'first_name': employee.first_name,
                    'data': data
                }
                res.append(vals)
        return res

    def get_rules_changed(self, id_employee, date_from, date_to, old_date_from, old_date_to):
        """
        Function allowing to know the headings which have varied over a given period

        """
        # récupérer les bulletins de chaque période
        # ressotir de chaque bulletin, les inputs
        # comparer le montant de chacun des inputs
        # si montant différent, alors mettre la règle dans le lot des changements
        # si montant identique, passer au suivant
        # Si la rubrique n'existe dans l'autre bulletin, alors mettre égelement la règle de le lot des changements
        res = []
        last_slip = self.env['hr.payslip'].search([('date_from', '>=', old_date_from), ('date_to', '<=', old_date_to),
                                                   ('employee_id', '=', id_employee),
                                                   ('company_id', '=', self.company_id.id)], limit=1)

        current_slip = self.env['hr.payslip'].search([('date_from', '>=', date_from), ('date_to', '<=', date_to),
                                                      ('employee_id', '=', id_employee),
                                                      ('company_id', '=', self.company_id.id)], limit=1)
        if not last_slip and not current_slip:
            return []
        current_inputs = []
        last_inputs = []
        if last_slip:
            for line in last_slip.input_line_ids:
                vals = {
                    'code': line.code,
                    'label': line.input_type_id.name,
                    'amount': line.amount
                }
                last_inputs.append(vals)

        if current_slip:

            for line in current_slip.input_line_ids:
                vals = {
                    'code': line.code,
                    'label': line.input_type_id.name,
                    'amount': line.amount
                }
                current_inputs.append(vals)

        if current_inputs:
            if last_inputs:
                # récupérer les 2 listes
                # fusionner les listes et ressortir une liste unique sans doublon
                # parcourir cette liste unique et faire la comparaison sur les montants
                for cr_input in current_inputs:
                    for lt_input in last_inputs:
                        if cr_input['code'] == lt_input['code']:
                            if cr_input['amount'] != lt_input['amount']:
                                vals = {
                                    'label': cr_input['label']
                                }
                                res.append(vals)
                            else:
                                pass
                        else:
                            continue

                for lt_input in last_inputs:
                    if lt_input['code'] not in [cr_input.get('code') for cr_input in current_inputs]:
                        vals = {
                            'label': lt_input['label']
                        }
                        res.append(vals)

                for cr_input in current_inputs:
                    if cr_input['code'] not in [lt_input.get('code') for lt_input in last_inputs]:
                        vals = {
                            'label': cr_input['label']
                        }
                        res.append(vals)
            else:
                res = current_inputs
        else:
            if current_inputs:
                res = current_inputs
            else:
                pass
        result = []
        if res:
            res_string = ''
            for res_line in res:
                res_string += res_line['label'] + ', '
            result.append(res_string)
        return result

    def get_date_header(self):
        for rec in self:
            form_read = rec.read()[0]
            date_from = form_read.get('date_from').strftime('%d/%m/%Y')
            date_to = form_read.get('date_to').strftime('%d/%m/%Y')
            old_date_from = form_read.get('old_date_from').strftime('%d/%m/%Y')
            old_date_to = form_read.get('old_date_to').strftime('%d/%m/%Y')
            date_header = [date_from, date_to, old_date_from, old_date_to]
            return date_header
    def export_to_excel(self):
        for rec in self:
            if not( rec.date_from and rec.date_to and rec.company_id):
                raise ValidationError(_("Vous devez définir les différentes dates ainsi que la société avant de générer le rapport."))

            codes = rec.getCodes()

            data = {
                'model': rec._name,
                'date_header': rec.get_date_header(),
                'codes': codes,
                'elements': rec.compute_data(codes)
            }

            return self.env.ref('hr_payroll_custom.action_salary_variation_employee_xls').report_action(self, data=data,
                                                                                                   config=False)

    def export_recap_to_excel(self):
        for rec in self:
            if not( rec.date_from and rec.date_to and rec.company_id):
                raise ValidationError(_("Vous devez définir les différentes dates ainsi que la société avant de générer le rapport."))
            data = {
                'model': rec._name,
                'date_header': rec.get_date_header(),
                'elements': rec.getVariationByRule(rec.getCodes())
            }

            return self.env.ref('hr_payroll_custom.action_salary_variation_rule_xls').report_action(self, data=data,
                                                                                                          config=False)
