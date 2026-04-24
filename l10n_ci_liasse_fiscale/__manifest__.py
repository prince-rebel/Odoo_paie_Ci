# -*- coding: utf-8 -*-
{
    'name': 'Ivory Coast - Liasse Fiscale SYSCOHADA',
    'version': '1.0',
    'author': 'Djakaridja Traoré',
    'description': """
Liasse Fiscale DGI Côte d'Ivoire — SYSCOHADA révisé
=====================================================
- Tableau des Flux de Trésorerie (TFT)
- 39 Notes annexes obligatoires
- Suppléments DGI CI (SUPPL1-7, COMP-CHARGES, COMP-TVA)
    """,
    'category': 'Accounting/Localizations/Reporting',
    'depends': [
        'l10n_syscohada_reports',
        'l10n_ci_reports',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/syscohada_tft.xml',
        'data/notes_immobilisations.xml',
        'data/notes_actif_passif.xml',
        'data/notes_charges_produits.xml',
        'data/notes_resultats.xml',
        'views/l10n_ci_liasse_wizard_views.xml',
        'views/l10n_ci_reports_menus.xml',
    ],
    'auto_install': False,
    'license': 'OEEL-1',
}
