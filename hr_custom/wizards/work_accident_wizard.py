# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
import babel
import datetime


class WorkAccidentWizard(models.Model):
    _name = 'hr_custom.work_accident_wizard'
    _description = "Assistant des accidents de travail"

    def _get_default_date_from(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        return '{}-01-01'.format(year)

    def _get_default_date_to(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    date_to = fields.Date(string='Au', default=_get_default_date_to)
    date_from = fields.Date(string="De", default=_get_default_date_from)

    def generate_data(self):
        res = []
        accidents = self.env['hr_custom.work_accident'].search([('accident_date', '>=', self.date_from),
                                                             ('accident_date', '<', self.date_to),
                                                             ('employee_id', '!=', None),
                                                             ('employee_id.active', 'in', (True,False))])
        if accidents:
            for acc in accidents:
                if acc.employee_id.gender == 'male':
                    gender = 'M'
                elif acc.employee_id.gender == 'female':
                    gender = 'F'
                else:
                    gender = ''

                val = {
                    'reference': acc.name,
                    'identification_id': acc.employee_id.identification_id,
                    'name': str(acc.employee_id.name) + ' ' + str(acc.employee_id.first_name),
                    'job_id': acc.employee_id.job_id.name,
                    'service_id': acc.employee_id.service_id.description or '',
                    'department_id': acc.employee_id.department_id.description or '',
                    'direction_id': acc.employee_id.direction_id.description or '',
                    'gender': gender,
                    'age': acc.employee_id.age,
                    'birthday': acc.employee_id.birthday.strftime('%d/%m/%Y') if acc.employee_id.birthday else '',
                    'accident_date': acc.accident_date.strftime('%d/%m/%Y') if acc.accident_date else '',
                    'description': acc.work_accident_description or ''
                }
                res.append(val)
        return res

    def add_hr_manager_signature(self):
        res = []
        emp = self.env['hr.employee'].search([], limit=1)
        val = {
            'manager': str(emp.company_id.hr_manager_id.first_name) + ' ' + str(emp.company_id.hr_manager_id.name)
        }
        res.append(val)
        return res

    def print_management_accident_xls(self):
        data = {
            'lines': self.generate_data(),
            'ids': self.id,
            'form': self.read(),
        }
        return self.env.ref('hr_custom.action_work_accident_wizard_xls').report_action(self, data=data)

    def print_management_accident_pdf(self):
        locale = self.env.context.get('lang') or 'en_US'
        data = {'model': self._name, 'form': self.read(), 'work_accident': self.generate_data(),
                'manager': self.add_hr_manager_signature(),
                'date': tools.ustr(
                    babel.dates.format_date(date=datetime.datetime.now(), format='dd MMMM y', locale=locale))}
        return self.env.ref('hr_custom.action_work_accident_wizard_pdf').report_action(self, data=data)