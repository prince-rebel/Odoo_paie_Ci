# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    department_id = fields.Many2one(domain="[('type', '=', 'direction')]")
    salary_category_id = fields.Many2one('hr_custom.salary_category', 'Catégorie salariale',
                                         help="Catégorie salariale. Ex: CV-1,M III-1")

    def send_alert_contract(self, email_template_id, contracts):
        """

        :param email_template_id: id of emaim template
        :param contracts: list of contract
        :return: None
        """
        for contract in contracts:
            email_template = self.env['mail.template'].browse(email_template_id)
            email_template.send_mail(contract.id, force_send=True)

    def cron_end_contract_notification(self):
        """
        Fonction verifiant la date de fin de contrat et de fin de periode d'essai ensuite envois un mail de notification
        aux différents responsables de la société
        :return:
        """
        today = datetime.today()
        config_rc = self.env['res.company'].search([], limit=1)
        #Recupération des contrats dont la période d'essai est échue
        contracts_trial = self.env['hr.contract'].search([
            ('trial_date_end', '=', str(today + relativedelta(days=config_rc.alert_trial_contract_expiry))[:10]),
            ('state', '=', 'open')])
        # Recupération des contrats des non cadres
        contracts_not_cadre = self.env['hr.contract'].search([
            ('date_end', '=', str(today + relativedelta(days=config_rc.alert_contract_expiry_non_cadre))[:10]),
            ('state', '=', 'open'),('employee_id.employee_status','not in', ('cadre','csup'))])
        # Recupération des contrats des cadres qui arrivent à expiration
        contracts_cadre = self.env['hr.contract'].search(
            [('date_end', '=', str(today + relativedelta(days=config_rc.alert_contract_expiry_cadre))[:10]),
             ('state', '=', 'open'),('employee_id.employee_status','in', ('cadre','csup'))])
        #Envois des mails selon le cas
        if contracts_trial:
            email_template_id = self.env.ref('hr_custom.template_end_trial_period').id
            self.send_alert_contract(email_template_id, contracts_trial)

        email_template_id = self.env.ref('hr_custom.template_end_contract').id
        if contracts_not_cadre:
            self.send_alert_contract(email_template_id, contracts_not_cadre)
        if contracts_cadre:
            self.send_alert_contract(email_template_id, contracts_cadre)

    @api.constrains('name')
    def _check_unique_name(self):
        for rec in self:
            count_name = self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)])
            if count_name > 0:
                raise ValidationError(
                    _("Cette référence de contrat est déjà attribuée. S'il s'agit du même contrat, veuillez le "
                      "rechercher et actualiser les données. Dans le cas contraire, définissez une nouvelle référence."))

