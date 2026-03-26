from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    number_holidays_locaux = fields.Float('Congés des nationaux', default='2.2',
                                          help="Nombre de jours de congés mensuels à attribuer aux employés locaux")
    number_holidays_expat = fields.Float('Congés des expatriés', default='5',
                                         help="Nombre de jours de congés mensuels à attribuer aux employés expatriés")
    stock_legal_absence = fields.Integer('Stock annuel des absences légales', default=10,
                                         help="Stock maximum annuel des absences légales autorisées")
