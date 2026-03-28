# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, tools
from odoo.exceptions import ValidationError
import babel
import logging

_logger = logging.getLogger(__name__)


class PayBook(models.TransientModel):
    _name = 'hr_payroll_custom.pay_book'
    _description = 'Assistant des livres de paye'

    @api.onchange('date_from', 'company_id')
    def onchange_company(self):
        for rec in self:
            rec.name = "LIVRE DE PAIE "
            locale = rec.env.context.get('lang') or 'en_US'
            if rec.date_from and rec.company_id:
                rec.name = str(
                    f"Livre de paie {rec.company_id.name} de "
                    f"{tools.ustr(babel.dates.format_date(date=rec.date_from, format='MMMM-y', locale=locale))}").upper()

    name = fields.Char('Libellé')
    date_from = fields.Date('Date de début')
    date_to = fields.Date('Date de fin')
    company_id = fields.Many2one('res.company', 'Compagnie', default=lambda self: self.env.user.company_id.id)

    def get_payslip_line_data(self, id_employee, code, date_from, date_to, id_company):
        """
            Function that returns the total of an employee's position according to the given period
        Args:
            id_company: company ID
            code: pay section code
            id_employee: employee ID
            date_from: date start
            date_to: date end

        Returns: Total of payroll section

        """
        _req_payslip_line = f" SELECT SUM(total) FROM hr_payslip_line pl INNER JOIN hr_payslip p ON p.id = pl.slip_id " \
                            f"WHERE pl.employee_id = {id_employee} AND pl.code = '{code}' AND pl.date_from >= " \
                            f"'{date_from}' AND pl.date_to <= '{date_to}' AND p.company_id = {id_company}"
        self.env.cr.execute(_req_payslip_line)
        payslip_line = self.env.cr.dictfetchall()
        return payslip_line[0]['sum'] if payslip_line[0]['sum'] else 0

    def get_cumul_payslip_line_data(self, code, date_from, date_to, id_company):
        """
            Function that returns the accumulation of an employee position according to the given period
        Args:
            code: pay section code
            date_from: date start
            date_to: date end
            id_company: company ID

        Returns: cumulative amount of the payroll section

        """

        _req_cumul_payslip_line = f" SELECT SUM(total) FROM hr_payslip_line pl INNER JOIN hr_payslip p ON p.id = pl.slip_id" \
                                  f" WHERE pl.code = '{code}' AND pl.date_from >= '{date_from}' AND pl.date_to <= '{date_to}' " \
                                  f"AND p.company_id = {id_company}"
        self.env.cr.execute(_req_cumul_payslip_line)
        cumul_payslip_line = self.env.cr.dictfetchall()
        return cumul_payslip_line[0]['sum'] if cumul_payslip_line[0]['sum'] else 0

    def generate_payroll_data(self):
        for rec in self:
            res = []
            date_from = rec.date_from
            date_to = rec.date_to
            id_company = rec.company_id.id
            if not (date_from and date_to and id_company):
                raise ValidationError(_("Vous devez definir les différentes dates et la société pour générer le rapport"))

            # 1- récuperer les employés qui ont un bulletin dans la période définie
            _req_ids_employee = f"SELECT id, employee_id FROM hr_payslip where date_from = '{date_from}' AND " \
                                f"date_to = '{date_to}' AND company_id = {id_company};"
            self.env.cr.execute(_req_ids_employee)
            ids_employee = self.env.cr.dictfetchall()
            if not ids_employee:
                raise ValidationError(_("Aucune donnée à afficher. Il n'y a pas de bulletin de ce type et cette "
                                        "société pour cette période. Merci de faire les corrections nécessaires"))

            ids_emp = [x['employee_id'] for x in ids_employee]
            # 2- Récupérér toutes les rubriques qui doivent apparaître dans le livre de paie
            _req_salary_rules = f"SELECT code, name FROM hr_salary_rule WHERE appears_on_payroll IS True " \
                                f" ORDER BY sequence;"
            self.env.cr.execute(_req_salary_rules)
            salary_rules_rec = self.env.cr.dictfetchall()
            if not salary_rules_rec:
                raise ValidationError(_("Aucune donnée à afficher. Il n'y a pas de rubriques à afficher. Allez dans la "
                                        "configuration => Règle salariale et choisir les rubriques qui doivent apparraître "
                                        "dans le livre de paye via la case à cocher 'Apparaît sur le Livre de paie'"))
            header = ['Matricule', 'NOM ET PRENOMS']
            totals = []
            for sr in salary_rules_rec:
                header.append(sr['name']['en_US'])
                totals.append(self.get_cumul_payslip_line_data(sr['code'], date_from, date_to, id_company))

            # 2- pour chaque employé récupérer les valeurs pour chacunes des rubriques
            ids_tuple = tuple(ids_emp) if len(ids_emp) > 1 else f"({ids_emp[0]})"
            _req_employee = f"SELECT id, registration_number, name, first_name FROM hr_employee WHERE id IN {ids_tuple} " \
                            f"ORDER BY registration_number"
            self.env.cr.execute(_req_employee)
            employee_rec = self.env.cr.dictfetchall()
            cpt = 1
            for emp in employee_rec:
                res_line = []
                for sr in salary_rules_rec:
                    res_line.append(self.get_payslip_line_data(emp['id'], sr['code'], date_from, date_to, id_company))
                vals_line = {
                    'matricule': emp['registration_number'],
                    'name': emp['name'] + ' ' + emp['first_name'],
                    'data': res_line
                }

                res.append(vals_line)
                cpt += 1

            return header, res, totals

    def _print_report(self, data):
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise ValidationError(_("You must define a Start Date"))
        return self.env.ref('hr_payroll_ci_raport.report_hr_payroll').with_context(landscape=True).report_action(self,
                                                                                                                 data=data)

    def export_xls(self):
        for rec in self:
            data = {}
            data['title'] = rec.name or 'LIVRE DE PAYE'
            data['header'], data['lines'], data['totals'] = self.generate_payroll_data()
            return self.env.ref('hr_payroll_custom.action_pay_book_xls').report_action(self, data=data, config=False)
