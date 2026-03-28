# -*- coding:utf-8 -*-


from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class CmuMonthly(models.Model):
    _name = "hr_payroll_custom.cmu_monthly"
    _description = "CMU Mensuelle"

    def compute_cmu_monthly(self):
        for rec in self:
            data = []
            rec.env.cr.execute(
                "SELECT employee_id FROM hr_payslip WHERE date_from >= %s AND date_to <= %s AND company_id = %s AND state IN ('validated','paid')",
                (rec.date_from, rec.date_to, rec.company_id.id))
            results = rec.env.cr.fetchall()
            if results:
                employee_ids = [x[0] for x in results]
                if employee_ids:
                    employees = rec.env['hr.employee'].search([('type', '!=', 'p'), ('id', 'in', employee_ids),
                                                               ('cmu_contributor','!=','do_not_contribute')
                                                                ], order='registration_number')
                    for emp in employees:
                        val = {
                            'cmu_monthly_id': rec.id,
                            'identification_cnps': emp.identification_cnps,
                            'identification_cmu': emp.identification_cmu,
                            'type': 't',
                            'name': emp.name,
                            'first_name': emp.first_name,
                            'birthday': emp.birthday,
                            'gender': emp.gender,
                            'num_cmu_beneficiary': emp.identification_cmu,
                            'name_beneficiary': emp.name,
                            'first_name_beneficiary': emp.first_name,
                            'birthday_beneficiary': emp.birthday,
                        }
                        data.append(val)
                        if emp.marital == 'married':
                            val = {
                                'cmu_monthly_id': rec.id,
                                'identification_cnps': emp.identification_cnps,
                                'identification_cmu': emp.identification_cmu,
                                'type': 'c',
                                'name': emp.name,
                                'first_name': emp.first_name,
                                'birthday': emp.birthday,
                                'gender': emp.gender_conjoint,
                                'num_cmu_beneficiary': emp.num_cmu_conjoint,
                                'name_beneficiary': emp.conjoint_name,
                                'first_name_beneficiary': emp.conjoint_first_name,
                                'birthday_beneficiary': emp.spouse_birthdate,

                            }
                            data.append(val)
                        if emp.childrens_ids:
                            for enf in emp.childrens_ids:
                                val = {
                                    'cmu_monthly_id': rec.id,
                                    'identification_cnps': emp.identification_cnps,
                                    'identification_cmu': emp.identification_cmu,
                                    'type': 'e',
                                    'name': emp.name,
                                    'first_name': emp.first_name,
                                    'birthday': emp.birthday,
                                    'gender': enf.gender,
                                    'num_cmu_beneficiary': enf.num_cmu,
                                    'name_beneficiary': enf.name,
                                    'first_name_beneficiary': enf.first_name,
                                    'birthday_beneficiary': enf.date_of_birth,

                                }
                                data.append(val)
            if data:
                rec.line_ids.unlink()
                rec.line_ids.create(data)
            return data

    name = fields.Char('Libellé')
    date_from = fields.Date('Date de début')
    date_to = fields.Date('Date de fin')
    amount  = fields.Integer('Montant à payer', compute='get_amount')
    total_workforce = fields.Integer('Effectif total', compute='get_amount')
    company_id = fields.Many2one('res.company', 'Compagnie', default=lambda self: self.env.user.company_id.id)
    line_ids = fields.One2many("hr_payroll_custom.cmu_monthly_line", "cmu_monthly_id", "Lignes")

    def get_amount(self):
        for rec in self:
            rec.total_workforce = len(rec.line_ids)
            rec.amount = rec.total_workforce * rec.company_id.cmu_amount

    def export_xls(self):
        for rec in self:
            #context = rec._context
            rec.ensure_one()
            datas = {'ids': rec.ids}
            datas['model'] = 'hr_payroll_custom.cmu_monthly'
            return rec.env.ref('hr_payroll_custom.action_cmu_monthly_xls').with_context(data=datas).report_action(rec, data=datas,
                                                                                           config=False)


class CmuMonthlyLine(models.Model):
    _name = "hr_payroll_custom.cmu_monthly_line"
    _description = "Ligne CMU mensuelle"

    identification_cnps = fields.Char("Numéro CNPS") #num_cnps
    identification_cmu = fields.Char("N° CMU assuré") #num_cmu
    type = fields.Selection([('t', 'T'), ('c', 'C'), ('e', 'E')], "Type bénéficiaire")
    name = fields.Char("Nom assuré")
    first_name = fields.Char("Prénoms assuré")
    birthday = fields.Date("Date de naissance assuré")
    gender = fields.Selection([('male', 'H'), ('female', 'F')], "Genre du bénéficiaire")
    cmu_monthly_id = fields.Many2one("hr_payroll_custom.cmu_monthly", "CMU", required=False)
    num_cmu_beneficiary = fields.Char("N° CMU Beneficiaire")
    name_beneficiary = fields.Char("Nom beneficiaire")
    first_name_beneficiary = fields.Char('Prenoms beneficiaire')
    birthday_beneficiary = fields.Date('Date de naissance beneficiaire')
