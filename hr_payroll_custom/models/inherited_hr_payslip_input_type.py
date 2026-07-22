# -*- coding: utf-8 -*-
import re
import unicodedata

from odoo import api, fields, models


class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'

    premium_treatment = fields.Selection(
        [
            ('none', "Aucun (géré par une règle salariale dédiée)"),
            ('taxable', "Prime imposable (ajoutée au salaire brut imposable)"),
            ('non_taxable', "Prime non imposable (versée nette, sans impact sur l'impôt)"),
        ],
        string="Traitement automatique",
        default='none',
        required=True,
        help="Pour les primes déjà connues du système (Transport, Rendement, Gratification, "
             "Congé, Indemnité de représentation...), laissez 'Aucun' : elles sont déjà "
             "calculées par une règle salariale dédiée.\n\n"
             "Pour une prime que vous créez vous-même et qui n'a pas encore de règle "
             "dédiée, choisissez si elle est imposable ou non : elle sera automatiquement "
             "prise en compte dans le calcul du bulletin de paie, sans intervention "
             "technique supplémentaire.",
    )

    @api.onchange('name')
    def _onchange_name_suggest_code(self):
        """Propose un code technique à partir du nom, pour un utilisateur non technicien."""
        for rec in self:
            if rec.name and not rec.code:
                normalized = unicodedata.normalize('NFKD', rec.name)
                ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
                code = re.sub(r'[^A-Z0-9]+', '_', ascii_name.upper()).strip('_')
                rec.code = code[:32] or 'NOUVELLE_PRIME'
