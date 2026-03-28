import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    resumption_of_service = fields.Boolean('Reprise de service', default=False)
    number_due = fields.Integer("Nbre jour max", related="holiday_status_id.max_days",
                                help="Nombre de jours max qu'il est possible de prendre")

    # @api.constrains('state', 'number_of_days', 'holiday_status_id')
    # def _check_holidays(self):
    #     mapped_days = self.holiday_status_id.get_employees_days((self.employee_id | self.sudo().employee_ids).ids)
    #     for holiday in self:
    #         if holiday.holiday_status_id.time_type == 'other' and holiday.employee_ids:
    #             for employee in holiday.employee_ids:
    #                 if employee.remaining_legal_absence_stock == 0:
    #                     raise ValidationError(_(f"L'employée {employee.name} {employee.first_name} a épuisé son stock "
    #                                             f"d'absence. Il ne peut pas donc faire de demande d'absence"))
    #         if holiday.holiday_status_id.legal_absences:
    #             if holiday.number_due < holiday.number_of_days:
    #                 raise ValidationError(
    #                     _("La réglementation vous autorise à prendre au maximum %s jour(s). Merci de faire"
    #                       " les corrections nécessaires.") % holiday.number_due)

    #         if holiday.holiday_type != 'employee' \
    #                 or not holiday.employee_id and not holiday.employee_ids \
    #                 or holiday.holiday_status_id.requires_allocation == 'no':
    #             continue

    #         if holiday.employee_id:
    #             leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
    #             if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 \
    #                     or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
    #                 raise ValidationError(
    #                     _('The number of remaining time off is not sufficient for this time off type.\n'
    #                       'Please also check the time off waiting for validation.'))
    #         else:
    #             unallocated_employees = []
    #             for employee in holiday.employee_ids:
    #                 leave_days = mapped_days[employee.id][holiday.holiday_status_id.id]
    #                 if float_compare(leave_days['remaining_leaves'], self.number_of_days, precision_digits=2) == -1 \
    #                         or float_compare(leave_days['virtual_remaining_leaves'], self.number_of_days,
    #                                          precision_digits=2) == -1:
    #                     unallocated_employees.append(employee.name)
    #             if unallocated_employees:
    #                 raise ValidationError(
    #                     _('The number of remaining time off is not sufficient for this time off type.\n'
    #                       'Please also check the time off waiting for validation.')
    #                     + _('\nThe employees that lack allocation days are:\n%s',
    #                         (', '.join(unallocated_employees))))

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_number_of_days(self):
        for holiday in self:
            if holiday.date_from and holiday.date_to:
                if holiday.holiday_status_id and holiday.holiday_status_id.is_calendar:
                    # En Odoo 19, date_from/date_to sont des Datetime — utiliser .date() pour le calcul
                    date_from = holiday.date_from.date() if hasattr(holiday.date_from, 'date') else holiday.date_from
                    date_end = holiday.date_to.date() if hasattr(holiday.date_to, 'date') else holiday.date_to
                    tmp = date_end - date_from
                    holiday.number_of_days = tmp.days + 1
                else:
                    holiday.number_of_days = \
                        holiday._get_number_of_days(holiday.date_from, holiday.date_to, holiday.employee_id.id)['days']
            else:
                holiday.number_of_days = 0

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    code = fields.Char('Code', size=4)
    legal_absences = fields.Boolean('Absence légale', default=False)
    max_days = fields.Integer('Nbre max jours', help="Nombre de jours maximum qui peut être pris", default=0)
    is_calendar = fields.Boolean('Basé sur les jours calendaires', default=True)