# -*- encoding: utf-8 -*-

from odoo import models, fields, api
from itertools import groupby
import logging

_logger = logging.getLogger(__name__)


class ItsMonthly(models.Model):
    _name = 'hr_payroll_custom.its_monthly'
    _description = "ITS"

    def _get_effectif_employee(self):
        for rec in self:
            ids_slip = []
            rec.total_number = 0
            rec.total_mt_a_payer = 0
            slip_obj = self.env['hr.payslip']
            all_slips = slip_obj.search([('date_from', '>=', rec.date_from), ('date_to', '<=', rec.date_to),
                                         ('company_id', '=', rec.company_id.id),
                                         ('state', 'in', ('validated', 'paid'))])
            if all_slips:
                payslip_lines = self.env['hr.payslip.line'].search([('slip_id','in',all_slips.ids),
                                                                    ('code', '=', 'ITS'),
                                                                    ('company_id', '=', rec.company_id.id)])
                cumul_amount = 0
                for line in payslip_lines:
                     cumul_amount += line.total

                rec.total_its_employee = cumul_amount
                self.env.cr.execute("SELECT COUNT (distinct(id)), nature_employe FROM hr_employee WHERE "
                                    "id IN (SELECT employee_id FROM hr_payslip WHERE id=ANY(%s)) "
                                    "GROUP BY nature_employe", (all_slips.ids,))
                result = self.env.cr.dictfetchall()
                if result:
                    rec.total_number_local = 0
                    rec.total_number_expat = 0
                    for res in result:
                        if res['nature_employe'] == 'local':
                            rec.total_number_local = res['count']
                        elif res['nature_employe'] == 'expat':
                            rec.total_number_expat = res['count']
                        else:
                            pass
                    rec.total_number = rec.total_number_local + rec.total_number_expat
                for slip in all_slips:
                    ids_slip.append(slip.id)
            return ids_slip

    def _get_revenu_employee(self, all_slips):
        local_ids = []
        expat_ids = []

        if all_slips:
            self.total_brut_imposable_expat = 0
            self.total_brut_imposable_local = 0
            self.total_mt_a_payer_expat = 0
            self.total_mt_a_payer_local = 0
            slips_tuple = tuple(all_slips) if len(all_slips) > 1 else f"({all_slips[0]})"
            self.env.cr.execute(f"SELECT distinct(id), nature_employe FROM hr_employee WHERE id IN (SELECT employee_id "
                                f"FROM hr_payslip WHERE id in {slips_tuple}) GROUP BY nature_employe, id")
            result = self.env.cr.dictfetchall()
            if result:
                for x in result:
                    if x['nature_employe'] == 'local':
                        local_ids.append(x['id'])
                    elif x['nature_employe'] == 'expat':
                        expat_ids.append(x['id'])
                    else:
                        pass

            #Vérifier s'il y a ITS_P dans les bulletins
            self.env.cr.execute("SELECT sum(total) FROM hr_payslip_line WHERE slip_id=ANY(%s) AND code='ITS_P'",
                                (all_slips,))
            result = self.env.cr.fetchone()

            if result[0]:
                if local_ids:

                    self.env.cr.execute("SELECT sum(total) FROM hr_payslip_line WHERE slip_id=ANY(%s) AND code='BRUT'"
                                        " AND employee_id=ANY(%s)",
                                        (all_slips, local_ids))
                    result = self.env.cr.fetchone()
                    if result:
                        self.total_brut_imposable_local = result[0]
                        total_mt_a_payer_local = round(self.total_brut_imposable_local * 0.012)
                        self.total_mt_a_payer_local = total_mt_a_payer_local if \
                            self.total_its_employee == total_mt_a_payer_local else self.total_its_employee
                if expat_ids:
                    self.env.cr.execute("SELECT sum(total) FROM hr_payslip_line WHERE slip_id=ANY(%s) AND code='BRUT'"
                                        " AND employee_id=ANY(%s)",
                                        (all_slips, expat_ids))
                    result = self.env.cr.fetchone()
                    if result:
                        self.total_brut_imposable_expat = result[0]
                        self.total_mt_a_payer_expat = round(self.total_brut_imposable_expat * 0.104)
            self.total_mt_a_payer = self.total_mt_a_payer_local + self.total_mt_a_payer_expat

    def _compute_all_total(self):
        for rec in self:
            # ITS unifié depuis la réforme 2024 — CN et IGR fusionnés dans ITS
            rec.total_retenu_employee = rec.total_its_employee
            rec.amount_total = rec.total_retenu_employee + rec.total_mt_a_payer

    name = fields.Char('Nom', required=True, size=155)
    date_from = fields.Date('Debut mois', required=True)
    date_to = fields.Date('Fin mois', required=True)
    company_id = fields.Many2one('res.company', 'Société', default=lambda self: self.env.user.company_id.id, required=1)
    total_its_employee = fields.Integer("ITS", help="Impôt sur traitements, salaires, pensions, rentes viagères (IS)",
                                        default=0)
    total_igr_employee = fields.Integer("IGR", help="Impôt Général sur le revenu (IGR)", default=0, )
    total_cn = fields.Integer("CN", help="Contribution national", default=0)
    total_retenu_employee = fields.Integer("TOTAL DES RETENUES AUX SALARIES", compute='_compute_all_total', default=0,
                                           store=True)
    total_number_local = fields.Integer("Effectif locaux", compute='_get_effectif_employee', default=0, store=True)
    total_brut_imposable_local = fields.Integer("Total salaire BRUTS des locaux", compute='_get_revenu_employee',
                                                default=0, store=True)
    total_mt_a_payer_local = fields.Integer("Total montant à payer local", compute='_get_revenu_employee', default=0,
                                            store=True)
    total_number_expat = fields.Integer("Effectif Expatriés", compute='_get_effectif_employee', default=0, store=True)
    total_brut_imposable_expat = fields.Integer("Total salaire BRUTS des expatriés", compute='_get_revenu_employee',
                                                default=0, store=True)
    total_mt_a_payer_expat = fields.Integer("Total montant à payer expatrié", compute='_get_revenu_employee', default=0,
                                            store=True)
    total_number = fields.Integer("Effectif total", compute='_get_effectif_employee', default=0, store=True)
    total_mt_a_payer = fields.Integer("Total montant à payer employeur", compute='_get_revenu_employee', default=0,
                                      store=True)
    amount_total = fields.Integer("TOTAL A PAYER", compute='_compute_all_total', default=0, store=True)

    def compute_its_monthly(self):
        for rec in self:
            all_slips = rec._get_effectif_employee()
            rec._get_revenu_employee(all_slips)
            if all_slips:
                # CN et IGR fusionnés dans ITS depuis la réforme 2024 — les champs restent à 0
                rec.total_cn = 0
                rec.total_igr_employee = 0
                rec._compute_all_total()
