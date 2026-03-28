# -*- encoding: utf-8 -*-
from math import ceil

from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil import relativedelta
from math import ceil
import babel

import logging

_logger = logging.getLogger(__name__)


class PayrollBalanceAnyAccount(models.Model):
    _name = 'hr_payroll_custom.balance_any_account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Gestion des soldes de tout compte'

    def get_default_end_date(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    name = fields.Char('Référence', compute='get_employee_info', store=True, readonly=False, tracking=True)
    other_indemnity = fields.Integer('Autre indemnité', default=0, tracking=True,
                                     help="Ajouter les autres indemnités: voitures...")
    total_gross = fields.Integer('Total BRUT', help="Somme des BRUTS des 12 derniers salaires et des autres indemnités")
    average_gross = fields.Integer('Moyenne BRUT', help="Moyenne de Total BRUT sur 12 mois")
    sum_salary_elements = fields.Integer('Cumul éléments du salaire', default=0, compute='get_sum_salary_elements',
                                         help="Somme des éléments du salaire")
    hiring_date = fields.Date("Date d'embauche", compute='get_employee_info', store=True)
    end_date = fields.Date('Date de sortie Effective ', default=get_default_end_date, tracking=True,
                           help="Date d'arrêt effectif de service. Elle peut être différente de la date de sortie "
                                "prévisionnelle si l'employé de fais pas son préavis dans les normes.")
    medal_leave = fields.Integer('Jours ouvrables pour médaille', default=0, tracking=True,
                                 help="Nombre de jours ouvrables de congés supplémentaires dû à l'obtention d'une "
                                      "médaille ")
    seniority = fields.Integer('Ancienneté', default=0, compute='get_seniority', store=True, help="Estimée en jour")
    seniority_days = fields.Integer('Jours', compute='get_seniority', store=True)
    seniority_months = fields.Integer('Mois', compute='get_seniority', store=True)
    seniority_years = fields.Integer('Année', compute='get_seniority', store=True)
    deposit_date = fields.Date('Date dépôt', tracking=True, help="Date de dépôt de la lettre de démission")
    date_return_last_holidays = fields.Date('Date de retour dernier congé', compute='get_employee_info', store=True,
                                            help="Date de retour du dernier congé")
    gross_salary_leave = fields.Integer('BRUT congé', compute='get_gross_salary_leave', store=True,
                                        help='Cumul des BRUT depuis le dernier congé')
    estimated_departure_date = fields.Date('Date sortie prévisionnelle', compute='compute_estimated_departure_date',
                                           help="Date de sortie si l'employé effectue son préavis dans les normes")
    notice_given = fields.Integer("Préavis effectué", compute='compute_estimated_departure_date',
                                  help="Préavis effectué en fonction de la date de dépôt de la lettre de démission "
                                       "et de la date de sortie effective.")
    notice_not_given = fields.Integer("Préavis non effectué", compute='compute_estimated_departure_date',
                                      help="Différence entre 60 et le préavis effectué.Il permet de savoir"
                                           " si l'employé doit rembourser à l'entreprise.")
    total_indemnity = fields.Integer('Total indemnité', default=0, compute='get_indemnity',
                                     help="Le cumul des indemnités")
    taxable_indemnity = fields.Integer('Indemnité imposable', default=0, compute='get_indemnity',
                                       help="La part de l'indemnité qui est imposable")
    spreading_period = fields.Integer('Période étalement')
    not_taxable_indemnity = fields.Integer('Indemnité non imposable', default=0, compute='get_indemnity',
                                           help="La part de l'indemnité qui est non imposable")
    employee_id = fields.Many2one('hr.employee', 'Employé', required=True, ondelete='cascade', tracking=True)
    version_id = fields.Many2one('hr.version', 'Dossier employé', required=False, compute='get_employee_info', store=True)
    motif_fin_contract_id = fields.Many2one('hr.departure.reason', 'Motif du départ', tracking=True,
                                            help="Utilisé pour le calcul des indemnités.")
    state = fields.Selection([('draft', 'Bouillion'), ('validate', 'Validé')], string='Etat', default='draft',
                             tracking=True)
    holiday_bonuses = fields.Boolean("Primes sur congé", default=False,
                                     help="Cocher si vous voulez payer la gratification/congé et le 13e mois/congé")
    job_search_time = fields.Boolean("Préavis effectué a plein temps?", default=False,
                                     help="Cocher si l'agent n'a pas bénéficié de ces jours de recherche d'emploi")
    company_id = fields.Many2one('res.company', 'Compagnie', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    last_salary_line_ids = fields.One2many('hr_payroll_custom.last_salary_line', 'balance_any_account_id',
                                           'Derniers bulletins')
    net_payable = fields.Float("Net à payer", digits=(16, 0), store=True,
                               help="Montant net à payer parès calcul des droits de l'employé")
    salary_elements_ids = fields.One2many('hr_payroll_custom.salary_elements', 'balance_any_account_id',
                                          'Elements du salaire')
    taxable_section_ids = fields.One2many('hr_payroll_custom.taxable_section', 'balance_any_account_id',
                                          'Recapitulatif')
    allowances_ids = fields.One2many('hr_payroll_custom.allowances', 'balance_any_account_id', 'Indemnités')
    tax_balance_any_account_ids = fields.One2many('hr_payroll_custom.tax_balance_any_account', 'balance_any_account_id',
                                                  'Impots')
    not_taxable_section_ids = fields.One2many('hr_payroll_custom.not_taxable_section', 'balance_any_account_id',
                                              'Rubrique non imposable')
    taken_into_account = fields.Boolean('Pris en compte', default=False)

    _sql_constraints = [
        ('balance_any_account_uniq', 'unique(employee_id)',
         "Il ne peut y avoir qu'un seul calcul du solde de tout compte d'un employé. Merci rechercher celui qui a "
         "été crée."),
    ]

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def get_employee_info(self):
        if self.employee_id:
            hiring_date = self.employee_id.hiring_date
            self.hiring_date = hiring_date
            self.date_return_last_holidays = self.employee_id.date_return_last_holidays

            name = 'SOLDE DE TOUT COMPTE ' + self.employee_id.name + ' ' + (self.employee_id.first_name or '') + ' (' + \
                   (self.employee_id.registration_number or '') + ')'
            self.name = name
            version = self.employee_id.version_id
            self.version_id = version.id if version else False
        else:
            self.motif_fin_contract_id = False

    @api.onchange('hiring_date', 'end_date')
    @api.depends('hiring_date', 'end_date')
    def get_seniority(self):
        if self.hiring_date and self.end_date:
            seniority_total = relativedelta.relativedelta(self.end_date, self.hiring_date)
            self.seniority_days = seniority_total.days + 1
            self.seniority_months = seniority_total.months
            self.seniority_years = seniority_total.years
            self.seniority = seniority_total.days + seniority_total.months * 30 + seniority_total.years * 360 + 1

    @api.onchange('salary_elements_ids')
    @api.depends('salary_elements_ids')
    def get_sum_salary_elements(self):
        if self.salary_elements_ids:
            self.sum_salary_elements = sum([x.amount for x in self.salary_elements_ids])
        else:
            self.sum_salary_elements = 0

    @api.onchange('allowances_ids')
    @api.depends('allowances_ids')
    def get_indemnity(self):
        if self.allowances_ids:
            total_indemnity = sum([x.amount for x in self.allowances_ids])
            self.total_indemnity = total_indemnity
            self.not_taxable_indemnity = ceil(total_indemnity / 2)
            self.taxable_indemnity = total_indemnity - self.not_taxable_indemnity
        else:
            self.total_indemnity = 0
            self.not_taxable_indemnity = 0
            self.taxable_indemnity = 0

    @api.onchange('last_salary_line_ids')
    @api.depends('last_salary_line_ids')
    def get_gross_salary_leave(self):
        for rec in self:
            if rec.last_salary_line_ids:
                last_payslip = rec.last_salary_line_ids.filtered(lambda d: d.order == 1)
                rec.gross_salary_leave = last_payslip.payslip_id.gross_salary_leave
            else:
                # chercher le dernier bulletin et recuperer le brut conge
                payslips = rec.env['hr.payslip'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', 'in', ('validated', 'paid'))
                     ], order='date_from desc', limit=1)
                if payslips:
                    rec.gross_salary_leave = payslips.gross_salary_leave
                else:
                    # recuperer le solde conge car nouvelle installation
                    rec.gross_salary_leave = rec.employee_id.leave_balance

    def get_id_by_code(self, code):
        id_rule = self.env['hr.salary.rule'].search([('code', '=', code)], limit=1).id
        if id_rule:
            return id_rule
        else:
            return False

    def generate_data(self):
        for rec in self:
            if rec.employee_id:
                gross_salary_leave = 0
                gross_account_balance = 0
                if rec.deposit_date > rec.end_date:
                    raise ValidationError(_("La date de départ effective doit être supérieur à la date de dépôt de la "
                                    "lettre de démission. Merci de faire les corrections nécessaires."))

                if rec.end_date and rec.date_return_last_holidays:
                    duration_presence = relativedelta.relativedelta(rec.end_date, rec.date_return_last_holidays)
                    days_presence = duration_presence.years * 360 + duration_presence.months * 30 + duration_presence.days
                    facteur = rec.company_id.number_holidays_locaux if rec.employee_id.nature_employe == 'local' \
                        else rec.company_id.number_holidays_expat
                    acquired_leave = facteur * days_presence / 30
                    # Prise en compte des jours supplémentaires liés à une décoration"
                    if rec.medal_leave > 0:
                        acquired_leave += rec.medal_leave
                    # determination des jours suplémentaires liés à l'ancienneté
                    seniority_in_years = rec.seniority_years
                    if 5 <= seniority_in_years < 10:
                        acquired_leave += 1
                    elif 10 <= seniority_in_years < 15:
                        acquired_leave += 2
                    elif 15 <= seniority_in_years < 20:
                        acquired_leave += 3
                    elif 20 <= seniority_in_years < 25:
                        acquired_leave += 5
                    elif 25 <= seniority_in_years < 30:
                        acquired_leave += 7
                    elif seniority_in_years >= 30:
                        acquired_leave += 8
                    else:
                        pass
                    if rec.employee_id.gender == 'female':
                        if rec.employee_id.age < 21:
                            acquired_leave += 2 * rec.employee_id.children
                        else:
                            if rec.employee_id.children >= 4:
                                acquired_leave += 2 * (rec.employee_id.children - 3)
                    calendar_days_off = round(round(acquired_leave) + round(acquired_leave) / 6)
                    payslips = rec.env['hr.payslip'].search(
                        [('employee_id', '=', rec.employee_id.id), ('state', 'in', ('validated', 'paid')),
                         ('date_to', '<=', rec.end_date)],
                        order='date_from desc', limit=12)
                    if payslips and rec.motif_fin_contract_id and rec.motif_fin_contract_id.indemnity:
                        res_payslip = []
                        cpt = 0
                        for payslip in payslips:
                            cpt += 1
                            vals_payslip = {
                                'order': cpt,
                                'name': payslip.name,
                                'payslip_id': payslip.id,
                                'balance_any_account_id': rec.id
                            }
                            res_payslip.append(vals_payslip)
                        rec.last_salary_line_ids.unlink()
                        rec.env['hr_payroll_custom.last_salary_line'].create(res_payslip)

                    rec.get_gross_salary_leave()

                    if rec.version_id:
                        res_contract = []
                        vals = {
                            'balance_any_account_id': rec.id,
                            'name': 'Salaire catégoriel',
                            'amount': rec.version_id.wage
                        }
                        res_contract.append(vals)
                        vals = {
                            'balance_any_account_id': rec.id,
                            'name': 'extra_pay',
                            'amount': rec.version_id.extra_pay
                        }
                        res_contract.append(vals)
                        rec.employee_id._get_seniority()
                        if rec.employee_id.seniority_employee >= 2:
                            vals = {
                                'balance_any_account_id': rec.id,
                                'name': "Primes d'ancienneté",
                                'amount': rec.version_id.wage * 0.01 * min(rec.employee_id.seniority_employee, 25)
                            }
                            res_contract.append(vals)

                        for line in rec.version_id.fixed_premiums_ids.filtered(
                                (lambda p: p.input_type_id.code != 'ALL_FAM')):
                            vals = {
                                'balance_any_account_id': rec.id,
                                'name': line.input_type_id.name,
                                'amount': line.amount
                            }
                            res_contract.append(vals)
                        rec.salary_elements_ids.unlink()

                        rec.env['hr_payroll_custom.salary_elements'].create(res_contract)
                    else:
                        raise ValidationError(
                            _("Cet employé n'a pas de dossier actif. Nous ne pouvons pas poursuivre l'opération"))
                    if rec.motif_fin_contract_id:
                        if rec.motif_fin_contract_id.indemnity:
                            res_indemnity = []
                            if 360 <= rec.seniority:
                                seniority = min(rec.seniority, 1800)
                                val_indemnity = {
                                    'balance_any_account_id': rec.id,
                                    'name': 'Ancienneté de 1 à 5 ans',
                                    'amount': ceil(rec.average_gross * 0.30 * (seniority / 360))
                                }
                                res_indemnity.append(val_indemnity)
                            if 1800 < rec.seniority:
                                seniority = min(rec.seniority, 3600) - 1800
                                val_indemnity = {
                                    'balance_any_account_id': rec.id,
                                    'name': 'Ancienneté de 5 à 10 ans',
                                    'amount': ceil(self.average_gross * 0.35 * (seniority / 360))
                                }
                                res_indemnity.append(val_indemnity)
                            if 3600 < rec.seniority:
                                seniority = rec.seniority - 3600
                                val_indemnity = {
                                    'balance_any_account_id': rec.id,
                                    'name': 'Ancienneté supérieur à 10 ans',
                                    'amount': ceil(rec.average_gross * 0.40 * (seniority / 360))
                                }
                                res_indemnity.append(val_indemnity)

                            if res_indemnity:
                                rec.allowances_ids.unlink()
                                rec.env['hr_payroll_custom.allowances'].create(res_indemnity)
                        else:
                            pass
                    else:
                        raise ValidationError(_("Vous devez définit le motif de départ"))
                    # Recapitulate

                    # Préavis effectué
                    res_recap = []
                    res_tax = []
                    res_not_taxable = []
                    bonus_transport = rec.company_id.bonus_transport
                    notice_paid = rec.notice_given / 3
                    if rec.job_search_time:
                        notice_paid = 30
                    if not rec.motif_fin_contract_id.indemnity:
                        vals_recap = {
                            'balance_any_account_id': rec.id,
                            'rule_id': rec.get_id_by_code('PREA'),
                            'name': "Temps de recherche d'emploi / préavis effectués (" + str(
                                int(notice_paid)) + " jours)",
                            'amount': round(((rec.notice_given / 3) if not rec.job_search_time else 30) * (
                                    (rec.sum_salary_elements - bonus_transport) / 30))
                        }
                        gross_salary_leave += vals_recap['amount']
                        gross_account_balance += vals_recap['amount']
                        res_recap.append(vals_recap)
                    if not rec.motif_fin_contract_id.indemnity:
                        # Préavis non effectué
                        vals_not_taxable = {
                            'balance_any_account_id': rec.id,
                            'rule_id': rec.get_id_by_code('SAL_AV'),
                            'name': 'Préavis non effectués (' + str(rec.notice_not_given) + ' jours)',
                            'amount': round(rec.notice_not_given * (rec.sum_salary_elements / 30)) * -1
                        }
                        res_not_taxable.append(vals_not_taxable)
                    bonus_on_gross = 0  # bonus pour augmenter le brut du dernier bulletin
                    # Calcul de la gratification
                    year = rec.end_date.year
                    first_day_year = str(year) + '-01-01'
                    first_day_year = datetime.strptime(first_day_year, '%Y-%m-%d')
                    delta_days = relativedelta.relativedelta(rec.end_date,
                                                             first_day_year) + relativedelta.relativedelta(
                        days=1)
                    delta_days = min(delta_days.months * 30 + delta_days.days, 360)
                    if rec.end_date.month != 12:
                        quotient_days_bonus = delta_days / 360
                        vals_recap_amount = round(rec.sum_salary_elements * quotient_days_bonus)
                        bonus_on_gross += vals_recap_amount
                        vals_recap = {
                            'balance_any_account_id': rec.id,
                            'rule_id': rec.get_id_by_code('GRATIF'),
                            'name': 'Gratification (' + str(delta_days) + ' jours)',
                            'amount': vals_recap_amount
                        }
                        gross_salary_leave += vals_recap['amount']
                        gross_account_balance += vals_recap['amount']
                        res_recap.append(vals_recap)
                    else:
                        pass

                    if rec.holiday_bonuses:
                        quotient_days_bonus = calendar_days_off / 360
                        vals_recap = {
                            'balance_any_account_id': rec.id,
                            'rule_id': rec.get_id_by_code('GRATIF'),
                            'name': 'Gratification/Congé (' + str(calendar_days_off) + ' jours)',
                            'amount': round(rec.sum_salary_elements * quotient_days_bonus)
                        }
                        gross_salary_leave += vals_recap['amount']
                        gross_account_balance += vals_recap['amount']
                        res_recap.append(vals_recap)

                    # Calcul du Treizieme mois
                    # if self.end_date.month == 12:
                    quotient_days_bonus = delta_days / 360
                    vals_recap_amount = round(rec.sum_salary_elements * quotient_days_bonus)
                    bonus_on_gross += vals_recap_amount
                    vals_recap = {
                        'balance_any_account_id': rec.id,
                        'rule_id': rec.get_id_by_code('P_13M'),
                        'name': 'Treizième mois (' + str(delta_days) + ' jours)',
                        'amount': vals_recap_amount
                    }
                    gross_salary_leave += vals_recap['amount']
                    gross_account_balance += vals_recap['amount']
                    res_recap.append(vals_recap)

                    if rec.holiday_bonuses:
                        quotient_days_bonus = calendar_days_off / 360
                        vals_recap = {
                            'balance_any_account_id': rec.id,
                            'rule_id': rec.get_id_by_code('P_13M'),
                            'name': 'Treizième mois/ Congé (' + str(calendar_days_off) + ' jours)',
                            'amount': round(rec.sum_salary_elements * quotient_days_bonus)
                        }
                        gross_salary_leave += vals_recap['amount']
                        gross_account_balance += vals_recap['amount']
                        res_recap.append(vals_recap)

                    # Transport non imposable recherche emploi
                    if not rec.motif_fin_contract_id.indemnity:
                        vals_not_taxable = {
                            'balance_any_account_id': rec.id,
                            'rule_id': rec.get_id_by_code('TRSP'),
                            'name': "Transport non imposable /Recherche d'emploi (" + str(int(notice_paid)) + " jours)",
                            'amount': round(notice_paid * bonus_transport / 30)
                        }
                        res_not_taxable.append(vals_not_taxable)

                    leave_not_taken = ceil(rec.employee_id.remaining_leaves)

                    vals_recap_amout = round(((rec.sum_salary_elements - bonus_transport) / 30) * leave_not_taken)
                    bonus_on_gross += vals_recap_amout
                    vals_recap = {
                        'balance_any_account_id': rec.id,
                        'rule_id': rec.get_id_by_code('CONG'),
                        'name': "Congés non pris (" + str(leave_not_taken) + " jours)",
                        'amount': vals_recap_amout
                    }
                    gross_salary_leave += vals_recap['amount']
                    gross_account_balance += vals_recap['amount']
                    res_recap.append(vals_recap)

                    # Période etalement
                    month = rec.end_date.month
                    first_day_month = str(year) + '-' + str(month) + '-01'
                    first_day_month = datetime.strptime(first_day_month, '%Y-%m-%d')
                    days_worked = relativedelta.relativedelta(rec.end_date,
                                                              first_day_month) + relativedelta.relativedelta(
                        days=1)
                    days_worked = min(days_worked.days, 30)
                    rec.spreading_period = notice_paid + days_worked + leave_not_taken + calendar_days_off
                    if rec.motif_fin_contract_id.indemnity:
                        bonus = (rec.taxable_indemnity / rec.average_gross) * 30
                        rec.spreading_period += round(bonus)

                    # Calcul du salaire du mois
                    """
                    Création et calcul du bulletin de l'employé. Ensuite récupération du montant du BRUT et du Transport 
                    et suppression du bulletin            
                    """
                    date_to = first_day_month + relativedelta.relativedelta(days=-1, months=1)
                    payslip_obj = self.env['hr.payslip']
                    version = self.env['hr.version'].browse(rec.version_id.id)
                    # inputs = payslip_obj.get_inputs(version, first_day_month, date_to)
                    # input_line_ids = []
                    # if inputs:
                    #     for input in inputs:
                    #         temp = [0, False, input]
                    #         input_line_ids += [temp]
                    # worked_days = payslip_obj.get_worked_day_lines(contract, first_day_month, date_to)
                    # worked_days_line_ids = []
                    # if worked_days:
                    #     for worked_day in worked_days:
                    #         if worked_day['code'] == 'WORK100':
                    #             worked_day['number_of_days'] = days_worked
                    #         temp = [0, False, worked_day]
                    #         worked_days_line_ids += [temp]
                    locale = self.env.context.get('lang') or 'fr_FR'

                    vals = {
                        'name': _('Salary Slip of %s for %s') % (
                            rec.employee_id.name, tools.ustr(
                                babel.dates.format_date(date=first_day_month, format='MMMM-y', locale=locale))),
                        'employee_id': rec.employee_id.id,
                        'date_from': first_day_month,
                        'date_to': date_to,
                        'version_id': version.id,
                        'struct_id': version.structure_type_id.default_struct_id.id
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
                    # Suppression des rubiques généré en doublon
                    self.env['hr.payslip.input'].browse(list(input_records_to_delete.keys())).unlink()

                    logging.info(f"{'=' * 50}>L468")
                    payslip_id.compute_sheet()
                    logging.info(f"{'=' * 50}>L470")
                    monthly_salary_amount = self.env['hr.payslip.line'].search([('slip_id', '=', payslip_id.id),
                                                                                ('code', '=', 'BRUT')], limit=1)
                    vals_recap_amount = monthly_salary_amount.total
                    bonus_on_gross += vals_recap_amount
                    vals_recap = {
                        'balance_any_account_id': rec.id,
                        'name': 'Salaire ' + str(tools.ustr(
                            babel.dates.format_date(date=rec.end_date, format='MMMM',
                                                    locale=locale))).capitalize() + ' ' +
                                str(year) + ' (' + str(days_worked) + ' jours)',
                        'amount': vals_recap_amount
                    }
                    gross_salary_leave += vals_recap['amount']
                    gross_account_balance += vals_recap['amount']
                    res_recap.append(vals_recap)

                    # Calcul du montant moyen des 12 derniers bulletins
                    total_gross = 0
                    for payslip in rec.last_salary_line_ids:
                        if payslip.order == 1:
                            payslip.write({'gross_amount_report': payslip.gross_amount + bonus_on_gross,
                                           'gross_amount': payslip.gross_amount + bonus_on_gross})
                        total_gross += payslip.gross_amount

                    if rec.other_indemnity > 0:
                        total_gross += rec.other_indemnity
                    rec.total_gross = total_gross
                    rec.average_gross = ceil(total_gross / 12)

                    # Calcul du transport non imposable
                    non_taxable_transportation = self.env['hr.payslip.line'].search(
                        [('slip_id', '=', payslip_id.id), ('code', '=', 'TRSP')], limit=1)
                    vals_not_taxable = {
                        'balance_any_account_id': rec.id,
                        'rule_id': rec.get_id_by_code('TRSP'),
                        'name': 'Prime de transport non imposable',
                        'amount': non_taxable_transportation.total
                    }
                    res_not_taxable.append(vals_not_taxable)
                    # Suppresion du bulletin
                    payslip_id.write({'state': 'draft'})
                    payslip_id.unlink()

                    # calcul des indemnités de congés
                    rec.gross_salary_leave += gross_salary_leave
                    average_holiday_salary = rec.gross_salary_leave / days_presence
                    vals_recap = {
                        'balance_any_account_id': rec.id,
                        'rule_id': rec.get_id_by_code('CONG'),
                        'name': 'Allocation congés (' + str(calendar_days_off) + ' jours)',
                        'amount': round(average_holiday_salary * calendar_days_off)
                    }
                    gross_account_balance += vals_recap['amount']
                    res_recap.append(vals_recap)

                    """Ajoute des indemnités depart à la retraite dans le calcul solde de tout compte"""
                    if rec.total_indemnity > 0:
                        # Indemnité depart a la retraite imposable
                        vals_recap = {
                            'balance_any_account_id': rec.id,
                            'rule_id': rec.get_id_by_code('IND_RET'),
                            'name': 'Indemnité départ retraite imposable',
                            'amount': rec.taxable_indemnity
                        }
                        gross_account_balance += vals_recap['amount']
                        res_recap.append(vals_recap)

                        # Indemnité depart a la retraite non imposable
                        vals_not_taxable = {
                            'balance_any_account_id': rec.id,
                            'rule_id': rec.get_id_by_code('IND_RET_NN_IMP'),
                            'name': 'Indemnité départ retraite non imposable',
                            'amount': rec.taxable_indemnity
                        }
                        res_not_taxable.append(vals_not_taxable)

                    """Calcul des impots :
                    * ITS (impôt unifié — fusion ITS + CN + IGR, réforme fiscale 2024)
                    * CNPS ou CGRAE
                    Le calcul utilise gross_account_balance ramené à un équivalent mensuel
                    via le spreading_period (période d'étalement en jours).
                    """
                    # ITS unifié (barème progressif sur le brut mensuel équivalent)
                    rate_spreading_period = rec.spreading_period / 30
                    brut_mensuel = gross_account_balance / rate_spreading_period if rate_spreading_period else gross_account_balance

                    if brut_mensuel < 75000:
                        its_mensuel = 0
                    elif brut_mensuel <= 240000:
                        its_mensuel = (brut_mensuel - 75000) * 0.16
                    elif brut_mensuel <= 800000:
                        its_mensuel = (brut_mensuel - 240000) * 0.21 + 26400
                    elif brut_mensuel <= 2400000:
                        its_mensuel = (brut_mensuel - 800000) * 0.24 + 144000
                    elif brut_mensuel <= 8000000:
                        its_mensuel = (brut_mensuel - 2400000) * 0.28 + 527999
                    else:
                        its_mensuel = (brut_mensuel - 8000000) * 0.32 + 2095999

                    parts = rec.employee_id.part_igr or 1
                    if parts <= 1:
                        reduction = 0
                    elif parts <= 1.5:
                        reduction = 5500
                    elif parts <= 2:
                        reduction = 11000
                    elif parts <= 2.5:
                        reduction = 16500
                    elif parts <= 3:
                        reduction = 22000
                    elif parts <= 3.5:
                        reduction = 27500
                    elif parts <= 4:
                        reduction = 33000
                    elif parts <= 4.5:
                        reduction = 38500
                    else:
                        reduction = 44000

                    payroll_tax = round(max(0, its_mensuel - reduction) * rate_spreading_period)
                    vals_tax = {
                        'balance_any_account_id': rec.id,
                        'rule_id': rec.get_id_by_code('ITS'),
                        'name': 'RETENUE ITS',
                        'amount': payroll_tax
                    }
                    res_tax.append(vals_tax)

                    # CNPS & CGRAE
                    social_fund = 0
                    code = ''
                    if rec.employee_id.type != 'p':
                        gross_cnps = sum([x.amount for x in rec.salary_elements_ids])
                        max_cnps_tax_base = rec.company_id.max_cnps_tax_base
                        if gross_cnps < max_cnps_tax_base:
                            social_fund = (gross_account_balance * rec.company_id.local_employee_cnps_rate) / 100
                        else:
                            social_fund = (max_cnps_tax_base * rec.company_id.local_employee_cnps_rate) / 100
                        social_fund_name = 'CNPS'
                        code = 'CNPS'
                    else:
                        if rec.version_id:
                            social_fund = (rec.version_id.salaire_cgrae * rec.company_id.tx_cgrae_employee) / 100
                        social_fund_name = 'CGRAE'
                        code = 'CGRAE_E'
                    vals_tax = {
                        'balance_any_account_id': rec.id,
                        'rule_id': rec.get_id_by_code(code),
                        'name': 'RETENUE ' + social_fund_name,
                        'amount': round(social_fund)
                    }
                    res_tax.append(vals_tax)

                    # if self.allowances_ids:
                    #     self.allowances_ids.unlink()
                    # if self.last_salary_line_ids:
                    #     self.last_salary_line_ids.unlink()
                    rec.taxable_section_ids.unlink()
                    rec.tax_balance_any_account_ids.unlink()
                    rec.not_taxable_section_ids.unlink()
                    rec.env['hr_payroll_custom.taxable_section'].create(res_recap)
                    rec.env['hr_payroll_custom.tax_balance_any_account'].create(res_tax)
                    rec.env['hr_payroll_custom.not_taxable_section'].create(res_not_taxable)

                    rec.net_payable = sum(x.amount for x in rec.taxable_section_ids) - sum(
                        y.amount for y in rec.tax_balance_any_account_ids) + sum(
                        z.amount for z in rec.not_taxable_section_ids)

            else:
                raise ValidationError(_("Vous devez choisir un employé avant l'exécution de cette action."))

    @api.depends('deposit_date', 'end_date')
    def compute_estimated_departure_date(self):
        for rec in self:
            if rec.deposit_date:
                rec.estimated_departure_date = rec.deposit_date + relativedelta.relativedelta(days=90)
                if rec.end_date:
                    notice_given = (rec.end_date - rec.deposit_date) + relativedelta.relativedelta(days=1)
                    rec.notice_given = notice_given.days
                    if notice_given.days > 60:
                        rec.notice_not_given = 0
                    else:
                        rec.notice_not_given = 60 - notice_given.days
                else:
                    rec.notice_given = 0
                    rec.notice_not_given = 0
            else:
                rec.estimated_departure_date = False
                rec.notice_given = 0
                rec.notice_not_given = 0

    def action_done(self):
        self.state = 'validate'


class PayrollLastSalary(models.Model):
    _name = 'hr_payroll_custom.last_salary_line'
    _description = '12 derniers salaires'

    name = fields.Char('Référence')
    order = fields.Integer('N° ordre', default=0)
    period = fields.Char('Période', compute='get_data', store=True)
    gross_amount = fields.Integer('Montant (BRUT)', compute='get_data', store=True)
    gross_amount_report = fields.Integer('Montant', default=0)  # utiliser pour le rapport
    payslip_id = fields.Many2one('hr.payslip', 'Bulletin')
    balance_any_account_id = fields.Many2one('hr_payroll_custom.balance_any_account', 'Solde de tout compte',
                                             ondelete='cascade')

    @api.depends('payslip_id')
    def get_data(self):
        if self.payslip_id:
            gross_amount = 0
            for line in self.payslip_id.line_ids:
                if line.code == 'BRUT':
                    gross_amount += line.total
                    break

            self.gross_amount = gross_amount
            period = self.payslip_id.date_from
            self.period = datetime.strftime(period, '%m-%Y')

        else:
            raise ValidationError(_("Vous devez définir le bulletin avant d'effectuer cette action."))


class PayrollSalaryElements(models.Model):
    _name = 'hr_payroll_custom.salary_elements'
    _description = "Les elements du salaire"

    name = fields.Char('Libellé')
    input_type_id = fields.Many2one('hr_payroll_custom.fixed_premiums', 'Rubrique')
    rule_id = fields.Many2one('hr.salary.rule', 'Règle', compute='get_rule', store=True)
    amount = fields.Integer('Montant')
    balance_any_account_id = fields.Many2one('hr_payroll_custom.balance_any_account', 'Solde de tout compte',
                                             ondelete='cascade')

    @api.depends('input_type_id')
    def get_rule(self):
        for rec in self:
            if rec.input_type_id:
                rule_rec = self.env['hr.salary.rule'].search([('code', '=', rec.input_type_id.code)], limit=1)
                rec.rule_id = rule_rec.id


class PayrollAllowances(models.Model):
    _name = 'hr_payroll_custom.allowances'
    _description = "Les indemnités du solde de tout compte"

    name = fields.Char('Libellé')
    amount = fields.Integer('Montant')
    balance_any_account_id = fields.Many2one('hr_payroll_custom.balance_any_account', 'Solde de tout compte',
                                             ondelete='cascade')


class PayrollTaxableSection(models.Model):
    _name = 'hr_payroll_custom.taxable_section'
    _description = "Rubrique imposable"

    name = fields.Char('Libellé')
    amount = fields.Integer('Montant')
    rule_id = fields.Many2one('hr.salary.rule', 'Rubrique')
    balance_any_account_id = fields.Many2one('hr_payroll_custom.balance_any_account', 'Solde de tout compte',
                                             ondelete='cascade')


class PayrollTaxBalanceAnyAccount(models.Model):
    _name = 'hr_payroll_custom.tax_balance_any_account'
    _description = "Impot du solde de tout compte"

    name = fields.Char('Libellé')
    amount = fields.Integer('Montant')
    rule_id = fields.Many2one('hr.salary.rule', 'Rubrique')
    balance_any_account_id = fields.Many2one('hr_payroll_custom.balance_any_account', 'Solde de tout compte',
                                             ondelete='cascade')


class PayrollNotTaxableSection(models.Model):
    _name = 'hr_payroll_custom.not_taxable_section'
    _description = 'Rubrique non imposable'

    name = fields.Char('Libellé')
    amount = fields.Integer('Montant')
    rule_id = fields.Many2one('hr.salary.rule', 'Rubrique')
    balance_any_account_id = fields.Many2one('hr_payroll_custom.balance_any_account', 'Solde de tout compte',
                                             ondelete='cascade')
