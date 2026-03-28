# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    max_cnps_tax_base = fields.Float("Plafond regime de retraite mensuel", default=3354000,
                                     help="Plafond du regime de la CNPS est de 3.354.000 FCFA par défaut")
    max_other_tax_base = fields.Float("Plafond regime autres contributions", default=75000,
                                      help="Plafond du regime des autres contributions est de 75.000 FCFA par défaut")
    work_accident_rate = fields.Float('Taux accident de travail', default=2.0)  # taux_accident_travail
    family_benefit_rate = fields.Float('Taux prestation familiale', default=5.0)  # taux_prestation_familiale
    maternity_insurance_rate = fields.Float('Taux assurance maternité', default=0.75)  # taux_assurance_mater
    local_employee_cnps_rate = fields.Float('Taux CNPS employé local', default=6.30)  # taux_cnps_employee_local
    expatriate_employee_cnps_rate = fields.Float('Taux CNPS employé expatrié', default=6.30)  # taux_cnps_employe_expat
    employer_cnps_rate = fields.Float('Taux CNPS employeur', default=7.70)  # taux_cnps_employer
    employer_identification_cnps = fields.Char("Numéro CNPS", size=124, required=False)  # num_cnps
    acronym = fields.Char('Sigle')
    legal_status = fields.Char('Forme', help="S.A., S.A.R.L., S.N.C., S.C.S...")
    tax_base_service = fields.Char("Service des impots",
                                   help="Service des impôts en charge de receptionner les déclarations "
                                        "de l'entreprise.")
    account_number = fields.Char('Numéro de compte', help="Utilisé pour la déclaration de l'ITS")
    system_implementation_date = fields.Date('Date de mise en place du système', default="2022-01-01",
                                             help="Cette date permettra de tenir compte de certaines informations "
                                                  "antérieur telle que le solde antérieur des congés dans les calculs")
    profession = fields.Char('Profession', help="Profession de la société. Utilisé dans l'Etat 301")
    address = fields.Char('Adresse postale', help="Adresse postale de la société. Utilisé dans l'Etat 301")
    establishment_code = fields.Char('Code Etab.', help="Code Établissement. Utilisé au niveau de la déclaration CNPS")
    activity_code = fields.Char('Code Activ.', help="Code Activité. Utilisé au niveau de la déclaration CNPS")
    activity_label = fields.Char('Activité', help="Activité. Utilisé dans la déclaration FDFP")
    cmu_amount = fields.Integer('Montant de la CMU', default=1000,
                                help="Renseigner le montant cumulé patronal et salarial de la mensualité de la cotisation CMU")
    bonus_transport = fields.Integer('Primes de transport', default=30000,
                                     help="Renseignez la prime de transport non imposable selon la législation "
                                          "en vigueur")
