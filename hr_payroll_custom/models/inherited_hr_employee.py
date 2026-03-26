
from odoo import fields, models, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    annual_leave_payment_date = fields.Date('Date de payement congé')
    leave_balance = fields.Float('Solde congé antérieur',
                                 help="Utilisé dans le calcul des allocations congés. Il permet l'intégration des "
                                      "données issues d'un autre système")
    days_worked_since_last_leave = fields.Integer("Jours travaillé depuis dernier congé", default=0,
                                                  help="Utilisé dans le calcul des allocations congés. Il permet de "
                                                       "l'intégration des données issues d'un autre système.")
    cmu_contributor = fields.Selection([('do_not_contribute', 'Ne cotise pas'),
                                        ('supported_fifty', 'Pris en charge 50%'),
                                        ('fully_supported', 'Pris en charge 100%')], "Contribution CMU",
                                       default='supported_fifty',
                                       help="Ne cotise pas: Conseillé pour les fonctionnaires de l'entreprise\n"
                                            "Pris en charge 50%: Appliqué par la législation en vigueur \n"
                                            "Pris en charge 100%: Appliqué s'il a été convenu avec la société de "
                                            "supporter la totalité de la cotisaion.")

    def getTotalRubriqueByPeriod(self, code, date_from, date_to):
        amount = 0
        payslips = self.slip_ids.filtered(lambda slip: slip.date_from >= date_from and slip.date_to <= date_to)
        if payslips:
            p_lines = self.env['hr.payslip.line'].search([('code', '=', code), ('slip_id', 'in', payslips.ids)])
            if p_lines:
                amount = sum([line.total for line in p_lines])
        return amount

    def getBaseATPF(self, code, date_from, date_to):
        """
        This function determines the basis for calculating the work accident and family benefit for each month and
        cumulates over the year.
        :param code:
        :param date_from:
        :param date_to:
        :return amount:
        """
        amount = 0
        max_other_tax_base = self.company_id.max_other_tax_base
        payslips = self.slip_ids.filtered(lambda slip: slip.date_from >= date_from and slip.date_to <= date_to)
        if payslips:
            p_lines = self.env['hr.payslip.line'].search([('code', '=', code), ('slip_id', 'in', payslips.ids)])
            if p_lines:
                amount = sum([min(line.amount, max_other_tax_base) for line in p_lines])
        return amount

    def getAmountRubriqueByPeriod(self, code, date_from, date_to):
        amount = 0
        payslips = self.slip_ids.filtered(lambda slip: slip.date_from >= date_from and slip.date_to <= date_to)
        if payslips:
            p_lines = self.env['hr.payslip.line'].search([('code', '=', code), ('slip_id', 'in', payslips.ids)])
            if p_lines:
                amount = sum([line.amount for line in p_lines])
        return amount


class HrEmployeeCategory(models.Model):
    _name = 'hr_payroll_custom.employee_category'
    _description = "Gestion des cetegories d'employee"
    _order = 'sequence'

    name = fields.Char('Désignation')
    code = fields.Char('Code', size=2)
    sequence = fields.Integer('Séquence')
    description = fields.Text('Description')

class HrDepartureReason(models.Model):
    _inherit = 'hr.departure.reason'

    indemnity = fields.Boolean('Indemnité à calculer', default=False,
                               help="Utilisé pour la détermination des indemnités lors du calcul du solde de "
                                    "tout compte")