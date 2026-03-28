{
    'name': 'Personnalisation du module Congé',
    'version': '19.0.1.0.0',
    'summary': "Ce module permet de personnaliser le module congé natif afin de l'adapter aux réalités Ivoiriennes",
    'description': """
    - Prise en compte des prévision congés
    - Prise en compte des attestion de reprise de service
    - Prise en compte de la gestion des historiques des stocks congés et des prévisions congés""",
    'category': 'Human Resources/Employees',
    'author': 'Djakaridja Traore',
    'website': 'https://www.neuronestech.com/',
    'license': 'LGPL-3',
    'depends': ['hr_holidays','hr_custom'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'data/cron_data.xml',
        'views/resumption_of_service_view.xml',
        'views/hr_employee_view_inherit.xml',
        'views/holiday_forecast.xml',
        'views/hr_leave_type_inherit.xml',
        'views/legal_holidays_view.xml',
        'views/planning_holidays_view.xml',
        # 'views/res_config_setting_view_inherit.xml',


        'wizards/detailed_report_holidays_wizard_view.xml',
        'wizards/planning_report_holidays_wizard_view.xml',

        
        'views/hr_holidays_custom_menu.xml',

        'reports/report_resumption_of_service.xml',
        'reports/report_detailed_report_holiday.xml',
        'reports/report_planning_holidays.xml',
        'reports/report_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
