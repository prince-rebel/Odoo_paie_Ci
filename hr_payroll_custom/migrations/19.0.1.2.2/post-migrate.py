# -*- coding: utf-8 -*-
"""
Migration 19.0.1.2.1 -> 19.0.1.2.2

Bug de double comptage des indemnités non imposables (transport, logement,
représentation, ...) dans le net à payer :

- NET_PAIE (salary_rule_net_paie) partait de BRUT_TOTAL, qui inclut déjà les
  indemnités non imposables (catégorie INDMNI).
- NET (salary_rule_net) réinjecte ensuite categories['INDMNI'] en supposant,
  lui, que NET_PAIE ne contenait que le brut imposable (BRUT).

Ces deux hypothèses contradictoires faisaient que chaque indemnité non
imposable était ajoutée deux fois au net payé (une fois via BRUT_TOTAL dans
NET_PAIE, une fois via l'ajout explicite dans NET) : le net à payer était
gonflé du montant total des indemnités non imposables sur chaque bulletin.

NET_PAIE doit se baser sur BRUT (et non BRUT_TOTAL), NET se chargeant déjà
de rajouter les indemnités non imposables ensuite.

Comme pour les migrations précédentes (19.0.1.1, 19.0.1.2, 19.0.1.2.1), cette
règle est chargée avec noupdate="1" : il faut forcer la mise à jour en base.
"""
import logging

_logger = logging.getLogger(__name__)

NET_PAIE_FORMULA = "result = round(BRUT) - categories['IMP_SAL'] - result_rules['Maladie']['total']"


def migrate(cr, version):
    if not version:
        return

    cr.execute("""
        SELECT imd.name, imd.res_id
        FROM ir_model_data imd
        WHERE imd.module = 'hr_payroll_custom'
          AND imd.model = 'hr.salary.rule'
          AND imd.name = 'salary_rule_net_paie'
    """)
    row = cr.fetchone()

    if row:
        _, rule_id = row
        cr.execute(
            "UPDATE hr_salary_rule SET amount_python_compute = %s WHERE id = %s",
            (NET_PAIE_FORMULA, rule_id),
        )
        _logger.info(
            "Migration 1.2.2 : NET_PAIE (id=%s) basé sur BRUT au lieu de BRUT_TOTAL "
            "(correction du double comptage des indemnités non imposables)",
            rule_id,
        )
