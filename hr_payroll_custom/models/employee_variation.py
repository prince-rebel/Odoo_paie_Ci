# -*- coding:utf-8 -*-

from odoo import api, fields, _, models, tools
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import babel
import logging

_logger = logging.getLogger(__name__)

Type_variation = [('in', 'Entrée'), ('out', 'Sortie')]


class EmployeeVariation(models.Model):
    _name = 'hr_payroll_custom.employee_variation'
    _description = "Variation des effectifs payés"

    @api.depends('date_from')
    def get_employee_variation_name(self):
        for rec in self:
            rec.name = "Variation des effectifs "
            locale = rec.env.context.get('lang') or 'en_US'
            if rec.date_from:
                date_from = str(fields.Date.from_string(rec.date_from) + relativedelta(day=1, months=-1))
                date_to = str(fields.Date.from_string(rec.date_from) + relativedelta(days=-1))
                rec.old_date_from = date_from
                rec.old_date_to = date_to
                rec.name = str(f"Variation des effectifs de "
                               f"{tools.ustr(babel.dates.format_date(date=rec.old_date_from, format='MMMM-y', locale=locale))} à "
                               f"{tools.ustr(babel.dates.format_date(date=rec.date_from, format='MMMM-y', locale=locale))}")

    name = fields.Char("Libellé", default="Variation des effectifs")
    date_from = fields.Date(string='Début (en cours)', help="Date de Début du mois en cours")
    date_to = fields.Date(string='Fin (en cours)', help="Date de fin du mois en cours")
    old_date_from = fields.Date(string='Début (antérieur)', compute="get_employee_variation_name", store=True,
                                help="Date de Début du mois antérieur")
    old_date_to = fields.Date(string='Fin (antérieur)', compute="get_employee_variation_name", store=True,
                              help="Date de fin du mois antérieur")
    company_id = fields.Many2one("res.company", "Société", default=lambda self: self.env.user.company_id.id)
    total_previous_employees = fields.Integer("Total effectif payé mois précedent")
    employees_out = fields.Integer("Employés sortis")
    employees_in = fields.Integer("Employés entrés")
    total_current_employees = fields.Integer("Total effectif payé mois en cours")
    employee_ids = fields.One2many("hr_payroll_custom.employee_variation_line", "emp_variation_id",
                                   "Liste des employés Entrées/sorties")

    def getEmployeesByPeriode(self, date_from, date_to):
        select_query = """
                SELECT DISTINCT
                    employee_id
                FROM 
                    hr_payslip 
                WHERE 
                    date_from >= %(date_from)s AND date_to <= %(date_to)s AND company_id = %(company_id)s
                """

        params_query = {
            'date_from': date_from,
            'date_to': date_to,
            'company_id': self.company_id.id
        }
        self.env.cr.execute(select_query, params_query)
        slip_ids = [x[0] for x in self.env.cr.fetchall()]
        return slip_ids

    def getLines(self, emp_ids, emp_variation_id, type):
        res = []
        if emp_ids:
            for emp_id in emp_ids:
                val = {
                    'employee_id': emp_id,
                    'emp_variation_id': emp_variation_id,
                    'type': type,
                }
                res.append(val)
        return res

    def action_compute(self):
        for rec in self:
            rec.employee_ids.unlink()
            employees = rec.getEmployeesByPeriode(rec.date_from, rec.date_to)
            rec.total_current_employees = len(employees)
            old_employes = rec.getEmployeesByPeriode(rec.old_date_from, rec.old_date_to)
            rec.total_previous_employees = len(old_employes)
            emp_out = [item for item in old_employes if item not in employees]
            emp_in = [item for item in employees if item not in old_employes]
            rec.employees_out = len(emp_out)
            rec.employees_in = len(emp_in)
            emp_variation_id = rec.id
            empl_ids = rec.getLines(emp_in, emp_variation_id, 'in') + rec.getLines(emp_out, emp_variation_id, 'out')
            for emp in empl_ids:
                emp['emp_variation_id'] = rec.id
            rec.employee_ids.create(empl_ids)
            rec.get_reason_entry_or_exit()
            return True

    def get_reason_entry_or_exit(self):
        for rec in self:
            if rec.employee_ids:
                first_day_last_month = fields.Date.from_string(rec.date_to) + relativedelta(months=-2, days=+1)
                last_four_months = fields.Date.from_string(rec.date_to) + relativedelta(months=-5, days=+1)
                for emp in rec.employee_ids:
                    if emp.type == 'in':
                        # vérifier la date d'embauche
                        # si date d'embauche est comprise entre le 1er du mois précédent et la fin du mois encours, mettre nouvel embauche
                        # Si la date de payement du congé est compris entre les 4 mois précédent de la fin du mois en cours, mettre retour congé

                        if emp.employee_id.hiring_date and first_day_last_month <= emp.employee_id.hiring_date < rec.date_to:
                            emp.observation = 'NOUVEL AGENT'
                        elif emp.employee_id.date_return_last_holidays and last_four_months <= emp.employee_id.date_return_last_holidays < rec.date_to:
                            emp.observation = 'RETOUR CONGE'
                        else:
                            pass
                    elif emp.type == 'out':
                        # Si la date de départ est renseigné, alors prend le motif de départ
                        # Si la date de payement du congé est compris entre les 9 mois précédent de la fin du mois en cours, mettre congé payé
                        if emp.employee_id.departure_date:
                            emp.observation = emp.employee_id.departure_reason_id.name
                        elif emp.employee_id.date_return_last_holidays and last_four_months <= emp.employee_id.date_return_last_holidays < rec.date_to:
                            emp.observation = 'CONGE DE MATERNITE'
                    else:
                        raise ValidationError(
                            _(f"Nous ne sommes pas en mesure de donner la situation de l'employé {emp.employee_id.identification_id}/"
                              f"{emp.employee_id.name} {emp.employee_id.first_name}. Merci de vérifier sa date d'embauche et la date "
                              f"retour du dernier congé"))
            else:
                pass


class ReportEmployeeAbsentPreviousPay(models.AbstractModel):
    _name = 'report.hr_payroll_custom.report_absent_prev_pay'
    _description = 'Salarié absent de la précédente paye'

    def _get_report_values(self, docids, data=None):
        docs = self.env['hr_payroll_custom.employee_variation'].browse(docids)
        if docs:
            locale = self.env.context.get('lang') or 'en_US'
            date_from = tools.ustr(
                babel.dates.format_date(date=docs.date_from, format='MMMM y', locale=locale))
            return {
                'doc_ids': docs.ids,
                'doc_model': 'hr_payroll_custom.employee_variation',
                'docs': docs,
                'date_from': date_from
            }

        else:
            raise ValidationError(_("Impossible de générer le rapport. Merci de contacter un administrateur"))


class ChangeInPaidStaff(models.AbstractModel):
    _name = 'report.hr_payroll_custom.report_change_in_paid_staffs'
    _description = "Analyse des variations de l'effectif payé"

    def _get_report_values(self, docids, data=None):
        docs = self.env['hr_payroll_custom.employee_variation'].browse(docids)
        if docs:
            locale = self.env.context.get('lang') or 'en_US'
            date_from = tools.ustr(
                babel.dates.format_date(date=docs.date_from, format='MMMM y', locale=locale))
            return {
                'doc_ids': docs.ids,
                'doc_model': 'hr_payroll_custom.employee_variation',
                'docs': docs,
                'date_from': date_from
            }

        else:
            raise ValidationError(_("Impossible de générer le rapport. Merci de contacter un administrateur"))


class HrSalaryEmployeeVariationLine(models.Model):
    _name = 'hr_payroll_custom.employee_variation_line'
    _description = "Ligne des variations des effectifs payés"

    name = fields.Char("NOM & PRENOMS", compute="get_employee_name", store=True)
    identification_id = fields.Char("MATRICULE", related="employee_id.identification_id")
    type = fields.Selection(Type_variation, "Type")
    observation = fields.Text("Observation")
    employee_id = fields.Many2one("hr.employee", "Employé")
    emp_variation_id = fields.Many2one("hr_payroll_custom.employee_variation", "Variation")

    @api.depends('employee_id')
    def get_employee_name(self):
        for rec in self:
            if rec.employee_id:
                rec.name = rec.employee_id.name + ' ' + rec.employee_id.first_name
            else:
                rec.name = "Indéfinie"
