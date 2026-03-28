# -*- coding:utf-8 -*-

from odoo import api, fields, _, models

Type_employee = [('j', 'Journalier'), ('m', 'Mensuel')]
Type_cotisation = [('cnps', 'Régime de retraite'), ('other', 'Autres régimes')]

class CnpsSlice(models.Model):
    _name = "hr_payroll_custom.cnps_slice"
    _description = "Tranche de la CNPS"
    _order = "sequence"

    name = fields.Char("Libellé")
    active = fields.Boolean("Actif", default=True)
    sequence = fields.Integer('Sequence', default=10)
    amount_min = fields.Float("Montant Min", default=0.0)
    amount_max = fields.Float('Montant Max', default=0.0)
    type = fields.Selection(Type_employee, 'Type', default=False)


class CnpsCotisationTemplate(models.Model):
    _name = "hr_payroll_custom.cnps_cotisation_template"
    _description = "Ligne du modèle de cotisation CNPS"
    _order = "sequence"

    name = fields.Char("Designation")
    company_id = fields.Many2one("res.company", "Société", default=lambda self: self.env.user.company_id.id)
    rate = fields.Float("Taux") #taux
    sequence = fields.Integer("Sequence", default=10)
    active = fields.Boolean("Actif", default=True)
    type = fields.Selection(Type_cotisation, 'Type', default=False)
    #account_id = fields.Many2one('account.account', 'Compte comptable associé', domain="[('company_id', '=', company_id)]")