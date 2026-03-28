from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self):
        record = super(HrPayslipEmployees, self).compute_sheet()
        id_payslip_run = record.get('res_id')
        if id_payslip_run:
            payslip_run_rec = self.env['hr.payslip.run'].search([('id', '=', id_payslip_run)])
            if payslip_run_rec:
                payslip_run_rec.compute_payslip_input_line_ids()
            else:
                raise ValidationError(
                    _("Impossible de récupérer les primes fixes des contrats des employés. Merci de ressayer et de contacter"
                      "un administrateur si cela persiste."))
            payslip_run_rec.deletion_payslip_input_duplicates()
        return record
