from odoo import fields, models, api


class SalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    appears_on_payroll = fields.Boolean(string='Apparaît sur le Livre de paie', default=False,
                                        help="Utilisé pour afficher la règle salariale sur le livre de paie")
    imputation_type = fields.Selection([('earnings', 'Est un gain'), ('deductions', 'Est une retenue')],
                                       string="Type imputation",
                                       help="Utiliser dans la génération de certains rapports tel que le rapport "
                                            "des cumuls des rubriques par période")
    is_tax_fdfp = fields.Boolean("Est un impôt FDFP", default=False)
    natural_advantage = fields.Boolean('Avantage en nature', default=False)
    use_to_compute_leave = fields.Boolean('Utilisé pour le calcul des allocations congés',
                                          help="Cochez si cette règle doit être utilisée pour le calcul de "
                                               "l'allocation des congés")
