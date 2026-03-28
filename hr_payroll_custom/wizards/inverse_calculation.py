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
            version = self.env['hr.version'].browse(rec._context.get('active_id'))

            total_intrant = version.wage + sum(prime.amount for prime in version.fixed_premiums_ids)

            if total_intrant > rec.montant:
                raise ValidationError('Le montant est inférieur aux intrants')

            structure_salariale = version.structure_type_id.default_struct_id

            now = datetime.now()
            date_from = datetime(now.year, now.month, 1)
            date_to = date_from + relativedelta.relativedelta(months=1, days=-1)

            vals = {
                'name': _('Salary Slip of %s for %s') % (version.employee_id.name, 'Novembre 2023'),
                'employee_id': version.employee_id.id,
                'date_from': date_from,
                'date_to': date_to,
                'version_id': version.id,
                'struct_id': structure_salariale.id,
            }

            payslip_id = payslip_obj.create(vals)
            extra_pay_initial = version.extra_pay
            try:
                payslip_id._compute_input_line_ids()
                input_records_to_delete = {}
                for input_line in payslip_id.input_line_ids:
                    input_rec = self.env['hr.payslip.input'].search(
                        [('input_type_id', '=', input_line.input_type_id.id),
                         ('payslip_id', '=', input_line.payslip_id.id)], limit=2)

                    if len(input_rec) >= 2:
                        input_records_to_delete[input_rec[1].id] = True

                # Suppression des rubriques générées en doublon
                self.env['hr.payslip.input'].browse(list(input_records_to_delete.keys())).unlink()

                payslip_id.compute_sheet()

                payslip_input_rec = self.env['hr.payslip.input'].search(
                    [('code', '=', 'SURSA'), ('payslip_id', '=', payslip_id.id)], limit=1)

                target_code = 'BRUT' if rec.type_calcul == 'brut' else 'NET'
                target_amount = rec.montant

                MAX_ITERATIONS = 500
                iteration = 0
                while iteration < MAX_ITERATIONS:
                    current_amount = payslip_id.get_amountbycode(target_code, payslip_id.line_ids)
                    if abs(current_amount - target_amount) <= 1:
                        break
                    adjustment = target_amount - current_amount
                    payslip_input_rec.amount += adjustment
                    version.extra_pay += adjustment
                    payslip_id.compute_sheet()
                    iteration += 1

                if iteration >= MAX_ITERATIONS:
                    raise ValidationError(
                        _("Le calcul inverse n'a pas convergé après %d itérations. "
                          "Vérifiez le montant cible.") % MAX_ITERATIONS)
            except Exception:
                # Restaurer extra_pay en cas d'erreur
                version.extra_pay = extra_pay_initial
                payslip_id.unlink()
                raise

            payslip_id.unlink()
