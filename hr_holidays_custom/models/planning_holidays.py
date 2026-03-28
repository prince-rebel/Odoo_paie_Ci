# -*- coding:utf-8 -*-

from odoo import api, fields, _, models
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class PlanningHolidays(models.Model):
    _name = "hr_holidays_custom.planning_holidays"
    _description = "HR Holidays Planning"

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)


    name = fields.Char("Libellé", size=225, compute='_get_label', store=True, readonly=False)
    employee_id = fields.Many2one("hr.employee", 'Employé', required=False, default=_default_employee)
    date_from = fields.Date("Début", required=True)
    date_end = fields.Date("Date de fin", required=True)
    number_of_days = fields.Float("Nombre jours")
    date_first_alert = fields.Date("Date première alerte")
    date_second_alert = fields.Date("Date deuxième alerte")
    holiday_type = fields.Many2one('hr.leave.type', "Type",
                                   default=lambda self: self.env['hr.leave.type'].search(
                                       [('code', '=', 'CONG')], limit=1).id)
    company_id = fields.Many2one('res.company', "Société", default=lambda self: self.env.user.company_id.id)
    direction_id = fields.Many2one("hr.department", "Direction", related="employee_id.direction_id")
    department_id = fields.Many2one("hr.department", "Departement", related="employee_id.department_id")
    service_id = fields.Many2one("hr.department", "Service", related="employee_id.service_id")
    state = fields.Selection([('draft', 'Brouillon'), ('rh', 'Service RH'), ('done', 'Validé'), ('cancel', 'Annulé')],
                             string='Statut', default='draft')

    @api.depends('employee_id')
    @api.onchange('employee_id')
    def _get_label(self):
        # for rec in self:
        result = "Planning personnel de congé "
        if self.employee_id:
            result += str(self.employee_id.identification_id)
        self.name = result

    @api.onchange('date_from', 'date_end')
    @api.depends('date_from', 'date_end')
    def _get_number_of_days(self):
        for rec in self:
            if rec.date_from and rec.date_end:
                date_end = fields.Datetime.from_string(rec.date_end)
                date_from = fields.Datetime.from_string(rec.date_from)
                leave_rec = self.env['hr.leave'].search([], limit=1)
                if leave_rec:
                    rec.number_of_days = 1 + leave_rec._get_number_of_days(date_from, date_end, rec.employee_id.id)['days']
                else:
                    raise ValidationError(_("Impossible de déterminer le nombre de jour. Merci de contacter un administrateur"))
            else:
                rec.number_of_days = 0

    def action_submit(self):
        for rec in self:
            rec.state = 'rh'
            rec.send_notification('hr_holidays_custom.email_template_validate_real_planning')


    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            rec.send_notification('hr_holidays_custom.email_template_real_planning')


    def action_rejected(self):
        for rec in self:
            rec.state = 'draft'
            rec.send_notification('hr_holidays_custom.email_template_real_planning')

    def action_validate(self):
        for rec in self:
            rec.state = 'done'
            rec.send_notification('hr_holidays_custom.email_template_real_planning')

    def action_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.constrains('date_from', 'date_end', 'employee_id')
    def _check_contraints(self):
        if self.date_from > self.date_end:
            raise ValidationError(_("La date de fin doit toujours être supérieure à la date de début"))
        today = date.today()
        if self.date_from.year != today.year or self.date_end.year != today.year:
            raise ValidationError(
                _("Vous ne pouvez prendre des congés prévisionnels que pour cette année %s") % today.year)
        leave_taken = self.get_number_days_taken(self.employee_id.id)
        if leave_taken > self.employee_id.stock_total_holiday:
            raise ValidationError(_("Impossible d'enregistrer cette opération car le nombre de jours demandés doit "
                                    "être inférieur ou égal au nombre de jours possible"))

    def send_notification(self, email_id):
        for rec in self:
            template_id = self.env['ir.model.data']._xmlid_lookup(email_id)

            try:
                mail_templ = self.env['mail.template'].browse(template_id[2])
                result = mail_templ.send_mail(res_id=rec.id, force_send=True)
                return True
            except:
                return False

    def get_number_days_taken(self, id_employee):
        num_day = 0
        if id_employee:
            today = date.today()
            first_date = date(today.year, 1, 1)
            planning_rc = self.env['hr_holidays_custom.planning_holidays'].search([('employee_id', '=', id_employee),
                                                                  ('create_date', '>=', first_date)])
            if planning_rc:
                for planning in planning_rc:
                    num_day += planning.number_of_days
        return num_day

    def cron_send_email_real_planning_alert(self):
        today = fields.Date.today()
        real_plannings = self.env['hr_holidays_custom.planning_holidays'].search([('state', '=', 'done'), ('date_from', '>', today)])
        if real_plannings:
            for line in real_plannings:
                first_alert = line.company_id.first_alert_real_planning
                second_alert = line.company_id.second_alert_real_planning
                line.date_first_alert = str(fields.Date.from_string(line.date_from) +
                                            relativedelta.relativedelta(days=- first_alert))
                line.date_second_alert = str(fields.Date.from_string(line.date_from) +
                                             relativedelta.relativedelta(days=- second_alert))
                if line.date_first_alert == today or line.date_second_alert == today:
                    line.send_notification('email_template_alert_real_planning')
        else:
            pass
