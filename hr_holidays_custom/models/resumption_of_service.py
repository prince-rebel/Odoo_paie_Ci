# -*- coding:utf-8 -*-

from odoo import api, fields, _, models, tools
from dateutil import relativedelta
from odoo.exceptions import ValidationError
import babel

Type_state = [('draft', "brouillon"), ('done', "Validé"), ('cancel', "Annulé")]

class ResumptionOfService(models.Model):
    _name = "hr_holidays_custom.resumption_of_service"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Reprise de service"
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', 'Employé', tracking=True)
    holidays_id = fields.Many2one('hr.leave', 'Congé', domain="[('employee_id', '=', employee_id),"
                                                              "('state', '=', 'validate'),"
                                                              "('resumption_of_service','=',False)]")
    resumption_date = fields.Date("Date de reprise")
    resumption_hour = fields.Char("Heure de réprise", default='07H30')
    number_of_holidays = fields.Float("Nombre de jours",  related="holidays_id.number_of_days")
    direction_id = fields.Many2one("hr.department", "Direction", related="employee_id.direction_id")
    department_id = fields.Many2one("hr.department", "Departement", related="employee_id.department_id")
    service_id = fields.Many2one("hr.department", "Service", related="employee_id.service_id")
    state = fields.Selection(Type_state, "Etat", default="draft", tracking=True)
    validator_id = fields.Many2one('hr.employee', 'Validateur', related='employee_id.parent_id')
    company_id = fields.Many2one('res.company', 'Société', related="employee_id.company_id")

    @api.onchange('holidays_id')
    def onChangeHoliday(self):
        for rec in self:
            if rec.holidays_id:
                rec.resumption_date = rec.holidays_id.request_date_to + relativedelta.relativedelta(days=+1) \
                    if rec.holidays_id.request_date_to else False

    def action_validate(self):
        for rec in self:
            if rec.holidays_id:
                rec.state = 'done'
                rec.holidays_id.resumption_of_service = True
                # definir la nouvelle date de retour du dernier congé dans la fiche employé
                rec.employee_id.date_return_last_holidays = rec.resumption_date
    def action_to_draft(self):
        for rec in self:
            if rec.holidays_id:
                rec.state = 'draft'
                rec.holidays_id.resumption_of_service = False


    def action_to_cancel(self):
        for rec in self:
            if rec.holidays_id:
                rec.state = 'cancel'
                rec.holidays_id.resumption_of_service = False



class ReportResumptionOfService(models.AbstractModel):
    _name = 'report.hr_holidays_custom.report_resumption_of_service'
    _description = 'Attestation de reprise de service'

    def _get_report_values(self, docids, data=None):
        docs = self.env['hr_holidays_custom.resumption_of_service'].browse(docids)
        if docs.state != 'done':
            raise ValidationError(_("Vous ne pouvez imprimer la fiche de reprise de congé que si elle est validée. "
                                    "Merci de faire le nécessaire ou de contacter un administrateur su vous pensez "
                                    "que c'est une erreur."))
        else:
            locale = self.env.context.get('lang') or 'en_US'
            date_of_recovery = tools.ustr(
                babel.dates.format_date(date=docs.resumption_date, format='dd MMMM y', locale=locale))

            return {
                'doc_ids': docs.ids,
                'doc_model': 'hr_holidays_custom.resumption_of_service',
                'docs': docs,
                'date_of_recovery': date_of_recovery,
            }