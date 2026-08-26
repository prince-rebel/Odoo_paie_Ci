# -*- coding: utf-8 -*-
"""
Migration 19.0.1.2 -> 19.0.1.2.1

Deux bugs restaient sur les règles ITS, indépendants du fix BRUT_TOTAL déjà
apporté en 19.0.1.1 :

1. ITS_P (salary_rule_its_p, part patronale 1,2%) était basée sur BRUT_TOTAL
   au lieu de BRUT : elle incluait donc à tort les primes non imposables
   (transport, logement, etc.) dans la base de calcul de la cotisation
   patronale, contrairement à toutes les autres cotisations patronales du
   bulletin (Accidents du travail, Prestations familiales, Taxe
   d'apprentissage, Formation professionnelle) qui utilisent BASE/BRUT.

2. NET_IMP (salary_rule_net_imp) contenait la même faute de frappe que
   BRUT_TOTAL avant sa correction en 19.0.1.1 (espace en trop dans
   categories.get("INDMNI ")), non couverte par cette migration précédente.

Comme pour les migrations 19.0.1.1/19.0.1.2, ces règles sont chargées avec
noupdate="1" : une modification du fichier XML seul ne suffit pas pour les
bases déjà installées, d'où ce script qui force la mise à jour en base.
"""
import logging

_logger = logging.getLogger(__name__)

ITS_P_BASE = 'BRUT'
NET_IMP_FORMULA = 'result = round(BRUT) - round(RET) + round(categories.get("INDMNI", 0))'


def migrate(cr, version):
    if not version:
        return

    cr.execute("""
        SELECT imd.name, imd.res_id
        FROM ir_model_data imd
        WHERE imd.module = 'hr_payroll_custom'
          AND imd.model = 'hr.salary.rule'
          AND imd.name IN ('salary_rule_its_p', 'salary_rule_net_imp')
    """)
    rule_ids_by_name = dict(cr.fetchall())

    if 'salary_rule_its_p' in rule_ids_by_name:
        cr.execute(
            "UPDATE hr_salary_rule SET amount_percentage_base = %s WHERE id = %s",
            (ITS_P_BASE, rule_ids_by_name['salary_rule_its_p']),
        )
        _logger.info(
            "Migration 1.2.1 : ITS_P (id=%s) base corrigée BRUT_TOTAL -> BRUT",
            rule_ids_by_name['salary_rule_its_p'],
        )

    if 'salary_rule_net_imp' in rule_ids_by_name:
        cr.execute(
            "UPDATE hr_salary_rule SET amount_python_compute = %s WHERE id = %s",
            (NET_IMP_FORMULA, rule_ids_by_name['salary_rule_net_imp']),
        )
        _logger.info(
            "Migration 1.2.1 : correction du bug INDMNI (espace en trop) sur NET_IMP (id=%s)",
            rule_ids_by_name['salary_rule_net_imp'],
        )
