from odoo import fields, models, api
import time


class PayrollDisa(models.Model):
    _name = 'hr_payroll_custom.statement_disa'
    _description = 'DISA'

    name = fields.Char('Référence', )
    date_from = fields.Date("Date de début", default=time.strftime('%Y-01-01'))
    date_to = fields.Date("Date de fin", default=time.strftime('%Y-12-31'))
    company_id = fields.Many2one('res.company', 'Société', default=1)
    seq_disa = fields.Char('Sequence')
    total_general_brut = fields.Float('Total brut annuel', compute='_compute', store=True)
    total_general_retraite = fields.Float('Total retraite', compute='_compute', store=True)
    total_cotisation_pf_am = fields.Float(compute='_compute', store=True)
    disa_line_ids = fields.One2many('hr_payroll_custom.statement_disa_line', 'disa_id', 'Ligne disa')
    cumul_contribution_line_ids = fields.One2many('hr_payroll_custom.cumul_contribution_line', 'disa_id', 'Cumul des cotisations')
    cnps_monthly_ids = fields.One2many('hr_payroll_custom.cnps_monthly', 'disa_id', 'CNPS Mensuel')
    contribution_scheme = fields.Float('Total cotisation', compute='get_contribution_scheme', store=True)
    total_cnps_monthly = fields.Float('Total cnps', compute='get_total_cnps_monthly', store=True)

    def computeDisa(self):
        res = []
        employees = self.env['hr.employee'].search(
            [('company_id', '=', self.company_id.id), ('active', 'in', (True, False)),
             ('type', 'in', ('h', 'j', 'm'))], order='identification_id')
        if employees:
            for emp in employees:
                employee_type = 'M'
                if emp.type == 'j':
                    employee_type = 'J'
                if emp.type == 'h':
                    employee_type = 'H'
                val = {
                    'employee_id': emp.id,
                    'disa_id': self.id,
                    'num_cnps': emp.identification_cnps or '',
                    'birthday': emp.birthday.strftime("%d/%m/%Y") if emp.birthday else '',
                    'hiring_date': emp.hiring_date.strftime("%d/%m/%Y") if emp.hiring_date else '',
                    'date_of_departure': emp.departure_date.strftime("%d/%m/%Y") if emp.departure_date else '',
                    'employee_type': employee_type,
                    'work_time': emp.getTotalRubriqueByPeriod('CON', self.date_from, self.date_to) / 30,
                    'total_gross': emp.getTotalRubriqueByPeriod('BRUT', self.date_from, self.date_to),
                    'other_gross': emp.getBaseATPF('BRUT', self.date_from, self.date_to),
                    'cnps_gross': emp.getAmountRubriqueByPeriod('CNPS', self.date_from, self.date_to),
                    'contribution': '1234',
                    'comment': ""
                }
                res.append(val)
        self.disa_line_ids.unlink()
        self.env['hr_payroll_custom.statement_disa_line'].create(res)

        cnps_monthly = self.env['hr_payroll_custom.cnps_monthly'].search([('date_from', '>=', self.date_from),
                                                           ('date_to', '<=', self.date_to)])
        cnps_monthly_ids = []
        for cnps_month in cnps_monthly:
            cnps_month.disa_id = self.id
            cnps_monthly_ids.append(cnps_month.id)

        contribution_scheme = self.env['hr_payroll_custom.cnps_cotisation_template'].search([], order='sequence')

        if contribution_scheme:
            contribution_scheme_data = []
            for line in contribution_scheme:
                vals = {
                    'name': line.name,
                    'rate': line.rate,
                    'amount_submitted': self.total_general_retraite if line.type == 'cnps' else self.total_cotisation_pf_am,
                    'amount': (line.rate * self.total_general_retraite) / 100 if line.type == 'cnps' else
                    (line.rate * self.total_cotisation_pf_am) / 100,
                    'disa_id': self.id,
                }
                contribution_scheme_data.append(vals)
            self.cumul_contribution_line_ids.unlink()
            self.env['hr_payroll_custom.cumul_contribution_line'].create(contribution_scheme_data)

    @api.depends('cumul_contribution_line_ids')
    def get_contribution_scheme(self):
        if self.cumul_contribution_line_ids:
            contribution_scheme = 0
            for line in self.cumul_contribution_line_ids:
                contribution_scheme += line.amount
            self.contribution_scheme = contribution_scheme

    @api.depends('cnps_monthly_ids')
    def get_total_cnps_monthly(self):
        if self.cnps_monthly_ids:
            total_cnps_monthly = 0.0
            for line in self.cnps_monthly_ids:
                total_cnps_monthly += line.total_amount_of_contributions
            self.total_cnps_monthly = total_cnps_monthly

    @api.depends('disa_line_ids')
    def _compute(self):
        if self.disa_line_ids:
            self.total_general_brut = sum(x.total_gross for x in self.disa_line_ids)
            self.total_cotisation_pf_am = sum(y.other_gross for y in self.disa_line_ids)
            self.total_general_retraite = sum(z.cnps_gross for z in self.disa_line_ids)
        else:
            pass


class PayrollDisaLine(models.Model):
    _name = 'hr_payroll_custom.statement_disa_line'
    _description = "Lignes de la DISA"

    name = fields.Char('Nom et Prénoms', related="employee_id.name")
    identification_id = fields.Char('Matricule', related="employee_id.identification_id", store=True)
    num_cnps = fields.Char('N° C.N.P.S')
    birthday = fields.Char('Date de naissance')
    hiring_date = fields.Char('Date embauche')
    date_of_departure = fields.Char('Date de départ')
    employee_type = fields.Char('Type employé')
    work_time = fields.Integer('Temps de travail')
    total_gross = fields.Float('Brut total')
    other_gross = fields.Float('Autre brut')
    cnps_gross = fields.Float('Brut CNPS')
    natural_advantage = fields.Float('Avantage en nature')
    contribution = fields.Char('Cotisation')
    comment = fields.Char('Commentaire')
    employee_id = fields.Many2one('hr.employee', 'Employé')
    disa_id = fields.Many2one('hr_payroll_custom.statement_disa', 'DISA')


class CumulContributionLine(models.Model):
    _name = "hr_payroll_custom.cumul_contribution_line"
    _description = "Cumul des cotisations"

    name = fields.Char('Designation')
    amount_submitted = fields.Float('Salaire soumis à cotisation')
    rate = fields.Float('Taux')
    amount = fields.Float('Montant')
    disa_id = fields.Many2one('hr_payroll_custom.statement_disa', 'DISA')


class CnpsMonthly(models.Model):
    _inherit = "hr_payroll_custom.cnps_monthly"

    disa_id = fields.Many2one('hr_payroll_custom.statement_disa', 'DISA')
