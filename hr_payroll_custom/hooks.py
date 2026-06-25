# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    """
    On first install: migrate any existing FixedPremiums lines that use input_type_id directly
    (legacy TRSP, ASM, CMU lines) to use prime_type_id.
    """
    _migrate_fixed_premiums(env)


def _migrate_fixed_premiums(env):
    prime_types = env['hr_payroll_custom.prime_type'].search([
        ('input_type_id', '!=', False)
    ])
    prime_by_input_id = {pt.input_type_id.id: pt.id for pt in prime_types}

    if not prime_by_input_id:
        return

    lines = env['hr_payroll_custom.fixed_premiums'].search([
        ('prime_type_id', '=', False),
        ('input_type_id', 'in', list(prime_by_input_id.keys())),
    ])
    for line in lines:
        pt_id = prime_by_input_id.get(line.input_type_id.id)
        if pt_id:
            line.write({'prime_type_id': pt_id})
