from odoo import fields, models, api


# class LegalHolidays(models.Model):
#     _name = 'hr_holidays_custom.legal_holidays'
#     _description = 'Jours fériés légaux'
#
#     name = fields.Char('Libellé')
#     date = fields.Date('Date')
#     payroll_in = fields.Boolean('Chômer et payer', default=False)
#     description = fields.Text('Description')
#     is_recurring = fields.Boolean('Est-il récurrent?', default=False)


class CalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    is_recurring = fields.Boolean('Est-il récurrent?', default=False)