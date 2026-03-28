# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
import babel
import datetime
import logging

_logger = logging.getLogger(__name__)

class EmployeeResignation(models.TransientModel):
    _name = 'hr_custom.employee_resignation_wizard'
    _description = 'Assistant de départ des employés'

    start_date = fields.Date('Début')
    end_date = fields.Date('Fin')
    departure_reason_ids = fields.Many2many('hr.departure.reason', string='Motif de départ',
                                            help="Selectionnez les motifs pour lesquels vous désirez voir dans le "
                                                 "rapport. Laissez le champ vide si vous souhaitez voir tous les motifs")
    company_id = fields.Many2one('res.company','Société', default=lambda self: self.env.user.company_id.id)

    def computeEmployeeResignation(self):
        motif_list = []
        if self.start_date:
            check_start_date = ('departure_date', '>=', self.start_date)
        else:
            check_start_date = (1, '=', 1)
        if self.end_date:
            check_end_date = ('departure_date', '<=', self.end_date)
        else:
            check_end_date = (1, '=', 1)

        if self.departure_reason_ids:
            for motif in self.departure_reason_ids:
                motif_list.append(motif.id)
        else:
            motifs = self.env['hr.departure.reason'].search([])
            for motif in motifs:
                motif_list.append(motif.id)
        employee_list = self.env['hr.employee'].search([('departure_reason_id', 'in', motif_list),
                                                        check_start_date, check_end_date,
                                                        '|', ('active', '=', True), ('active', '=', False)],
                                                       order="identification_id asc")
        res = []
        if employee_list:
            for emp in employee_list:
                gender = ''
                status = ''
                if emp.employee_status == 'cadre':
                    status = 'CADRE'
                elif emp.employee_status == 'non_cadre':
                    status = 'NON CADRE'
                if emp.gender == 'male':
                    gender = 'M'
                elif emp.gender == 'female':
                    gender = 'F'
                else:
                    gender = 'other'

                contract_type_id = ''
                contrat_empl = self.env['hr.version'].search([('employee_id', '=', emp.id), ('is_current', '=', True)], limit=1)

                if contrat_empl:
                    contract_type_id = contrat_empl.contract_type_id.name
                    cat = contrat_empl.salary_category_id.name if contrat_empl.salary_category_id else ''
                else:
                    cat = emp.salary_category_id.name if emp.salary_category_id else ''
                val = {
                    'matricule': emp.identification_id or '',
                    'cat': cat or '',
                    'status': status or '',
                    'age': emp.age or '',
                    'gender': gender or '',
                    'birthday': emp.birthday.strftime("%d/%m/%Y") if emp.birthday else '',
                    'contract_type_id': contract_type_id or '',
                    'name': (str(emp.name) + ' ' + str(emp.first_name)) or '',
                    'job_id': emp.job_id.name if emp.job_id else '',
                    'department_id': emp.department_id.description if emp.department_id else '',
                    'service_id': emp.service_id.description if emp.service_id else '',
                    'direction_id': emp.direction_id.description if emp.direction_id else '',
                    'hiring_date': emp.hiring_date.strftime("%d/%m/%Y") if emp.hiring_date else '',
                    'departure_date': emp.departure_date.strftime("%d/%m/%Y") if emp.departure_date else '',
                    'departure_reason': emp.departure_reason_id.name if emp.departure_reason_id else ''
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

    def total_employee(self):
        emp = []
        total_employee = self.env['hr.employee'].search([])
        total_male = self.env['hr.employee'].search([('gender', '=', 'male')])
        total_female = self.env['hr.employee'].search([('gender', '=', 'female')])
        val = {
            'total_employee': len(total_employee),
            'total_male': len(total_male),
            'total_female': len(total_female)
        }
        emp.append(val)
        return emp

    def print_employee_resignation_xls(self):
        data = {
            'lines': self.computeEmployeeResignation(),
            'ids': self.id,
            'form': self.read(),
        }
        return self.env.ref('hr_custom.action_employee_resignation').report_action(self, data=data)

    def print_employee_resignation_pdf(self):
        locale = self.env.context.get('lang') or 'en_US'
        data = {'model': self._name, 'form': self.read(), 'motifs': self.computeEmployeeResignation(),
                'manager': self.add_hr_manager_signature(),
                'date': tools.ustr(
                    babel.dates.format_date(date=datetime.datetime.now(), format='dd MMMM y', locale=locale))
                }
        return self.env.ref('hr_custom.action_employee_resignation_pdf').report_action(self, data=data)



