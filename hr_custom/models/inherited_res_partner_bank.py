# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    partner_id = fields.Many2one(required=False)
    acc_number = fields.Char(size=12)
    box_office_code = fields.Char('Code guichet', size=5)
    rib = fields.Char('Clé RIB', size=2)

    @api.constrains('acc_number','box_office_code','rib')
    def _check_length_acc_number(self):
        for rec in self:
            len_acc_number = len(rec.acc_number) if rec.acc_number else 0
            len_rib = len(rec.rib) if rec.rib else 0
            len_box_office_code = len(rec.box_office_code) if rec.box_office_code else 0
            if len_acc_number < 12:
                raise ValidationError(_("Le numero de compte doit être obligatoirement de 12 caractères. "
                                        "Merci de faire les vérifications nécessaires."))
            if len_box_office_code < 5:
                raise ValidationError(
                    _("Le code guichet doit être de 5 caractères. Merci de faire les vérifications nécessaires."))
            if len_rib < 2:
                raise ValidationError(
                    _("La clé RIB doit être de 2 caractères. Merci de faire les vérifications nécessaires."))
