# -*- coding: utf-8 -*-
"""
Migration 19.0.1.0 -> 19.0.1.1

Les règles salariales de hr_salary_rule_data.xml sont chargées avec
noupdate="1" : une fois créées en base, les modifications faites dans le
fichier XML ne sont JAMAIS répercutées par une simple mise à jour de module.

Deux règles étaient restées bloquées sur une ancienne formule, avant même
l'ajout du mécanisme de "primes libres" (imposables/non imposables) :

1. BRUT (salary_rule_brut) utilisait encore une addition explicite
   (BASE + SURSA + PANC) au lieu de l'agrégation générique par catégorie
   (categories['PRIM']). Résultat : toute prime de la catégorie "Primes"
   qui n'est pas explicitement citée dans ce vieux code (GRATIF, CONG,
   et maintenant les primes libres) était silencieusement ignorée dans
   le Brut imposable.

2. BRUT_TOTAL (salary_rule_brut_total) contenait une faute de frappe
   (espace en trop : categories.get("INDMNI ") au lieu de "INDMNI"),
   qui faisait que le Brut Total ignorait systématiquement toutes les
   indemnités non imposables (Transport, Logement, Indemnité de
   représentation, etc.) alors que c'est justement leur rôle d'y figurer.

Ce script force la mise à jour de ces deux règles déjà installées,
pour toutes les bases qui ont ce module depuis avant la version 1.1.
"""
import logging

_logger = logging.getLogger(__name__)

BRUT_FORMULA = "result = round(categories['BASIC'] + categories['SURSA'] + categories['PRIM'] + categories['HSUPP'])"
BRUT_TOTAL_FORMULA = 'result = round(BRUT) + (categories.get("INDMNI") or 0)'


def migrate(cr, version):
    if not version:
        return

    cr.execute("""
        SELECT imd.name, imd.res_id
        FROM ir_model_data imd
        WHERE imd.module = 'hr_payroll_custom'
          AND imd.model = 'hr.salary.rule'
          AND imd.name IN ('salary_rule_brut', 'salary_rule_brut_total')
    """)
    rule_ids_by_name = dict(cr.fetchall())

    if 'salary_rule_brut' in rule_ids_by_name:
        cr.execute(
            "UPDATE hr_salary_rule SET amount_python_compute = %s WHERE id = %s",
            (BRUT_FORMULA, rule_ids_by_name['salary_rule_brut']),
        )
        _logger.info(
            "Migration 1.1 : formule BRUT (id=%s) mise à jour vers l'agrégation par catégorie",
            rule_ids_by_name['salary_rule_brut'],
        )

    if 'salary_rule_brut_total' in rule_ids_by_name:
        cr.execute(
            "UPDATE hr_salary_rule SET amount_python_compute = %s WHERE id = %s",
            (BRUT_TOTAL_FORMULA, rule_ids_by_name['salary_rule_brut_total']),
        )
        _logger.info(
            "Migration 1.1 : correction du bug INDMNI (espace en trop) sur BRUT_TOTAL (id=%s)",
            rule_ids_by_name['salary_rule_brut_total'],
        )
