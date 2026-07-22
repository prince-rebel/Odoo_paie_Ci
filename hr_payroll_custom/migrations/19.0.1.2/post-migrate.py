# -*- coding: utf-8 -*-
"""
Migration 19.0.1.1 -> 19.0.1.2

Les règles AUTRES_PRIM_IMP et AUTRES_PRIM_NI sommaient jusqu'ici toutes les
primes libres dans une seule ligne au libellé générique ("Autres primes
imposables" / "Autres primes non imposables"), masquant le nom de chaque
prime individuelle sur le bulletin.

On bascule sur le mécanisme natif Odoo `same_type_input_lines` (prévu à
l'origine pour agréger plusieurs entrées partageant le même code) : chaque
prime libre est désormais injectée avec le même input_type_id "bucket"
partagé (cf. hr_payslip_input_type_data.xml : input_type_autres_prim_imp /
input_type_autres_prim_ni), ce qui déclenche automatiquement une ligne de
bulletin distincte par prime, affichée sous son propre nom via result_name.

Ces deux règles sont dans hr_salary_rule_data.xml, chargé avec
noupdate="1" : comme pour la migration précédente, il faut forcer la mise à
jour en base par script, une simple modification du fichier XML ne suffit
pas pour les bases déjà installées.
"""
import logging

_logger = logging.getLogger(__name__)

AUTRES_PRIM_IMP_CONDITION = "result = 'AUTRES_PRIM_IMP' in inputs"
AUTRES_PRIM_IMP_AMOUNT = (
    "line = inputs['AUTRES_PRIM_IMP']\n"
    "result = line.amount\n"
    "result_name = line.name"
)
AUTRES_PRIM_NI_CONDITION = "result = 'AUTRES_PRIM_NI' in inputs"
AUTRES_PRIM_NI_AMOUNT = (
    "line = inputs['AUTRES_PRIM_NI']\n"
    "result = line.amount\n"
    "result_name = line.name"
)


def migrate(cr, version):
    if not version:
        return

    cr.execute("""
        SELECT imd.name, imd.res_id
        FROM ir_model_data imd
        WHERE imd.module = 'hr_payroll_custom'
          AND imd.model = 'hr.salary.rule'
          AND imd.name IN ('salary_rule_autres_prim_imp', 'salary_rule_autres_prim_ni')
    """)
    rule_ids_by_name = dict(cr.fetchall())

    if 'salary_rule_autres_prim_imp' in rule_ids_by_name:
        cr.execute(
            "UPDATE hr_salary_rule SET condition_python = %s, amount_python_compute = %s WHERE id = %s",
            (AUTRES_PRIM_IMP_CONDITION, AUTRES_PRIM_IMP_AMOUNT, rule_ids_by_name['salary_rule_autres_prim_imp']),
        )
        _logger.info(
            "Migration 1.2 : AUTRES_PRIM_IMP (id=%s) affiche désormais chaque prime par son nom",
            rule_ids_by_name['salary_rule_autres_prim_imp'],
        )

    if 'salary_rule_autres_prim_ni' in rule_ids_by_name:
        cr.execute(
            "UPDATE hr_salary_rule SET condition_python = %s, amount_python_compute = %s WHERE id = %s",
            (AUTRES_PRIM_NI_CONDITION, AUTRES_PRIM_NI_AMOUNT, rule_ids_by_name['salary_rule_autres_prim_ni']),
        )
        _logger.info(
            "Migration 1.2 : AUTRES_PRIM_NI (id=%s) affiche désormais chaque prime par son nom",
            rule_ids_by_name['salary_rule_autres_prim_ni'],
        )
