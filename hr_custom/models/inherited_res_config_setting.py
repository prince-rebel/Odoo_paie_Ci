from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    alert_trial_contract_expiry = fields.Integer(string="Alerte de fin de période d'essai (Jours)",
                                                 related="company_id.alert_trial_contract_expiry",
                                                 readonly=False, help="Définir le nombre de jours avant la date de fin"
                                                                      " de période d'essai du contrat des cadres et non"
                                                                      " cadres pour  recevoir une alerte par mail")
    alert_contract_expiry_cadre = fields.Integer(string="Alerte de fin de contrat pour les cadres (Jours)",
                                                 related="company_id.alert_contract_expiry_cadre",
                                                 readonly=False, help="Définir le nombre de jours avant la date de fin"
                                                                      " du contrat des cadres pour recevoir une alerte"
                                                                      " par mail")
    alert_contract_expiry_non_cadre = fields.Integer(string="Alerte de fin de contrat pour les non cadres (Jours)",
                                                     related="company_id.alert_contract_expiry_non_cadre",
                                                     readonly=False, help="Définir le nombre de jours avant la date de"
                                                                          " fin du contrat des non cadres pour recevoir"
                                                                          " une alerte par mail")
    first_retirement_alert = fields.Integer(string="Première alerte depart retraite (Mois)", readonly=False,
                                          related="company_id.first_retirement_alert")#first_alert_retraite
    second_retirement_alert = fields.Integer(string="Deuxième alerte depart retraite (Mois)", readonly=False,
                                           related="company_id.second_retirement_alert")#second_alert_retraite