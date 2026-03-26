# -*- coding: utf-8 -*-

from odoo import fields, models, api


class EmployeeTypeRelation(models.Model):
    _name = "employee_type_relation"
    _description = "Type de relation"

    name = fields.Char("Libellé")
    code = fields.Char("Code")
    description = fields.Text("Description")
