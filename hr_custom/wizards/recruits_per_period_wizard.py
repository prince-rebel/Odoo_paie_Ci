# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools, _
from odoo.exceptions import ValidationError
import datetime
import babel


class RecruitsPerPeriod(models.TransientModel):
    _name = 'hr_custom.recruits_per_period_wizard'
    _description = 'recrues par période'

    def _get_default_date_from(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        return '{}-01-01'.format(year)

    def _get_default_date_to(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    date_from = fields.Date(string="De", default=_get_default_date_from)
    date_to = fields.Date(string='Au', default=_get_default_date_to)


    def generate_data(self):
        res = []
        employees = self.env['hr.employee'].search([('hiring_date', '!=', False),
                                                    ('hiring_date', '>=', self.date_from),
                                                    ('hiring_date', '<=', self.date_to),
                                                    ('active', 'in', (True, False))])
        if employees:
            for emp in employees:
                contrat_empl = self.env['hr.version'].search(
                    [('employee_id', '=', emp.id), ('is_current', '=', True)])
                gender = ''
                if emp.gender == 'male':
                    gender = 'M'
                elif emp.gender == 'female':
                    gender = 'F'
                else:
                    pass
                if emp.employee_status == 'cadre':
                    employee_status = 'CADRE'
                elif emp.employee_status == 'non_cadre':
                    employee_status = 'NON CADRE'
                else:
                    employee_status = 'CADRE SUPERIEUR'

                val = {
                    'identification_id': emp.identification_id,
                    'cat': emp.salary_category_id.name or '',
                    'status': employee_status,
                    'name': str(emp.name) + ' ' + str(emp.first_name),
                    'job_id': emp.job_id.name,
                    'service_id': emp.service_id.description or '',
                    'department_id': emp.department_id.description or '',
                    'direction_id': emp.direction_id.description or '',
                    'gender': gender,
                    'age': emp.age,
                    'hiring_date': emp.hiring_date.strftime('%d/%m/%Y') if emp.hiring_date else '',
                    'birthday': emp.birthday.strftime('%d/%m/%Y') if emp.birthday else '',
                    'type_contrat': contrat_empl.contract_type_id.name or ''
                }
                res.append(val)
        else:
            raise ValidationError(_("Aucune donnée à afficher. Merci de contacter un administrateur "
                                "si vous estimez que c'est une erreur"))
        return res

    def add_hr_manager_signature(self):
        res = []
        emp = self.env['hr.employee'].search([], limit=1)
        val = {
            'manager': str(emp.company_id.hr_manager_id.first_name) + ' ' + str(emp.company_id.hr_manager_id.name)
        }
        res.append(val)
        return res

    def print_report_new_employee_xls(self):
        data = {}
        self.ensure_one()
        data['lines'] = self.generate_data()
        data['ids'] = self.id
        data['model'] = self._name
        return self.env.ref('hr_custom.action_recruits_per_period_xls').report_action(self, data=data)


    def print_report_new_employee_pdf(self):
        locale = self.env.context.get('lang') or 'en_US'
        data = {'model': self._name, 'form': self.read(), 'new_employee': self.generate_data(),
                'res': self.generate_data(), 'manager': self.add_hr_manager_signature(), 'date': tools.ustr(
                babel.dates.format_date(date=datetime.datetime.now(), format='dd MMMM y', locale=locale))}
        return self.env.ref('hr_custom.action_recruits_per_period_pdf').report_action(self, data=data)
