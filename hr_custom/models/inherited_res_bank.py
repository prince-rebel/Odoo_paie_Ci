# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResBank(models.Model):
    _inherit = 'res.bank'

    def default_country_id(self):
        """Get country by default"""
        country = self.env['res.country'].search([('phone_code', '=', 225)], limit=1)
        self.country = country.id
        return country.id

    logo = fields.Binary(string="Logo", readonly=False)
    sigle = fields.Char("Sigle")
    num_inscription  = fields.Char ("N° d'inscription")
    responsable  = fields.Char ("Responsable")
    capital  = fields.Float ("Capital social(en CFA)")
    country = fields.Many2one('res.country', string='Country', default=default_country_id)




