import logging
import babel
from odoo import fields, models, tools, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil import relativedelta

_logger = logging.getLogger(__name__)


class InverseCalculation(models.TransientModel):
    _name = 'hr_payroll_custom.inverse_calculation'
    _description = 'Calcul inverse du salaire'

    type_calcul = fields.Selection([('brut', 'Par le brut imposable'), ('net', 'Par le net')], 'Méthode de calcul',
                                   required=True)
    montant = fields.Integer("Montant ", required=True)

    def compute(self):
        for rec in self:
            payslip_obj = self.env['hr.payslip']
            contract = self.env['hr.contract'].browse(rec._context.get('active_id'))


            total_intrant = contract.wage + sum(prime.amount for prime in contract.fixed_premiums_ids)

            if total_intrant > rec.montant:
                raise ValidationError('Le montant est inférieur aux intrants')

            structure_salariale = contract.structure_type_id.default_struct_id

            now = datetime.now()
            date_from = datetime(now.year, now.month, 1)
            date_to = date_from + relativedelta.relativedelta(months=1, days=-1)

            vals = {
                'name': _('Salary Slip of %s for %s') % (contract.employee_id.name, 'Novembre 2023'),
                'employee_id': contract.employee_id.id,
                'date_from': date_from,
                'date_to': date_to,
                'contract_id': contract.id,
                'struct_id': structure_salariale.id,
            }

            payslip_id = payslip_obj.create(vals)
            payslip_id._compute_input_line_ids()
            input_records_to_delete = {}
            for input_line in payslip_id.input_line_ids:
                input_rec = self.env['hr.payslip.input'].search(
                    [('input_type_id', '=', input_line.input_type_id.id),
                     ('payslip_id', '=', input_line.payslip_id.id)], limit=2)

                if len(input_rec) >= 2:
                    input_records_to_delete[input_rec[1].id] = True

            #Suppression des rubiques généré en doublon
            self.env['hr.payslip.input'].browse(list(input_records_to_delete.keys())).unlink()

            payslip_id.compute_sheet()

            payslip_input_rec = self.env['hr.payslip.input'].search(
                [('code', '=', 'SURSA'), ('payslip_id', '=', payslip_id.id)], limit=1)

            target_code = 'BRUT' if rec.type_calcul == 'brut' else 'NET'
            target_amount = rec.montant

            while payslip_id.get_amountbycode(target_code, payslip_id.line_ids) != target_amount:
                current_amount = payslip_id.get_amountbycode(target_code, payslip_id.line_ids)
                adjustment = target_amount - current_amount if current_amount < target_amount else -(
                        current_amount - target_amount)
                payslip_input_rec.amount += adjustment
                contract.extra_pay += adjustment
                payslip_id.compute_sheet()

            payslip_id.state = 'draft'
            payslip_id.unlink()
