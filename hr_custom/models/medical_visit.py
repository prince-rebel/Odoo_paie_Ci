# -*- coding: utf-8 -*-
from odoo import fields, models, api


class MedicalVisit(models.Model):
    _name = 'hr_custom.medical_visit'
    _description = 'Visite Médicale'

    name = fields.Char('Libellé')
    predicted_date = fields.Date("Date prévue")
    effective_date = fields.Date("Date effective")
    place_of_visit = fields.Char("Lieu de la visite", help="L'hopital dans laquelle les examens médicaux se sont déroulés")
    remark = fields.Text("Commentaires", help="Détails sur la viste médicale")
    employee_id = fields.Many2one('hr.employee', "Employé")
