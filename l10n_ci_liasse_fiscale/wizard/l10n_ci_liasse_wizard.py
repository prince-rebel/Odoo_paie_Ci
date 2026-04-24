# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class L10nCiLiasseWizard(models.TransientModel):
    _name = 'l10n.ci.liasse.wizard'
    _description = 'Export Liasse Fiscale DGI Côte d\'Ivoire'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    date_from = fields.Date(
        string='Start date',
        required=True,
        default=lambda self: fields.Date.today().replace(month=1, day=1),
    )
    date_to = fields.Date(
        string='End date',
        required=True,
        default=lambda self: fields.Date.today().replace(month=12, day=31),
    )
    liasse_type = fields.Selection(
        [('NO', 'Normal (NO)'), ('SI', 'Simplifié (SI)'), ('RS', 'Résumé (RS)')],
        string='Liasse type',
        required=True,
        default='NO',
    )
    xml_file = fields.Binary(string='XML File', readonly=True)
    xml_filename = fields.Char(string='Filename', readonly=True)
    state = fields.Selection(
        [('draft', 'Parameters'), ('done', 'Generated')],
        default='draft',
    )

    def action_generate(self):
        self.ensure_one()
        if not self.date_from or not self.date_to:
            raise UserError(_('Please set start and end dates.'))
        if self.date_from > self.date_to:
            raise UserError(_('Start date must be before end date.'))

        export_helper = self.env['l10n.ci.liasse.export']
        xml_bytes = export_helper.generate_xml(
            date_from=self.date_from,
            date_to=self.date_to,
            company=self.company_id,
            liasse_type=self.liasse_type,
        )

        filename = 'liasse_fiscale_{}_{}_{}.xml'.format(
            self.company_id.vat or self.company_id.name.replace(' ', '_'),
            self.liasse_type,
            self.date_to.year,
        )
        self.write({
            'xml_file': base64.b64encode(xml_bytes),
            'xml_filename': filename,
            'state': 'done',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
