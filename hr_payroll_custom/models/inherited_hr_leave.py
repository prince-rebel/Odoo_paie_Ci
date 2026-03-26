from odoo import fields, models, api


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    to_pay = fields.Boolean('A payer', default=False, tracking=True,
                            help="Cliquez sur le bouton si le congé doit être pris en compte dans la prochaine paye")
    payslip_status = fields.Boolean('Rapporté dans les dernières payes', tracking=True, default=False,
                                    help="Il est coché automatiquement par le système lorsque le congé est pris "
                                         "en compte dans la paye.")
