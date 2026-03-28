from odoo import fields, models, api, _
from dateutil import relativedelta
from odoo.exceptions import ValidationError
from math import ceil
import logging
from datetime import date

_logger = logging.getLogger(__name__)


def get_marital_status_translate(marital):
    if marital == 'single':
        return 'Célibataire'
    elif marital == 'married':
        return 'Marié(e)'
    elif marital == 'cohabitant':
        return 'Cohabitant légal'
    elif marital == 'widower':
        return 'Veuf(ve)'
    elif marital == 'divorced':
        return 'Divorcé(e)'
    else:
        return "Indéfini"


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends("line_ids")
    def _get_basic_element(self):
        for slip in self:
            base_daily = slip.line_ids.filtered(lambda l: l.code == 'BASE_J')
            gross_taxable = slip.line_ids.filtered(lambda l: l.code == 'BRUT')
            total_gross = slip.line_ids.filtered(lambda l: l.code == 'BRUT_TOTAL')
            slip.base_daily = base_daily.total if base_daily else 0.0
            slip.gross_taxable = gross_taxable.total if gross_taxable else 0.0
            slip.total_gross = total_gross.total if total_gross else 0.0

    @api.depends('version_id')
    def _get_anciennete(self):
        for slip in self:
            start_date = slip.employee_id.hiring_date or (slip.version_id.date_start if slip.version_id else None)
            if not start_date or not slip.date_to:
                slip.update({'slip_seniority_year': 0, 'slip_seniority_month': 0})
                continue
            # En Odoo 19, date_to est un champ Date — pas besoin de from_string()
            end_date = slip.date_to
            tmp = relativedelta.relativedelta(end_date, start_date)
            slip.update({
                'slip_seniority_year': tmp.years,
                'slip_seniority_month': tmp.months,
            })
    mois_travailles = fields.Integer(string="Nombre de mois travaillés",compute="_compute_mois_travailles",store=True)
    slip_seniority_year = fields.Integer("Nombre d'année", compute=_get_anciennete)  # payslip_an_anciennete
    slip_seniority_month = fields.Integer("Nombre de mois (Ancienneté)",
                                          compute=_get_anciennete)  # payslip_mois_anciennete
    base_daily = fields.Float("Base journalière", compute="_get_basic_element", default=0.0, store=True)
    gross_taxable = fields.Float("Brut imposable", compute="_get_basic_element", default=0.0, store=True)
    total_gross = fields.Float("Brut Total", compute="_get_basic_element", default=0.0, store=True)
    acquired_leave_month = fields.Float('Congés acquis mensuel', compute='get_leave_of_month')
    taked_leave_month = fields.Float('Congés pris mensuel', compute='get_leave_of_month')
    acquired_leave = fields.Float('Congés acquis', compute='get_leave_of_month')
    taked_leave = fields.Float('Congés pris', compute='get_leave_of_month')
    available_leave = fields.Float('Congés disponible', compute='get_leave_of_month')
    days_since_last_leave = fields.Integer('Jours depuis dernier congé', compute='get_cumul_holiday')
    gross_salary_leave = fields.Integer('Brut congé', compute='get_cumul_holiday')
    number_days_off = fields.Integer('Nombre de jour de congé', compute='get_number_days_off', store=True)
    igr_part = fields.Float('IGR')
    marital_status = fields.Selection([
        ('single', 'Célibataire'),
        ('married', 'Marié(e)'),
        ('cohabitant', 'Cohabitant légal'),
        ('widower', 'Veuf(ve)'),
        ('divorced', 'Divorcé(e)')], string='Marital Status')
    print_logo = fields.Boolean('Imprimer le logo', default=True,
                                help="Affiche le logo sur le bulletin de paye. Il est fonction du type de papier que "
                                     "vous utiliserez pour les bulletins. S'il s'agit d'un papier entête ou non")
    

    @api.depends('employee_id', 'date_from')
    def _compute_mois_travailles(self):
        for slip in self:
            # Date d'embauche
            hiring_date = slip.employee_id.hiring_date
            if not hiring_date:
                slip.mois_travailles = 0
                continue

            # Date du bulletin (fin du mois du bulletin) — date_from est un champ Date en Odoo 19
            bulletin_date = slip.date_from
            annee_bulletin = bulletin_date.year
            mois_bulletin = bulletin_date.month

            # Nombre de mois travaillés dans l'année
            if hiring_date.year > annee_bulletin or \
               (hiring_date.year == annee_bulletin and hiring_date.month > mois_bulletin):
                slip.mois_travailles = 0
            elif hiring_date.year == annee_bulletin:
                slip.mois_travailles = mois_bulletin - hiring_date.month + 1
            else:
                slip.mois_travailles = mois_bulletin
                
    @api.depends('employee_id', 'version_id', 'struct_id', 'date_from', 'date_to')
    def _compute_input_line_ids(self):
        for slip in self:
            record = super(HrPayslip, self)._compute_input_line_ids()
            if slip.version_id and slip.version_id.fixed_premiums_ids and slip.employee_id and slip.struct_id:
                res = slip.input_line_ids.browse([])
                payroll_input = []
                for line in slip.input_line_ids:
                    res += line
                slip.input_line_ids = False
                bonus_legal = slip.employee_id.company_id.bonus_transport
                for fixed_premium in slip.version_id.fixed_premiums_ids:

                    if fixed_premium.input_type_id.code == 'TRSP' and fixed_premium.amount > bonus_legal:
                        vals = {
                            'name': fixed_premium.input_type_id.name,
                            'amount': bonus_legal,
                            'input_type_id': fixed_premium.input_type_id.id
                        }
                        payroll_input.append(vals)

                        input_type_rec = self.env['hr.payslip.input.type'].search([('code', '=', 'TRSP_IMP')], limit=1)
                        if not input_type_rec:
                            raise ValidationError(
                                _("Vous devez définir la prime de transport imposable avec le code 'TRSP_IMP' dans "
                                  "les autres entrées. Merci de contacter un administratreur si vous n'avez pas la "
                                  "possibilité de le faire."))
                        vals = {
                            'name': input_type_rec.name,
                            'amount': fixed_premium.amount - bonus_legal,
                            'input_type_id': input_type_rec.id
                        }
                        payroll_input.append(vals)
                        continue

                    vals = {
                        'name': fixed_premium.input_type_id.name,
                        'amount': fixed_premium.amount,
                        'input_type_id': fixed_premium.input_type_id.id
                    }

                    payroll_input.append(vals)

                # Récupérer les salaires categories et le sursalaire
                input_contract = ['BASE', 'SURSA']
                for rubric in input_contract:
                    input_type_rec = self.env['hr.payslip.input.type'].search([('code', '=', rubric)], limit=1)
                    if not input_type_rec:
                        raise ValidationError(
                            _(f"Les Types d'entrée salaire de base ou sursalaire ne sont pas définis. Merci de faire "
                              f"le nécessaire ou de contacter un administrateur"))
                    vals_category_salary = {
                        'name': input_type_rec.name,
                        'amount': slip.version_id.wage if rubric == 'BASE' else slip.version_id.extra_pay,
                        'input_type_id': input_type_rec.id
                    }
                    payroll_input.append(vals_category_salary)

                for dico in payroll_input:
                    res += res.new(dico)
                slip.input_line_ids = res
            else:
                slip.input_line_ids = False

            return record

    def getDatabyCode(self, code, line_ids, field_name):
        amount = 0
        if line_ids and field_name in ('rate', 'amount', 'quantity', 'total'):
            for line in line_ids:
                if line.code == code:
                    if field_name == 'rate':
                        return line.rate
                    if field_name == 'amount':
                        return line.amount
                    if field_name == 'quantity':
                        return line.quantity
                    if field_name == 'total':
                        return line.total
        return amount

    def getCumulDataByCode(self, employee_id, code, date_from, date_to, field_name):
        payslips = self.env['hr.payslip'].search([('date_from', '>=', date_from), ('date_to', '<=', date_to),
                                                  ('employee_id', '=', employee_id)])
        cumul_amount = 0
        for payslip in payslips:
            cumul_amount += payslip.getDatabyCode(code, payslip.line_ids, field_name)
        return cumul_amount

    def set_personnal_data(self):
        self.write(
            {'igr_part': self.employee_id.part_igr,
             'marital_status': self.employee_id.marital,
             })

    def action_payslip_done(self):
        record = super(HrPayslip, self).action_payslip_done()
        self.set_personnal_data()
        return record

    def get_personnal_info(self):
        data = []
        for rec in self:
            if rec.employee_id.type == 'p':
                employee_type = 'Num. CGRAE'
                matricule = rec.employee_id.num_cgare
            else:
                employee_type = 'Num. CNPS'
                matricule = rec.employee_id.identification_cnps

            if rec.state in ('validated', 'paid'):
                marital_status = get_marital_status_translate(rec.marital_status)
                igr_part = rec.igr_part
            else:
                marital_status = get_marital_status_translate(rec.employee_id.marital)
                igr_part = rec.employee_id.part_igr

            vals_dp = {
                'identification_id': rec.employee_id.identification_id,
                'categorie_salariale': rec.version_id.salary_category_id.name if rec.version_id else '',
                'employee_name': (rec.employee_id.name or '') + ' ' + (rec.employee_id.first_name or ''),
                'igr_part': igr_part,
                'zip': rec.employee_id.address_id.zip,
                'nationality': rec.employee_id.country_id.nationality if rec.employee_id.country_id else '',
                'birthday': rec.employee_id.birthday.strftime("%d/%m/%Y") if rec.employee_id.birthday else '',
                'marital_status': marital_status,
                'hiring_date': (lambda d: d.strftime("%d/%m/%Y") if d else '')(rec.employee_id.hiring_date or (rec.version_id.date_start if rec.version_id else None)),
                'slip_seniority_year': rec.slip_seniority_year if rec.slip_seniority_year != 0 else 0,
                'slip_seniority_month': rec.slip_seniority_month if rec.slip_seniority_month != 0 else 0,
                'department': rec.employee_id.department_id.name,
                'employee_type': employee_type,
                'matricule': matricule,
                'job': rec.employee_id.job_id.name,
                'mois_travailles': rec.mois_travailles,
            }
            data.append(vals_dp)
        return data

    def get_amount_rubrique(self, rubrique):
        line_ids = self.line_ids
        total = 0
        for line in line_ids:
            if line.code == rubrique:
                total = line.total
        # result = format_amount.manageSeparator(total)
        return total

    def get_gross_data(self):
        """
        Function allowing to return the constituent elements of the gross salary
        """
        data = []
        for rec in self:
            for line in rec.line_ids.filtered(
                    lambda l: l.appears_on_payslip and 100 <= l.sequence < 300 and l.amount != 0):
                if line.code in ('HS15', 'HS50', 'HS75', 'HS100'):
                    quantity = line.quantity
                elif line.code == 'PANC':
                    quantity = rec.slip_seniority_year
                elif line.code in ('CONG', 'CNGP'):
                    quantity = int(rec.number_days_off)
                elif line.code == 'RQ_CONG':
                    quantity = int(rec.number_remaining_days_leave)
                elif line.code == 'GRATIF' or line.code == 'P_13M':
                    quantity = int(rec.jfisc)
                else:
                    quantity = rec.get_amount_rubrique('WORK100')

                vals_gd = {
                    'sequence': line.sequence,
                    'name': line.name,
                    'quantity': int(quantity),
                    'amount': '{0:,.0f}'.format(round(line.amount)).replace(',', ' '),
                    'total': '{0:,.0f}'.format(round(line.total)).replace(',', ' '),
                }
                data.append(vals_gd)
        return data

    def get_gross(self):
        """
        Function to return the gross salary
        """
        data = []
        for rec in self:
            gross_line = self.env['hr.payslip.line'].search([('slip_id', '=', rec.id), ('code', '=', 'BRUT')], limit=1)
            vals_gross = {
                'total': '{0:,.0f}'.format(round(gross_line.total)).replace(',', ' '),
            }
            data.append(vals_gross)
        return data
    
    def is_employer_only_code(self, code):
        return 'DCEMP' in code


    def get_tax_data(self):
        """
        function that returns taxes
        """
        data = []
        for rec in self:
            for line in rec.line_ids.filtered(
                    lambda td: td.appears_on_payslip and 400 <= td.sequence <= 410 and td.amount != 0):
                rate_employer = ''
                total_employer = ''
                if line.amount_select == 'percentage' and line.code not in ('ACT', 'PF', 'TAXEAP', 'TAXEFP'):
                    rate_employee = '{0:,.2f}'.format(line.rate).replace('.', ',')
                else:
                    rate_employee = ''

                if line.code not in ('ACT', 'PF', 'TAXEAP', 'TAXEFP'):
                    total_employee = '{0:,.0f}'.format(round(line.total)).replace(',', ' ')
                else:
                    total_employee = ''

                if line.code == 'ITS':
                    # ITS_P est calculé après BRUT_TOTAL (seq 702), accessible via get_amount_rubrique
                    its_p = rec.get_amount_rubrique('ITS_P')
                    rate_employer = '1,20' if its_p else ''
                    total_employer = '{0:,.0f}'.format(round(its_p)).replace(',', ' ') if its_p else ''
                elif line.code == 'CNPS':
                    rate_employer = rec.getTauxByCode('CNPS_P')
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('CNPS_P'))).replace(',', ' ')
                elif line.code == 'CGRAE_E':
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('CGRAE_P'))).replace(',', ' ')
                elif line.code == 'RGL_CGRAE_E':
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('REG_CGRAE_P'))).replace(',', ' ')
                elif line.code in ('ACT', 'PF', 'TAXEAP', 'TAXEFP'):
                    rate_employer = rec.getTauxByCode(line.code)
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique(line.code))).replace(',', ' ')
                elif line.code == 'DLR':
                    rate_employee = ''
                    total_employee = ''
                    rate_employer = rec.getTauxByCode('DLR')
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('DLR'))).replace(',', ' ')

                else:
                    pass

                # Pour ITS : la colonne Base affiche le brut imposable (BRUT_TOTAL), pas le montant ITS
                if line.code == 'ITS':
                    amount_display = '{0:,.0f}'.format(round(rec.get_amount_rubrique('BRUT_TOTAL'))).replace(',', ' ')
                else:
                    amount_display = '{0:,.0f}'.format(round(line.amount)).replace(',', ' ')

                vals_td = {
                    'sequence': line.sequence,
                    'name': line.name,
                    'amount': amount_display,
                    'rate_employee': rate_employee,
                    'total_employee': total_employee,
                    'rate_employer': rate_employer,
                    'total_employer': total_employer,
                }
                data.append(vals_td)
        return data

    def get_total_tax(self):
        """
        function that returns the accumulated taxes
        """
        data = []
        for rec in self:
            vals_tt = {
                'total_employee': '{0:,.0f}'.format(int(rec.get_amount_rubrique('RET'))).replace(',', ' '),
                'total_employer': '{0:,.0f}'.format(int(rec.get_amount_rubrique('TTL_IMP_PART'))).replace(',', ' ')
            }
            data.append(vals_tt)
        return data

    def get_various_deductions(self):
        """
        function that returns miscellaneous deductions
        """
        data = []
        for rec in self:
            for line in rec.line_ids.filtered(
                    lambda vd: vd.appears_on_payslip and 412 < vd.sequence <= 498 and vd.amount != 0):
                sequence = line.sequence
                name = line.name
                amount = '{0:,.0f}'.format(round(line.amount)).replace(',', ' ')
                if line.employee_id.cmu_contributor == 'do_not_contribute' and line.code == 'CMU':
                    sequence = ''
                    name = ''
                    amount = ''
                elif line.code == 'CMU' and line.employee_id.cmu_contributor == 'fully_supported':
                    amount = '{0:,.0f}'.format(int(rec.get_amount_rubrique('CMU_P') / 2)).replace(',', ' ')
                else:
                    pass
                if line.amount_select == 'percentage' and line.code not in ('ACT', 'PF', 'TAXEAP', 'TAXEFP'):
                    rate_employee = line.rate
                else:
                    rate_employee = ''
                if line.code not in ('ACT', 'PF', 'TAXEAP', 'TAXEFP'):
                    total_employee = '{0:,.0f}'.format(round(line.total)).replace(',', ' ')
                else:
                    total_employee = ''

                if line.code in ('ACT', 'PF', 'TAXEAP', 'TAXEFP'):
                    rate_employer = rec.getTauxByCode(line.code)
                else:
                    rate_employer = ''

                if line.code == 'CMU' and line.employee_id.cmu_contributor != 'do_not_contribute':
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('CMU_P'))).replace(',', ' ')
                elif line.code == 'AJ_CMU':
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('AJ_CMU_P'))).replace(',', ' ')
                elif line.code == 'CRRAE_E':
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('CRRAE_PART'))).replace(',', ' ')
                elif line.code == 'C_FAAM_E':
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('CRRAE_FAAM_P'))).replace(',', ' ')
                elif line.code == 'REG_C_FAAM_E':
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('REG_CRRAE_FAAM_P'))).replace(',',
                                                                                                                   ' ')
                elif line.code == 'REG_CRRAE_E':
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique('REG_CRRAE_PART'))).replace(',',
                                                                                                                 ' ')
                elif line.code in ('ACT', 'PF', 'TAXEAP', 'TAXEFP'):
                    total_employer = '{0:,.0f}'.format(round(rec.get_amount_rubrique(line.code))).replace(',', ' ')
                else:
                    total_employer = ''

                vals_vd = {
                    'sequence': sequence,
                    'name': name,
                    'amount': amount,
                    'rate_employee': rate_employee,
                    'total_employee': total_employee,
                    'rate_employer': rate_employer,
                    'total_employer': total_employer
                }
                data.append(vals_vd)
        return data

    def get_total_various_deduction(self):
        """
        function that returns the total of miscellaneous deductions
        """
        data = []
        for rec in self:
            vals_tvd = {
                'total_employee': '{0:,.0f}'.format(int(rec.get_amount_rubrique('RET_DIV'))).replace(',', ' '),
                'total_employer': '{0:,.0f}'.format(int(rec.get_amount_rubrique('TTL_COT_PART'))).replace(',', ' ')
            }
            data.append(vals_tvd)
        return data

    def get_tax_free_allowance(self):
        data = []
        for rec in self:
            for line in rec.line_ids.filtered(
                    lambda tfa: tfa.appears_on_payslip and 500 < tfa.sequence <= 599 and tfa.amount != 0):
                vals_tfa = {
                    'sequence': line.sequence,
                    'name': line.name,
                    'amount': '{0:,.0f}'.format(round(line.amount)).replace(',', ' '),
                    'total': '{0:,.0f}'.format(int(line.total)).replace(',', ' ')
                }
                data.append(vals_tfa)
        return data

    def get_tax_free_withholding(self):
        data = []
        for rec in self:
            for line in rec.line_ids.filtered(
                    lambda tfw: tfw.appears_on_payslip and 700 < tfw.sequence <= 799 and tfw.amount != 0):
                vals_tfw = {
                    'sequence': line.sequence,
                    'name': line.name,
                    'amount': '{0:,.0f}'.format(round(line.amount)).replace(',', ' '),
                    'total': '{0:,.0f}'.format(int(line.total)).replace(',', ' ')
                }
                data.append(vals_tfw)
        return data

    def get_leave_of_month(self):
        """
        donnees du mois encours
        """
        for slip in self:
            month_date_from = slip.date_from
            month_date_to = slip.date_to
            slip.acquired_leave_month = slip.get_allocation(slip.employee_id, month_date_from, month_date_to)
            slip.taked_leave_month = slip.get_leave(slip.employee_id, month_date_from, month_date_to)

            """
            donnees cumulees
            """
            # En Odoo 19, date_from est un champ Date — pas besoin de from_string()
            date_temp = slip.date_from
            first_day = date_temp.replace(month=1, day=1)
            date_begin = slip.employee_id.annual_leave_payment_date if slip.employee_id.annual_leave_payment_date and \
                                                                       slip.employee_id.annual_leave_payment_date < \
                                                                       first_day else first_day
            if date_begin < month_date_to:
                cumul_date_from = date_begin
                cumul_date_to = month_date_to
            else:
                cumul_date_from = month_date_to
                cumul_date_to = date_begin

            slip.acquired_leave = slip.get_allocation(slip.employee_id, cumul_date_from, cumul_date_to)
            slip.taked_leave = slip.get_leave(slip.employee_id, cumul_date_from, cumul_date_to)
            slip.available_leave = slip.acquired_leave - slip.taked_leave

    def get_allocation(self, employee, date_from, date_to):
        acquired_leaves = self.env['hr.leave.allocation'].search([('employee_id', '=', employee.id),
                                                                  ('number_of_days', '>', 0),
                                                                  ('create_date', '>=', date_from),
                                                                  ('create_date', '<=', date_to)])
        total_number_of_days_acquired = 0
        for acquired_leave in acquired_leaves:
            total_number_of_days_acquired += acquired_leave.number_of_days
        return total_number_of_days_acquired

    def get_leave(self, employee, date_from, date_to):
        leaves_taken = self.env['hr.leave'].search([('employee_id', '=', employee.id),
                                                    ('holiday_status_id.code', '=', 'CONG'),
                                                    ('request_date_from', '>=', date_from),
                                                    ('request_date_to', '<=', date_to)])
        total_number_of_days_taked = 0
        for leave_taken in leaves_taken:
            total_number_of_days_taked += leave_taken.number_of_days
        return total_number_of_days_taked

    def get_amount_natural_advantage(self):
        total = 0
        for line in self.line_ids:
            if line.salary_rule_id.natural_advantage:
                total += line.total
        return total

    def get_sum_rubrique(self, code):
        annee = self.date_to.year
        for payslip in self:
            cpt = 0
            for line in self.line_ids:
                if line.salary_rule_id.code == code and self.date_to >= self.date_to and payslip.date_to.year == annee:
                    cpt += line.total
            result = cpt
            return result

    def get_somme_natural_advantage(self):
        annee = self.date_to.year
        result = 0
        for payslip in self:
            if payslip.date_to.year == annee:
                for line in self.line_ids:
                    if line.salary_rule_id.natural_advantage:
                        result += line.total
        return result

    def get_cumul_holiday(self):
        """
        determiner  le nombre de jours travaillé depuis dernier congé
        """
        # date_temp = fields.Datetime.from_string(self.date_from)
        for rec in self:
            system_implementation_date = rec.company_id.system_implementation_date
            #
            if not system_implementation_date:
                raise ValidationError(_("Vous devez définir la date de mise en service du systeme pour un meilleur "
                                        "fonctionnement. Elle se trouve dans les paramètres de la société."))
            date_payment_last_holiday = rec.employee_id.annual_leave_payment_date \
                if rec.employee_id.annual_leave_payment_date else rec.employee_id.hiring_date
            if not date_payment_last_holiday:
                raise ValidationError(
                    _(f"Vous devez définir la date d'embauche de l'employé {rec.employee_id.identification_id} / "
                      f"{rec.employee_id.name or ''} {rec.employee_id.first_name or ''}"))
            if date_payment_last_holiday <= system_implementation_date:
                days_since_last_leave = rec.employee_id.days_worked_since_last_leave
                days_since_last_leave += rec.cumulBYCode(rec.employee_id.id, 'WORK100', system_implementation_date,
                                                         rec.date_to)
            else:
                days_since_last_leave = rec.cumulBYCode(rec.employee_id.id, 'WORK100', date_payment_last_holiday,
                                                        rec.date_to)

            rec.days_since_last_leave = days_since_last_leave

            """
            Faire le cumul des bruts depuis dernier congé
            """
            if date_payment_last_holiday < system_implementation_date:
                rec.gross_salary_leave = rec.cumulBYCode(rec.employee_id.id, 'BRUT', system_implementation_date,
                                                         rec.date_to) + rec.employee_id.leave_balance
            else:
                rec.gross_salary_leave = rec.cumulBYCode(rec.employee_id.id, 'BRUT', date_payment_last_holiday,
                                                         rec.date_to)

    def get_amountbycode(self, code, line_ids):
        # line_obj = self.env['hr.payslip.line']
        amount = 0
        if line_ids:
            for line in line_ids:
                if line.code == code:
                    return line.total
        return 0

    # def getDatabyCode(self, code, line_ids, field_name):
    #     amount = 0
    #     if line_ids and field_name in ('rate', 'amount', 'quantity'):
    #         for line in line_ids:
    #             if line.code == code:
    #                 if field_name == 'rate':
    #                     return line.rate
    #                 if field_name == 'amount':
    #                     return line.amount
    #                 if field_name == 'quantity':
    #                     return line.quantity
    #     return amount

    def cumulBYCode(self, employee_id, code, date_from, date_to):
        slip_obj = self.env['hr.payslip']
        payslips = slip_obj.search([('date_from', '>=', date_from), ('date_to', '<=', date_to),
                                    ('employee_id', '=', employee_id)])
        total_amount = 0
        for slip in payslips:
            result = slip.get_amountbycode(code, slip.line_ids)
            total_amount += result
        return total_amount

    def compute_leave_amount(self, id_employee, number_days_off):
        """
        Function calculating the amount of paid leaves according to the "last 12 months" method
        :param id_employee: id of employee
        :param number_days_off: number of validated days of leave
        :return: amount
        """
        # 1- determiner la periode de reference
        employee_rc = self.env['hr.employee'].search([('id', '=', id_employee)], limit=1)
        system_implementation_date = employee_rc.company_id.system_implementation_date
        last_leave_payment_date = employee_rc.annual_leave_payment_date
        hiring_date = employee_rc.hiring_date
        gross_previous_leave = 0
        date_begin = False
        if not system_implementation_date:
            raise ValidationError(
                _("La date de mise en service de l'application doit être définie dans les paramètres de "
                  "la société"))
        if last_leave_payment_date:
            if last_leave_payment_date <= system_implementation_date:
                date_begin = last_leave_payment_date
                gross_previous_leave = employee_rc.leave_balance
            else:
                date_begin = last_leave_payment_date

        elif hiring_date and hiring_date <= system_implementation_date:
            date_begin = hiring_date
            gross_previous_leave = employee_rc.leave_balance
        elif hiring_date and hiring_date > system_implementation_date:
            date_begin = hiring_date
        else:
            pass

        today = self.date_to
        if date_begin:
            reference_months = relativedelta.relativedelta(today, date_begin) if today > date_begin \
                else relativedelta.relativedelta(date_begin, today)
        else:
            raise ValidationError(
                _("Une erreur a été rencontrée. Merci de vérifier que la date de payement du dernier congé ou"
                  " la date d'embauche a été définie"))

        # 2- rechercher les règles faisant partie du calcul de l'allocation congés-payés
        payslip = self.env['hr.payslip']
        rules = self.env['hr.salary.rule'].search([('use_to_compute_leave', '=', True)])
        # 3- recuperer pour chaque bulletin les éléments faisant partie du calcul (salaire de base, sursalaire...)
        # et faire le cumul
        cumulative_wages = 0
        if rules:
            for rule in rules:
                cumulative_wages += payslip.cumulBYCode(id_employee, rule.code, system_implementation_date,
                                                        self.date_from)
        else:
            raise ValidationError(_("Aucune regle n'a été definie pour le calcul de l'allocation congés payés"))

        # 4- Ajouter brut congé antérieur et calculer le salaire moyen
        cumulative_wages += gross_previous_leave
        ref_months = ceil(reference_months.months + reference_months.years * 12 + reference_months.days / 30)
        average_wage = cumulative_wages / (ref_months if ref_months > 0 else 1)
        # 5- Calculer le salaire journalier
        daily_salary = average_wage / (self.days_since_last_leave / ref_months if ref_months > 0 else 1)
        # 6- Calculer le montant de l'allocation en fonction du nombre de jour de congé pris
        leave_allowance = ceil(daily_salary) * number_days_off
        # 7- retourner la valeur calculée
        return leave_allowance

    def getTauxByCode(self, rubrique):
        lines = self.line_ids
        for line in lines:
            if line.code == rubrique:
                taux = "{:.2f}".format(line.rate).replace('.', ',')
                return taux
        return False

    def calculate_leave_allowances(self):
        for rec in self:
            # 0- rechercher le congé validé de l'employé et pas pris en compte dans la paye
            validated_leave = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),
                                                           ('holiday_status_id.code', '=', 'CONG'),
                                                           ('state', '=', 'validate'), ('payslip_status', '=', False),
                                                           ('to_pay', '=', True)], limit=1)
            rec.get_cumul_holiday()
            if validated_leave:
                # 1- rechercher à partir du code congé, l'enregistrement congé annuel ou congé payé dans autres entrées
                other_entries = self.env['hr.payslip.input'].search([('code', 'in', ('CONG', 'CNGP')),
                                                                     ('payslip_id', '=', rec.id)])
                # 2- Si trouvé, mettre à jour le montant. Si non, créer la ligne avec comme montant, celle que nous avons calculée

                if len(other_entries) > 1:
                    for element in other_entries:
                        element.unlink()
                    other_entries = self.env['hr.payslip.input'].search([('code', 'in', ('CONG', 'CNGP')),
                                                                         ('payslip_id', '=', rec.id)])
                if len(other_entries) == 1:
                    other_entries.amount = rec.compute_leave_amount(rec.employee_id.id,
                                                                    validated_leave.number_of_days_display)[0]
                    other_entries.number_days_off = validated_leave.number_of_days_display

                if not other_entries:
                    salary_rule = self.env['hr.payslip.input.type'].search([('code', '=', 'CONG')], limit=1)
                    vals = {
                        # contract_id supprimé en Odoo 19 (hr.payslip.input n'a plus ce champ)
                        'payslip_id': rec.id,
                        'name': salary_rule.name,
                        'input_type_id': salary_rule.id,
                        'number_days_off': validated_leave.number_of_days_display,
                        'amount': rec.compute_leave_amount(rec.employee_id.id, validated_leave.number_of_days_display)
                    }
                    self.env['hr.payslip.input'].create(vals)
                validated_leave.write({'payslip_status': True})

                # 3- Rechercher dans les jours travaillés, le work100 et faire les corrections necessaires
                works_days = self.env['hr.payslip.worked_days'].search([('code', '=', 'WORK100'),
                                                                        ('payslip_id', '=', rec.id)], limit=1)
                # validated_leave.request_date_from
                if rec.date_from <= validated_leave.request_date_from and validated_leave.request_date_to <= rec.date_to:
                    works_days.number_of_days = max(
                        works_days.number_of_days - (validated_leave.number_of_days_display + 1), 0)
                    works_days.number_of_hours = max((works_days.number_of_days * 173.33) / 30, 0)
                elif validated_leave.request_date_from < rec.date_to < validated_leave.request_date_to:
                    # En Odoo 19, ces champs sont des Date — pas besoin de from_string()
                    d1 = validated_leave.request_date_from
                    d2 = rec.date_to
                    delta_days = relativedelta.relativedelta(d2, d1)
                    works_days.number_of_days = max(works_days.number_of_days - (delta_days.days + 1), 0)
                    works_days.number_of_hours = max((works_days.number_of_days * 173.33) / 30, 0)
                else:
                    pass

                # 4 recuperer le nombre de jour de congé et recalculer le bulletin
                rec.get_number_days_off()
                rec.compute_sheet()
                rec.get_cumul_holiday()
            else:
                pass

    @api.depends('input_line_ids')
    def get_number_days_off(self):
        for rec in self:
            for line in rec.input_line_ids:
                if line.code in {'CONG', 'CNGP'}:
                    rec.number_days_off = line.number_days_off
                if line.code in {'RQ_CONG', 'RQ_CNGP'}:
                    rec.number_remaining_days_leave = line.number_days_off
                    
    


    def _get_worked_day_lines(self, domain=None, check_out_of_version=True):
        self.ensure_one()
        record = super(HrPayslip, self)._get_worked_day_lines(domain=domain, check_out_of_version=check_out_of_version)
        work100_rec = self.env['hr.work.entry.type'].search([('code', '=', 'WORK100')], limit=1)
        if not work100_rec:
            raise ValidationError(
                _("Le code WORK100 des jours travaillés n'est pas défini. Merci de faire le nécessaire "
                  "ou de contacter un administrateur"))
        for line in record:
            if line['work_entry_type_id'] == work100_rec.id:
                line['number_of_days'] = 30.0
                line['number_of_hours'] = 173.33
        return record

    def deletion_input_duplicates(self):
        for slip in self:
            id_input = [input_line.id for input_line in slip.input_line_ids]
            moitie = len(id_input) / 2
            for input_line in slip.input_line_ids:
                if input_line.id in id_input[0:int(moitie)]:
                    input_line.unlink()



class HrPayrollInput(models.Model):
    _inherit = "hr.payslip.input"

    number_days_off = fields.Integer('Nombre de jour de congé', default=0)


class HrPayrollRun(models.Model):
    _inherit = "hr.payslip.run"

    def generate_payslips(self, version_ids=None, employee_ids=None):
        result = super().generate_payslips(version_ids=version_ids, employee_ids=employee_ids)
        self.compute_payslip_input_line_ids()
        self.deletion_payslip_input_duplicates()
        return result

    def compute_payslip_input_line_ids(self):
        for run in self:
            for slip in run.slip_ids:
                slip._compute_input_line_ids()
                slip.compute_sheet()

    def deletion_payslip_input_duplicates(self):
        for run in self:
            for slip in run.slip_ids:
                slip.deletion_input_duplicates()
