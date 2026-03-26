# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    hr_general_manager_id = fields.Many2one('hr.employee', 'Directeur Général',
                                            help="Directeur général de l'entreprise")
    hr_director_id = fields.Many2one('hr.employee', 'Directeur des Ressources Humaines',
                                     help="Directeur des ressources humaines de l'entreprise")
    hr_manager_id = fields.Many2one("hr.employee", "Responsale personnel",
                                    help="Responsable des ressources humaines")
    hr_assistant_id = fields.Many2one("hr.employee", "Assistant(e) Responsable personnel",
                                      help="Assistant(e) du responsable des ressources humaines")
    payroll_manager_id= fields.Many2one("hr.employee", "Responsable Paie", help="Responsable de la paye")
    payroll_assistant_id= fields.Many2one("hr.employee", "Assistant(e) Responsable Paie",
                                          help="Assistant(e) du responsable de la paye")
    max_age_child = fields.Integer('Age maximal enfant à charge', default=21,
                                   help="Une fois cet age atteint, les enfants concernés ne seront plus pris en compte "
                                        "pour la détermination du nombre de part IGR sauf s'il présente un certificat "
                                        "de fréquentation")
    max_age_child_certificat = fields.Integer('Age limit', default=28,
                                              help='Age maximal des enfants à charge avec certificat de fréquentation')
    alert_trial_contract_expiry = fields.Integer(string="Alerte de fin de période d'essai (Jours)", default=0)
    alert_contract_expiry_cadre = fields.Integer(string="Alerte de fin de contrat pour les cadres (Jours)", default=0)
    alert_contract_expiry_non_cadre = fields.Integer(string="Alerte de fin de contrat pour les non cadres (Jours)",
                                                     default=0)
    first_retirement_alert = fields.Integer(string="Première alerte depart retraite (Mois)", readonly=False)#first_alert_retraite
    second_retirement_alert = fields.Integer(string="Deuxième alerte depart retraite (Mois)", readonly=False)#second_alert_retraite
    retirement_age = fields.Integer("Age de départ à la retraite (ans)", default=60)
