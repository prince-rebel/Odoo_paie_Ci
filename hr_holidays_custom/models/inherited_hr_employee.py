from odoo import fields, models, api
from dateutil import relativedelta
from datetime import datetime, date
from math import ceil
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    date_return_last_holidays = fields.Date(string="Date de retour Congés")
    estimed_date_leave = fields.Date("Date prévisonnelle de depart en congés", compute="_get_estimed_holidays",
                                     store=True)
    number_days_estimed_holidays = fields.Integer("Nombre de jours de congés estimés", compute="_get_estimed_holidays",
                                                  store=True)
    estimated_date_return_leave = fields.Date("Date prévisonnelle de retour de congés", compute="_get_estimed_holidays",
                                              store=True)
    stock_holiday = fields.Integer('Stock congé', default=0)
    stock_total_holiday = fields.Integer('Stock total congé', compute='compute_stock_total_holiday', default=0,
                                         store=True)
    remaining_legal_absence_stock = fields.Integer("Stock d'abscence légale restant",
                                                   compute='compute_remaining_legal_absence_stock',
                                                   help="Stock annuel d'abscence légale. Il est réinitialisé chaque 1er de l'an ")
    planning_save_ids = fields.One2many('hr_holidays_custom.save_planning_holiday', 'employee_id', 'Historique Prévisions congés')
    save_stock_holiday_ids = fields.One2many('hr_holidays_custom.save_stock_holiday', 'employee_id', 'Historique Stock congé')

    def compute_estimated_date_of_leave(self, date_start=False):
        """
        Fonction qui determine les dates prévisionnelles de congés annuels
        :param date_start: date d'embauche ou la date de retour du dernier congé
        :return: none
        """

        if date_start:
            nbr_days = 0
            anc = self.seniority_employee
            if 5 <= anc < 10:
                nbr_days += 1
            elif 10 <= anc < 15:
                nbr_days += 2
            elif 15 <= anc < 20:
                nbr_days += 3
            elif 20 <= anc < 25:
                nbr_days += 5
            elif 25 <= anc < 30:
                nbr_days += 7
            elif anc >= 30:
                nbr_days += 8
            if self.gender == 'female':
                if self.age < 21:
                    nbr_days += 2 * self.children
                else:
                    if self.children >= 4:
                        nbr_days += 2 * (self.children - 3)
            facteur = self.company_id.number_holidays_locaux if self.nature_employe == 'local' \
                else self.company_id.number_holidays_expat

            vals = {
                'estimed_date_leave': fields.Date.from_string(date_start) + relativedelta.relativedelta(years=+1, days=+1),
                'number_days_estimed_holidays': 0,
                'estimated_date_return_leave': False
            }

            # Check if the departure date falls on a Saturday or Sunday
            if vals['estimed_date_leave'].weekday() == 5:
                vals['estimed_date_leave'] = vals['estimed_date_leave'] + \
                                             relativedelta.relativedelta(days=+2)
            if vals['estimed_date_leave'].weekday() == 6:
                vals['estimed_date_leave'] = vals['estimed_date_leave'] + \
                                             relativedelta.relativedelta(days=+1)
            # check if the departure date of leave is holiday
            vals['estimed_date_leave'] = self.get_holiday_of_year(vals['estimed_date_leave'])
            base = facteur * 12 + nbr_days
            nbr_days = round(base + base / 6)
            vals['number_days_estimed_holidays'] = nbr_days
            number_calendar_days = ceil(vals['number_days_estimed_holidays'] * 1.25)
            vals['estimated_date_return_leave'] = vals['estimed_date_leave'] + relativedelta.relativedelta(
                days=+number_calendar_days)
            # Check if the return date of leave falls on a Saturday or a Sunday
            if vals['estimated_date_return_leave'].weekday() == 5:
                vals['estimated_date_return_leave'] = vals['estimated_date_return_leave'] + \
                                                      relativedelta.relativedelta(days=+2)
            if vals['estimated_date_return_leave'].weekday() == 6:
                vals['estimated_date_return_leave'] = vals['estimated_date_return_leave'] + \
                                                      relativedelta.relativedelta(days=+1)
            # check if the return date of leave is holiday
            vals['estimated_date_return_leave'] = self.get_holiday_of_year(vals['estimated_date_return_leave'])
            self.update(vals)

    @api.depends("date_return_last_holidays", "hiring_date")
    def _get_estimed_holidays(self):
        """
        Fontion permettant de déterminer automatiquement la prévision congé.

        Returns: none

        """

        for emp in self:
            if emp.date_return_last_holidays:
                emp.compute_estimated_date_of_leave(emp.date_return_last_holidays)
            elif emp.hiring_date:
                emp.compute_estimated_date_of_leave(emp.hiring_date)
            else:
                pass

    def get_holiday_of_year(self, date):
        """
        Fonction permettant de renvoyer la date du jour ouvrable le plus proche de la date qu'elle a reçu en paramètre
        :param date: date dont on veut vérifier si le jour est ouvrable ou férié (y compris les week-end)
        :return: date du jour ouvrable
        """
        if date.weekday() == 5:
            date = date + relativedelta.relativedelta(days=+2)
        if date.weekday() == 6:
            date = date + relativedelta.relativedelta(days=+1)
        is_holiday = self.env['resource.calendar.leaves'].search([('date_from', '=', date)], limit=1)

        if not is_holiday:
            holidays = self.env['resource.calendar.leaves'].search([('is_recurring', '=', True)])
            if holidays:
                for holiday in holidays:
                    is_holiday = all(getattr(holiday.date_from, x) == getattr(date, x) for x in ['month', 'day'])
                    if is_holiday:
                        break
        while is_holiday:
            date = date + relativedelta.relativedelta(days=+1)
            is_holiday = self.env['resource.calendar.leaves'].search([('date_from', '=', date)], limit=1)
            if not is_holiday:
                holidays = self.env['resource.calendar.leaves'].search([('is_recurring', '=', True)])
                if holidays:
                    for holiday in holidays:
                        is_holiday = all(getattr(holiday.date_from, x) == getattr(date, x) for x in ['month', 'day'])
                        if is_holiday:
                            break
        if date.weekday() == 5:
            date = date + relativedelta.relativedelta(days=+2)
        if date.weekday() == 6:
            date = date + relativedelta.relativedelta(days=+1)
        return date


    @api.depends('stock_holiday', 'number_days_estimed_holidays')
    def compute_stock_total_holiday(self):
        for rec in self:
            previous_year = datetime.now() + relativedelta.relativedelta(years=-1)
            previous_stock = self.env['hr_holidays_custom.save_stock_holiday'].search(
                [('name', '=', previous_year.year), ('employee_id', '=', rec.id)], limit=1)
            rec.stock_total_holiday = previous_stock.number_days if previous_stock else 0
            if rec.estimed_date_leave and rec.estimed_date_leave.year == datetime.now().year:
                rec.stock_total_holiday += rec.number_days_estimed_holidays

    def compute_remaining_legal_absence_stock(self):
        today = date.today()
        first_date = date(today.year, 1, 1)
        for rec in self:
            #recupérer tous les congés de l'année de l'employé dont le type fait parti des absences
            leaves = self.env['hr.leave'].search([('employee_id','=',rec.id),
                                                  ('holiday_status_id.time_type','=','other'),
                                                  ('holiday_status_id.legal_absences','=',False),
                                                  ('request_date_from','>=', first_date)])
            if not leaves:
                rec.remaining_legal_absence_stock = rec.company_id.stock_legal_absence
                continue
            # Faire la somme des jours
            count_leave = 0
            for leave in leaves:
                count_leave += leave.number_of_days
            #Faire la différence avec le stock légal et retourner le resultat : max(0, result)
            rec.remaining_legal_absence_stock = max(rec.company_id.stock_legal_absence - count_leave, 0)
            #tenir compte du resultat pendant les demande d'absence



    @api.model
    def cron_get_leave_allowance(self):
        """
        Fonction permettant d'attribuer une allocation à chaque mois à l'anniversaire d'embauche de chacun des employés
        :return:
        """
        this_date = date.today()
        type = self.env['hr.leave.type'].search([('code', '=', 'CONG')], limit=1)
        if type:
            for emp in self.search([]):
                if emp.hiring_date:
                    temp_date = fields.Date.from_string(emp.hiring_date) + relativedelta.relativedelta(
                        month=this_date.month,
                        year=this_date.year)
                    if temp_date == this_date:
                        vals = {
                            'name': "Allocation mensuelle de congé",
                            'holiday_type': 'employee',
                            'employee_id': emp.id,
                            'holiday_status_id': type.id
                        }
                        if emp.nature_employe == 'local':
                            vals['number_of_days'] = emp.company_id.number_holidays_locaux
                        else:
                            vals['number_of_days'] = emp.company_id.number_holidays_expat
                        holidays = self.env['hr.leave.allocation'].create(vals)
                        if holidays:
                            holidays.action_confirm()
                            holidays.action_validate()
        return True


class SavePlanningHoliday(models.Model):
    _name = 'hr_holidays_custom.save_planning_holiday'
    _description = "Sauvegarde du planning congé"

    estimed_date_leave = fields.Date('Date prévsionnelle de départ en congés', )
    estimated_date_return_leave = fields.Date('Date prévsionnelle de retour de congés', )
    date_return_last_holidays = fields.Date('Date de retour congés')
    number_days_estimed_holidays = fields.Char('Nombre de jours de congés estimés')
    employee_id = fields.Many2one('hr.employee', 'Employe')


class SaveStockHoliday(models.Model):
    _name = 'hr_holidays_custom.save_stock_holiday'
    _description = "Sauvegarde des stocks congés"

    name = fields.Char('Stock congé')
    number_days = fields.Integer("Nombre de jours")
    employee_id = fields.Many2one('hr.employee', 'Employé')
