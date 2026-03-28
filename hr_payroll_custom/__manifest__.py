{
    'name': 'Personnalisation du module Paye',
    'version': '19.0.1.0.0',
    'summary': "Ce module permet de personnaliser le module paye natif afin de l'adapter aux réalités Ivoiriennes",
    'description': """
    - Prise en compte des primes dans le contrat
    - Prise en compte des déclarations fiscales et sociales""",
    'category': 'Human Resources/Payroll',
    'author': 'Djakaridja Traore',
    'website': 'https://www.neuronestech.com/',
    'license': 'LGPL-3',
    'depends': ['hr_custom', 'hr_holidays_custom', 'hr_payroll', 'hr_payroll_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_structure_data.xml',
        'data/hr_salary_rule_category_data.xml',
        'data/hr_salary_rule_data.xml',

        'wizards/payroll_variables_wizard_view.xml',
        'wizards/benefits_in_kind_301_view.xml',
        'wizards/benefits_in_kind_disa_view.xml',
        'wizards/inverse_calculation_view.xml',

        'views/hr_employee_view_inherit.xml',
        'views/hr_version_view_inherit.xml',
        'views/hr_payroll_view_inherit.xml',
        'views/hr_leave_view_inherit.xml',
        'views/salary_rule_view_inherit.xml',
        'views/employee_variation_view.xml',
        'views/res_company_view_inherit.xml',
        'views/cnps_settings_view.xml',
        'views/fdfp_settings_view.xml',
        'views/cnps_monthly_view.xml',
        'views/cmu_monthly_view.xml',
        'views/fdfp_monthly_view.xml',
        'views/its_monthly_view.xml',
        'views/statement_301_view.xml',
        'views/statement_disa_view.xml',
        'views/balance_any_account_view.xml',


        'wizards/pay_book_wizard_view.xml',
        'wizards/payroll_by_post_wizard_view.xml',
        'wizards/salary_variation_wizard_view.xml',



        'views/hr_payroll_custom_menu.xml',

        'reports/templates/payslip_layout.xml',
        'reports/templates/payroll_report_layout.xml',
        'reports/templates/its_monthly_layout.xml',
        'reports/templates/paperformat_template.xml',
        'reports/templates/statement_301_layout.xml',
        'reports/templates/fdfp_monthly_layout.xml',
        'reports/report_employee_absent_previous_pay.xml',
        'reports/report_change_in_paid_staffs.xml',
        'reports/report_payslip.xml',
        'reports/report_payroll_by_post.xml',
        'reports/report_its_monthly.xml',
        'reports/report_statement_301.xml',
        'reports/report_list_contributors_disa.xml',
        'reports/report_disa_supplement.xml',
        'reports/report_fdfp_monthly.xml',
        'reports/report_cnps_monthly.xml',
        'reports/report_view.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
