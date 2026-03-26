# -*- coding: utf-8 -*-
from odoo import fields, models, api



class WorkAccident(models.Model):
    _name = 'hr_custom.work_accident'
    _description = 'Accidents de travail'


    name = fields.Char('Reference')
    accident_date = fields.Date("Accident Date")
    work_accident_description = fields.Html(string='Description')
    employee_id = fields.Many2one('hr.employee', 'Employee')
