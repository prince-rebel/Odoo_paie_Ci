# -*- coding: utf-8 -*-
from odoo import fields, models, api

Type_department = [('direction', 'Direction'), ('department', 'Departement'), ('service', 'Service')]
class HrDepartment(models.Model):
    _inherit = 'hr.department'

    type = fields.Selection(Type_department, "Type")
    description = fields.Char('Description')
