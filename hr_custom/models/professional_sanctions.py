# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProfessionalSanctions(models.Model):
    _name = 'hr_custom.professional_sanctions'
    _description = 'Sanctions professionnelles'

    name = fields.Char('Motif')
    description = fields.Char(string='Description')
    date_of_penalty = fields.Date('Date')
    number_of_days_suspension = fields.Integer('Nbre de jours', help="Nombre de jours de suspension de l'employé")
    type_sanction_id = fields.Many2one('hr_custom.type_of_penalty', 'Type sanction')
    employee_id = fields.Many2one('hr.employee', 'Employé')




class TypePenalty(models.Model):
    _name = 'hr_custom.type_of_penalty'
    _description = "Type de sanctions"

    name = fields.Char('Libelle')
    number_of_days_suspension = fields.Integer('Nbre de jours', help="Nombre de jours de suspension de l'employé")