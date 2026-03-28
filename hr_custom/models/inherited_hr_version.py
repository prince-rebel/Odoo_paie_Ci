# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class HrVersion(models.Model):
    _inherit = 'hr.version'

    # En Odoo 19, department_id existe déjà sur hr.version — on restreint le domaine
    department_id = fields.Many2one('hr.department', domain="[('type', '=', 'direction')]")
    salary_category_id = fields.Many2one('hr_custom.salary_category', 'Catégorie salariale',
                                         help="Catégorie salariale. Ex: CV-1,M III-1")

    def send_alert_contract(self, email_template_id, versions):
        """
        Envoie un email de notification pour chaque dossier/contrat employé

        :param email_template_id: id du template email
        :param versions: liste de hr.version
        :return: None
        """
        for version in versions:
            email_template = self.env['mail.template'].browse(email_template_id)
            email_template.send_mail(version.id, force_send=True)

    def cron_end_contract_notification(self):
        """
        Vérifie les dates de fin de contrat et de fin de période d'essai
        et envoie des emails de notification aux responsables.
        En Odoo 19, hr.contract est remplacé par hr.version.
        L'état 'open' est remplacé par is_current=True / is_in_contract=True.
        """
        today = datetime.today()
        config_rc = self.env['res.company'].search([], limit=1)

        # Dossiers dont la période d'essai arrive à échéance
        versions_trial = self.env['hr.version'].search([
            ('trial_date_end', '=',
             str(today + relativedelta(days=config_rc.alert_trial_contract_expiry))[:10]),
            ('is_current', '=', True),
        ])
        # Dossiers des non-cadres arrivant à expiration
        versions_not_cadre = self.env['hr.version'].search([
            ('contract_date_end', '=',
             str(today + relativedelta(days=config_rc.alert_contract_expiry_non_cadre))[:10]),
            ('is_in_contract', '=', True),
            ('employee_id.employee_status', 'not in', ('cadre', 'csup')),
        ])
        # Dossiers des cadres arrivant à expiration
        versions_cadre = self.env['hr.version'].search([
            ('contract_date_end', '=',
             str(today + relativedelta(days=config_rc.alert_contract_expiry_cadre))[:10]),
            ('is_in_contract', '=', True),
            ('employee_id.employee_status', 'in', ('cadre', 'csup')),
        ])

        if versions_trial:
            email_template_id = self.env.ref('hr_custom.template_end_trial_period').id
            self.send_alert_contract(email_template_id, versions_trial)

        email_template_id = self.env.ref('hr_custom.template_end_contract').id
        if versions_not_cadre:
            self.send_alert_contract(email_template_id, versions_not_cadre)
        if versions_cadre:
            self.send_alert_contract(email_template_id, versions_cadre)
