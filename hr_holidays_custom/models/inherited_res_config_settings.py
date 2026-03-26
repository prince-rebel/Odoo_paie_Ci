from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    number_holidays_locaux = fields.Float('Employés locaux', related='company_id.number_holidays_locaux',
                                          help="Nombre de jours de congés mensuels à attribuer aux employés locaux",
                                          readonly=False)
    number_holidays_expat = fields.Float('Employés expatriés', related='company_id.number_holidays_expat',
                                         help="Nombre de jours de congés mensuels à attribuer aux employés expatriés",
                                         readonly=False)
    stock_legal_absence = fields.Integer('Stock annuel des absences légales', related='company_id.stock_legal_absence',
                                         readonly=False, help="Stock maximum annuel des absences légales autorisées")
