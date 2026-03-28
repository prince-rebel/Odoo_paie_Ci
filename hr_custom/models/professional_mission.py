# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProfessionalMission(models.Model):
    _name = 'hr_custom.professional_mission'
    _description = 'Mission professionnelle'




    name = fields.Char('Reference')
    object = fields.Char('Objet', help="Objet de la mission")
    date_of_departure = fields.Date('Date départ', help="Date de départ en mission professionnelle")
    date_of_return = fields.Date('Date retour', help="Date de retour de la mission professionnelle")
    means_of_transport_id = fields.Many2one('hr_custom.means_of_transport', 'Moyen de transport')
    imputation_budgetaire_id = fields.Many2one('hr.department', 'Imputation Budgetaire',
                                               help="Le service ou le département ou la direction à qui sera imputer le budget")
    destination_ids = fields.Many2many('hr_custom.destination', string="Destionation",
                                       help="Les destinations qui seront visitées lors la mission")
    employee_id = fields.Many2one('hr.employee', 'Employe')


class HrMoyensTransport(models.Model):
    _name = "hr_custom.means_of_transport"
    _description = "Moyens de transport"

    name = fields.Char('Moyen de transport',
                       help="Les moyens de transport qui peuvent être utilisé dans le cadre d'une mission professionnelle")


class HrDestination(models.Model):
    _name = "hr_custom.destination"
    _description = "les destinations des missions"

    name = fields.Char('Destination')
    country_id = fields.Many2one('res.country', 'Pays')


class ResCountry(models.Model):
    _inherit = "res.country"

    nationality = fields.Char('Nationalité')
