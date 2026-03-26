# -*- coding: utf-8 -*-

from odoo import fields, models, api

Family_relationship = [('grand_parent', 'Grand père/Grande mère'), ('parent', 'Père / Mère'),
                              ('conjoint', 'Conjoint(e)'), ('enfant', 'Enfant'), ('frere', 'Frère / Soeur'),
                              ('voisin', 'Voisin'),
                              ('oncle', 'Oncle/Tante'), ('cousin', 'Cousin / Cousine'), ('other', 'Autres')]

Type_gender = [('male', 'Masculin'), ('female', 'Féminin'),('other','Autre')]

class EmergencyContacts(models.Model):
    _name = 'hr_custom.emergency_contacts'
    _description = "Contacts d'urgence"

    name = fields.Char("Nom et prenoms", help="Nom complet")
    email = fields.Char("Email")
    first_contact = fields.Char('Premier contact')
    second_contact = fields.Char('Deuxième contact')
    state = fields.Selection(Family_relationship, 'Type de lien', help="Lien de parenté")
    gender = fields.Selection(Type_gender, "Sexe")
    observations = fields.Html(string="Observations", help="Ajouter des informations complémentaires")
    employee_id = fields.Many2one("hr.employee", 'Employé')
