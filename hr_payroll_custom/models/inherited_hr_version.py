# -*- coding: utf-8 -*-
# Migration Odoo 17 → 19 : hr.contract remplacé par hr.version
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class HrVersion(models.Model):
    _inherit = 'hr.version'

    extra_pay = fields.Integer('Sursalaire', help="le sursalaire de l'employé")
    convention_id = fields.Many2one("hr_custom.convention", "Convention")
    activity_area_id = fields.Many2one("hr_custom.activity_area", "Secteur", help="Secteur d'activité")
    fixed_premiums_ids = fields.One2many("hr_payroll_custom.fixed_premiums", 'version_id', "Primes Fixes")
    # Note : wage existe déjà sur hr.version (Monetary). On le remplit via onchange salary_category_id.
    # salary_category_id est défini dans hr_custom sur hr.version.

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

    prime_type_id = fields.Many2one(
        'hr_payroll_custom.prime_type', 'Type de prime',
        help="Sélectionnez une rubrique créée dans la configuration des primes. "
             "La règle salariale correspondante sera appliquée automatiquement."
    )
    # Kept for backward compatibility (TRSP, ASM, CMU legacy lines)
    input_type_id = fields.Many2one('hr.payslip.input.type', 'Type (système)')
    is_taxable = fields.Boolean('Imposable', related='prime_type_id.is_taxable', store=False)
    # Migration Odoo 19 : contract_id → version_id
    version_id = fields.Many2one('hr.version', 'Dossier employé', ondelete='cascade')
    amount = fields.Integer('Montant')

    @api.onchange('prime_type_id')
    def _onchange_prime_type_id(self):
        if self.prime_type_id:
            self.input_type_id = self.prime_type_id.input_type_id
