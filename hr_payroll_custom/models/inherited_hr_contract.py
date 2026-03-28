# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'

    extra_pay = fields.Integer('Sursalaire', help="le sursalaire de l'employé")
    convention_id = fields.Many2one("hr_custom.convention", "Convention")
    activity_area_id = fields.Many2one("hr_custom.activity_area", "Secteur", help="Secteur d'activité")
    fixed_premiums_ids = fields.One2many("hr_payroll_custom.fixed_premiums", 'contract_id', "Primes Fixes")
    wage = fields.Integer(compute="on_change_salary_category_id")

    @api.onchange("convention_id")
    def on_change_convention_id(self):
        for rec in self:
            if rec.convention_id:
                return {'domain': {'activity_area_id': [('convention_id', '=', rec.convention_id.id)]}}
            else:
                return {'domain': {'activity_area_id': [('convention_id', '=', False)]}}

    @api.onchange("activity_area_id")
    def on_change_activity_area_id(self):
        for rec in self:
            if rec.activity_area_id:
                return {'domain': {'salary_category_id': [('activity_area_id', '=', rec.activity_area_id.id)]}}
            else:
                return {'domain': {'salary_category_id': [('activity_area_id', '=', False)]}}

    @api.depends('salary_category_id')
    def on_change_salary_category_id(self):
        for rec in self:
            if rec.salary_category_id:
                rec.wage = rec.salary_category_id.category_salary_amount
            else:
                rec.wage = 0


class FixedPremiums(models.Model):
    _name = 'hr_payroll_custom.fixed_premiums'
    _description = "Primes fixes"

    input_type_id = fields.Many2one('hr.payslip.input.type', 'Type de prime')
    #code = fields.Char("Code", compute='_get_code_prime')
    contract_id = fields.Many2one('hr.contract', 'Contract')
    amount = fields.Integer('Montant')
