# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from ..models import emergency_contacts
import datetime
import babel

class EmployeeListWizard(models.TransientModel):
    _name = "hr_custom.employee_list_wizard"
    _description = "Assistant liste des employes"

    direction_ids = fields.Many2many('hr.department','employee_list_wizard_direction_rel', string='Directions', domain=[('type', '=', 'direction')])
    department_ids = fields.Many2many('hr.department', 'employee_list_wizard_department_rel', string='Départements', domain=[('type', '=', 'department')])
    gender = fields.Selection(emergency_contacts.Type_gender, string='Genre')
    contract_type_ids = fields.Many2many('hr.contract.type', string='Type de contrat')

    def generate_data(self):
        if not self.direction_ids:
            dir = (1, '=', 1)
        else:
            dir_rc = []
            for dir in self.direction_ids:
                dir_rc.append(dir.id)
            dir = ('direction_id', 'in', dir_rc)
        if not self.department_ids:
            dep = (1, '=', 1)
        else:
            dep_rc = []
            for dep in self.department_ids:
                dep_rc.append(dep.id)
            dep = ('department_id', 'in', dep_rc)
        if not self.gender:
            gend = (1, '=', 1)
        else:
            gend = ('gender', '=', self.gender)
        if not self.contract_type_ids:
            cont_typ = (1, '=', 1)
        else:
            cont_list = []
            for cont in self.contract_type_ids:
                cont_list.append(cont.id)
            cont_typ = ('contract_type_id', 'in', cont_list)

        employees = self.env['hr.employee'].search([dir, dep, gend, ('active', '=', True)], order="identification_id asc")

        res = []
        if employees:
            for employee in employees:
                contract = self.env['hr.contract'].search([('employee_id', '=', employee.id), ('state', '=', 'open'),
                                                           ('active', '=', True), cont_typ], limit=1)
                if self.contract_type_ids and not contract:
                    continue
                status = ''
                if employee.employee_status == 'cadre':
                    status = 'CADRE'
                elif employee.employee_status == 'non_cadre':
                    status = 'NON CADRE'
                elif employee.employee_status == 'csup':
                    status = 'CADRE SUP'
                if employee.gender == 'male':
                    gender = 'M'
                elif employee.gender == 'female':
                    gender = 'F'
                else:
                    gender = 'Autre'
                val = {
                    'identification_id': employee.identification_id,
                    'name': str(employee.name) + ' ' + str(employee.first_name),
                    'job_id': employee.job_id.name if employee.job_id else '',
                    'service_id': employee.service_id.description if employee.service_id else '',
                    'department_id': employee.department_id.description if employee.department_id else '',
                    'direction_id': employee.direction_id.description if employee.direction_id else '',
                    'gender': gender,
                    'status': status,
                    'salary_category': employee.salary_category_id.name if employee.salary_category_id else '',
                    'contract_type': contract.contract_type_id.name if contract.contract_type_id else '',
                    'age': employee.age,
                    'birthday': employee.birthday.strftime(
                        '%d/%m/%Y') if employee.birthday else '',
                    'hiring_date': employee.hiring_date.strftime(
                        '%d/%m/%Y') if employee.hiring_date else '',
                }
                res.append(val)
            if not res:
                raise ValidationError(_(f"Aucune donnée à afficher. Merci de réessayer et de contacter un administrateur "
                                    f"si vous pensez que c'est une erreur."))
        else:
            raise ValidationError(_(f"Aucune donnée à afficher. Merci de réessayer et de contacter un administrateur "
                                    f"si vous pensez que c'est une erreur."))
        return res

    def add_hr_director_signature(self):
        res = []
        emp = self.env['hr.employee'].search([], limit=1)
        val = {
            'manager': str(emp.company_id.hr_director_id.first_name) + ' ' + str(emp.company_id.hr_director_id.name)
        }
        res.append(val)
        return res

    def print_report_xls(self):
        data = {
            'lines': self.generate_data(),
            'ids': self.id,
            'form': self.read(),
            'gender': self.gender
        }
        return self.env.ref('hr_custom.action_report_employee_list_xls').report_action(self, data=data)

    def print_report_pdf(self):
        locale = self.env.context.get('lang') or 'en_US'
        data = {'model': self._name, 'form': self.read(), 'lines': self.generate_data(),
                'manager': self.add_hr_director_signature(), 'gender': self.gender, 'date': tools.ustr(
                babel.dates.format_date(date=datetime.datetime.now(), format='dd MMMM y', locale=locale))}

        return self.env.ref('hr_custom.action_report_employee_list_pdf').report_action(self, data=data)
