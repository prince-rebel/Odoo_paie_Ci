# -*- coding: utf-8 -*-
"""
Migration Odoo 17 → 19 : hr.contract → hr.version
Ce script migre les clés étrangères contract_id vers version_id dans les tables
hr_payroll_custom qui référencent l'ancien modèle hr.contract.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    # Vérifier si la colonne contract_id existe encore sur fixed_premiums
    cr.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'hr_payroll_custom_fixed_premiums'
        AND column_name = 'contract_id'
    """)
    if cr.fetchone():
        _logger.info("Migration fixed_premiums : contract_id → version_id")
        cr.execute("""
            UPDATE hr_payroll_custom_fixed_premiums fp
            SET version_id = hv.id
            FROM hr_version hv
            WHERE fp.contract_id IS NOT NULL
              AND hv.employee_id = (
                  SELECT employee_id FROM hr_contract WHERE id = fp.contract_id
              )
              AND hv.is_current = TRUE
        """)
        rows = cr.rowcount
        _logger.info("fixed_premiums : %d lignes migrées", rows)

    # Vérifier si la colonne contract_id existe encore sur balance_any_account
    cr.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'hr_payroll_custom_balance_any_account'
        AND column_name = 'contract_id'
    """)
    if cr.fetchone():
        _logger.info("Migration balance_any_account : contract_id → version_id")
        cr.execute("""
            UPDATE hr_payroll_custom_balance_any_account ba
            SET version_id = hv.id
            FROM hr_version hv
            WHERE ba.contract_id IS NOT NULL
              AND hv.employee_id = (
                  SELECT employee_id FROM hr_contract WHERE id = ba.contract_id
              )
              AND hv.is_current = TRUE
        """)
        rows = cr.rowcount
        _logger.info("balance_any_account : %d lignes migrées", rows)
