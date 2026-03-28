{
    'name': 'Personnalisation des modules Employé et Contrat',
    'version': '19.0.1.0.0',
    'summary': "Ce module permet de personnaliser le module employé natif Odoo afin de l'adapter aux réalités Ivoiriennes",
    'description': 'Description',
    'category': 'Human Resources/Employees',
    'author': 'Djakaridja Traore',
    'website': 'https://www.neuronestech.com/',
    'license': 'LGPL-3',
    'depends': ['mail', 'hr', 'hr_payroll', 'documents', 'report_xlsx'],
    'data': [
        'data/res_country_data.xml',
        'data/mail_template_data.xml',
        'data/cron_data.xml',

        'views/hr_family_child_view.xml',
        'views/hr_family_mergency_view.xml',
        'views/professional_mission_view.xml',
        'views/work_accident_view.xml',
        'views/hr_employee_view_inherit.xml',
        'views/res_partner_bank_view_inherit.xml',
        'views/hr_department_view_inherit.xml',
        'views/hr_version_view_inherit.xml',
        'views/res_company_view_inherit.xml',

        'views/res_config_setting_view_inherit.xml',

        'wizards/employee_resignation_wizard_view.xml',
        'wizards/work_accident_wizard_view.xml',
        'wizards/recruits_per_period_wizard_view.xml',
        'wizards/employee_list_wizard_view.xml',
        'views/hr_custom_menu.xml',

        'reports/templates/layout_report_template_header.xml',
        'reports/templates/layout_report_template_footer.xml',
        'reports/templates/layout_report_template_pagination_footer.xml',
        'reports/templates/layout_report_paper_format_landscape.xml',
        'reports/templates/layout_report_human_ressources.xml',
        'reports/templates/layout_report_employee.xml',

        'reports/report_work_certificate.xml',
        'reports/report_recruits_per_period.xml',
        'reports/report_employee_resignation_pdf.xml',
        'reports/report_work_accident.xml',
        'reports/report_employee_list.xml',
        'reports/report_view.xml',

        'security/ir.model.access.csv',

    ],
    'demo': ['Demo'],
    'installable': True,
    'application': True,
    'auto_install': False

}
