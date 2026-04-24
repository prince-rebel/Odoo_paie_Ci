from odoo import models


class L10nCiNotesCustomHandler(models.AbstractModel):
    _name = 'l10n.ci.notes.custom.handler'
    _inherit = 'account.report.custom.handler'
    _description = "CI Notes Annexes Custom Handler"
