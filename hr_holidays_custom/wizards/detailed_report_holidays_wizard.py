# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, exceptions
from odoo import tools
import babel


class HolidaysSummaryEmployeeDepartment(models.TransientModel):
    _name = 'hr_holidays_custom.detailed_report_holiday'
    _description = 'Assistance de congés pris'

    date_to = fields.Date(string='Au')
    date_from = fields.Date(string="De")
    department_ids = fields.Many2many('hr.department', 'department_detailed_report_holidays', 'department_id',
                                      'detailed_report_holiday_id', string='Département(s)',
                                      domain=[('type', '=', 'department')], required=False)
    direction_ids = fields.Many2many('hr.department', 'direction_detailed_report_holidays', 'direction_id',
                                     'detailed_report_holiday_id', string='Direction(s)',
                                     domain=[('type', '=', 'direction')])
    service_ids = fields.Many2many('hr.department', 'service_detailed_report_holidays', 'service_id',
                                   'detailed_report_holiday_id', string='Service(s)',
                                   domain=[('type', '=', 'service')])
    holiday_status = fields.Selection([('Approved', 'Approuvé')], string='Statut', required=False, default='Approved')
    gender = fields.Selection([('male', 'M'), ('female', 'F')], string='Genre')
    holiday_type_ids = fields.Many2many('hr.leave.type', string="Type de congés")

    def generate_data(self):
        holiday_list = []
        if not self.department_ids:
            dep = (1, '=', 1)
        else:
            for dep in self.department_ids:
                holiday_list.append(dep.id)
            dep = ('department_id', 'in', holiday_list)
        if not self.gender:
            gend = (1, '=', 1)
        else:
            gend = ('employee_id.gender', '=', self.gender)
        if not self.direction_ids:
            dir = (1, '=', 1)
        else:
            if self.direction_ids:
                for dir in self.direction_ids:
                    holiday_list.append(dir.id)
                dir = ('employee_id.direction_id', 'in', holiday_list)
        if not self.holiday_type_ids:
            type = (1, '=', 1)
        else:
            if self.holiday_type_ids:
                for type in self.holiday_type_ids:
                    holiday_list.append(type.id)
                type = ('holiday_status_id.id', 'in', holiday_list)
        holidays = self.env['hr.leave'].search([dep, gend, type, dir,
                                                ('request_date_from', '>=', self.date_from),
                                                ('request_date_from', '<=', self.date_to),
                                                ('state', '=', 'validate')]).sorted(
            key=lambda r: r.employee_id.identification_id)
        res = []
        if holidays:
            for emp in holidays:
                gender = ''
                if emp.employee_id.gender == 'male':
                    gender = 'M'
                else:
                    if emp.employee_id.gender == 'female':
                        gender = 'F'
                val = {
                    'identification_id': emp.employee_id.identification_id or '',
                    'name': str(emp.employee_id.name) + ' ' + str(emp.employee_id.first_name) or '',
                    'job_id': emp.employee_id.job_id.name or '',
                    'service_id': emp.employee_id.service_id.description or '',
                    'department_id': emp.employee_id.department_id.description or '',
                    'direction_id': emp.employee_id.direction_id.description or '',
                    'duree': emp.number_of_days_display or '',
                    'date_start': emp.request_date_from.strftime('%d/%m/%Y') if emp.request_date_from else '',
                    'date_return': emp.request_date_to.strftime('%d/%m/%Y') if emp.request_date_to else '',
                    'gender': gender or '',
                    'holiday_status_id': emp.holiday_status_id.name or '',
                }
                res.append(val)
        return res

    def add_interval_date(self):
        res = []
        val = {
            'date_from': self.date_from.strftime('%d/%m/%Y'),
            'date_to': self.date_to.strftime('%d/%m/%Y'),
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

    def print_report_holiday_xls(self):
        data = {
            'lines': self.generate_data(),
            'ids': self.id,
            'form': self.read(),
        }
        return self.env.ref('hr_holidays_custom.action_detailed_report_holiday_xls').report_action(self, data=data)

    def print_report_holiday_pdf(self):
        locale = self.env.context.get('lang') or 'en_US'
        data = {'model': self._name, 'form': self.read(), 'holidays': self.generate_data(),
                'res': self.add_interval_date(),
                'manager': self.add_hr_manager_signature(),
                'date': tools.ustr(
                    babel.dates.format_date(date=datetime.datetime.now(), format='dd MMMM y', locale=locale))
                }
        return self.env.ref('hr_holidays_custom.action_detailed_report_holiday_pdf').report_action(self, data=data)
