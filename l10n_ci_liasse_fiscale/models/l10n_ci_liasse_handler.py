from odoo import models


class L10nCiTftCustomHandler(models.AbstractModel):
    _name = 'l10n.ci.tft.custom.handler'
    _inherit = 'account.report.custom.handler'
    _description = "CI TFT Custom Handler"

    def _report_custom_engine_get_note(self, expressions, options, date_scope, current_groupby, next_groupby, offset=0, limit=None, warnings=None):
        if current_groupby:
            return []
        return {
            'ZA': 'A',
            'ZB': 'B',
            'ZC': 'C',
            'ZD': 'D',
            'ZE': 'E',
            'ZF': 'F',
            'ZG': 'G',
            'ZH': 'H',
        }


class L10nCiNotesCustomHandler(models.AbstractModel):
    _name = 'l10n.ci.notes.custom.handler'
    _inherit = 'account.report.custom.handler'
    _description = "CI Notes Annexes Custom Handler"
