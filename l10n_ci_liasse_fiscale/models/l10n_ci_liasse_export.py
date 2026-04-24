# -*- coding: utf-8 -*-
from odoo import models, fields, api

# Mapping: DGI field code → (odoo_report_line_code, expression_label, period)
# period: 'current' or 'previous'
ACTIF_MAPPING = {}
for alias in ['AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AP','AQ','AR','AS','AZ',
              'BA','BB','BG','BH','BI','BJ','BK','BQ','BR','BS','BT','BU','BZ']:
    code = f'SYSCOHADA_{alias}'
    ACTIF_MAPPING[f'NO_ACTIF_{alias}_1'] = (code, 'gross', 'current')
    ACTIF_MAPPING[f'NO_ACTIF_{alias}_2'] = (code, 'depr',  'current')
    ACTIF_MAPPING[f'NO_ACTIF_{alias}_3'] = (code, 'balance','current')
    ACTIF_MAPPING[f'NO_ACTIF_{alias}_4'] = (code, 'balance','previous')

PASSIF_MAPPING = {}
for alias in ['CA','CB','CD','CE','CF','CG','CH','CJ','CL','CM','CP',
              'DA','DB','DC','DD','DF','DH','DI','DJ','DK','DM','DN','DP',
              'DQ','DR','DT','DV','DZ']:
    code = f'SYSCOHADA_{alias}'
    PASSIF_MAPPING[f'NO_PASSIF_{alias}_1'] = (code, 'balance','current')
    PASSIF_MAPPING[f'NO_PASSIF_{alias}_2'] = (code, 'balance','previous')

RESULTAT_MAPPING = {
    'NO_RESULTAT_TA_1': ('SYSCOHADA_Ventes_de_marchandises',   'balance','current'),
    'NO_RESULTAT_TA_2': ('SYSCOHADA_Ventes_de_marchandises',   'balance','previous'),
    'NO_RESULTAT_RA_1': ('SYSCOHADA_Achats_de_marchandises',   'balance','current'),
    'NO_RESULTAT_RA_2': ('SYSCOHADA_Achats_de_marchandises',   'balance','previous'),
    'NO_RESULTAT_RB_1': ('SYSCOHADA_Variation_de_stocks_mar',  'balance','current'),
    'NO_RESULTAT_RB_2': ('SYSCOHADA_Variation_de_stocks_mar',  'balance','previous'),
    'NO_RESULTAT_XA_1': ('SYSCOHADA_Marge_commerciale ',       'balance','current'),
    'NO_RESULTAT_XA_2': ('SYSCOHADA_Marge_commerciale ',       'balance','previous'),
    'NO_RESULTAT_TB_1': ('SYSCOHADA_Ventes_prod_fab',          'balance','current'),
    'NO_RESULTAT_TB_2': ('SYSCOHADA_Ventes_prod_fab',          'balance','previous'),
    'NO_RESULTAT_TC_1': ('SYSCOHADA_Travaux_services_vn',      'balance','current'),
    'NO_RESULTAT_TC_2': ('SYSCOHADA_Travaux_services_vn',      'balance','previous'),
    'NO_RESULTAT_TD_1': ('SYSCOHADA_Produits_accessoires',     'balance','current'),
    'NO_RESULTAT_TD_2': ('SYSCOHADA_Produits_accessoires',     'balance','previous'),
    'NO_RESULTAT_XB_1': ('SYSCOHADA_Chiffres_affaires',        'balance','current'),
    'NO_RESULTAT_XB_2': ('SYSCOHADA_Chiffres_affaires',        'balance','previous'),
    'NO_RESULTAT_TE_1': ('SYSCOHADA_Produc_stck',              'balance','current'),
    'NO_RESULTAT_TE_2': ('SYSCOHADA_Produc_stck',              'balance','previous'),
    'NO_RESULTAT_TF_1': ('SYSCOHADA_Produc_immo',              'balance','current'),
    'NO_RESULTAT_TF_2': ('SYSCOHADA_Produc_immo',              'balance','previous'),
    'NO_RESULTAT_TG_1': ('SYSCOHADA_Sub_exp',                  'balance','current'),
    'NO_RESULTAT_TG_2': ('SYSCOHADA_Sub_exp',                  'balance','previous'),
    'NO_RESULTAT_TH_1': ('SYSCOHADA_Autres_prod',              'balance','current'),
    'NO_RESULTAT_TH_2': ('SYSCOHADA_Autres_prod',              'balance','previous'),
    'NO_RESULTAT_TI_1': ('SYSCOHADA_Transf_chrg_exp',          'balance','current'),
    'NO_RESULTAT_TI_2': ('SYSCOHADA_Transf_chrg_exp',          'balance','previous'),
    'NO_RESULTAT_RC_1': ('SYSCOHADA_Achats_mat_prem',          'balance','current'),
    'NO_RESULTAT_RC_2': ('SYSCOHADA_Achats_mat_prem',          'balance','previous'),
    'NO_RESULTAT_RD_1': ('SYSCOHADA_Var_stocks_mp',            'balance','current'),
    'NO_RESULTAT_RD_2': ('SYSCOHADA_Var_stocks_mp',            'balance','previous'),
    'NO_RESULTAT_RE_1': ('SYSCOHADA_Autres_achats',            'balance','current'),
    'NO_RESULTAT_RE_2': ('SYSCOHADA_Autres_achats',            'balance','previous'),
    'NO_RESULTAT_RF_1': ('SYSCOHADA_Var_stocks_autres_app',    'balance','current'),
    'NO_RESULTAT_RF_2': ('SYSCOHADA_Var_stocks_autres_app',    'balance','previous'),
    'NO_RESULTAT_RG_1': ('SYSCOHADA_Transports',               'balance','current'),
    'NO_RESULTAT_RG_2': ('SYSCOHADA_Transports',               'balance','previous'),
    'NO_RESULTAT_RH_1': ('SYSCOHADA_Services_ext',             'balance','current'),
    'NO_RESULTAT_RH_2': ('SYSCOHADA_Services_ext',             'balance','previous'),
    'NO_RESULTAT_RI_1': ('SYSCOHADA_impots_et_taxes',          'balance','current'),
    'NO_RESULTAT_RI_2': ('SYSCOHADA_impots_et_taxes',          'balance','previous'),
    'NO_RESULTAT_RJ_1': ('SYSCOHADA_Autres_charges',           'balance','current'),
    'NO_RESULTAT_RJ_2': ('SYSCOHADA_Autres_charges',           'balance','previous'),
    'NO_RESULTAT_XC_1': ('SYSCOHADA_Val_ajoutee',              'balance','current'),
    'NO_RESULTAT_XC_2': ('SYSCOHADA_Val_ajoutee',              'balance','previous'),
    'NO_RESULTAT_RK_1': ('SYSCOHADA_Charges_pers',             'balance','current'),
    'NO_RESULTAT_RK_2': ('SYSCOHADA_Charges_pers',             'balance','previous'),
    'NO_RESULTAT_XD_1': ('SYSCOHADA_EBE',                      'balance','current'),
    'NO_RESULTAT_XD_2': ('SYSCOHADA_EBE',                      'balance','previous'),
    'NO_RESULTAT_TJ_1': ('SYSCOHADA_Reprise_amr_prov_dep',     'balance','current'),
    'NO_RESULTAT_TJ_2': ('SYSCOHADA_Reprise_amr_prov_dep',     'balance','previous'),
    'NO_RESULTAT_RL_1': ('SYSCOHADA_Dot_am_prov_dep',          'balance','current'),
    'NO_RESULTAT_RL_2': ('SYSCOHADA_Dot_am_prov_dep',          'balance','previous'),
    'NO_RESULTAT_XE_1': ('SYSCOHADA_Resultat_exp',             'balance','current'),
    'NO_RESULTAT_XE_2': ('SYSCOHADA_Resultat_exp',             'balance','previous'),
    'NO_RESULTAT_TK_1': ('SYSCOHADA_Revenu_fin_ass',           'balance','current'),
    'NO_RESULTAT_TK_2': ('SYSCOHADA_Revenu_fin_ass',           'balance','previous'),
    'NO_RESULTAT_TL_1': ('SYSCOHADA_Reprise_prov_dep_fin',     'balance','current'),
    'NO_RESULTAT_TL_2': ('SYSCOHADA_Reprise_prov_dep_fin',     'balance','previous'),
    'NO_RESULTAT_TM_1': ('SYSCOHADA_Transferts_charges_fin',   'balance','current'),
    'NO_RESULTAT_TM_2': ('SYSCOHADA_Transferts_charges_fin',   'balance','previous'),
    'NO_RESULTAT_RM_1': ('SYSCOHADA_Frais_fin_chrg_ass',       'balance','current'),
    'NO_RESULTAT_RM_2': ('SYSCOHADA_Frais_fin_chrg_ass',       'balance','previous'),
    'NO_RESULTAT_RN_1': ('SYSCOHADA_Dot_prov_dep_fin',         'balance','current'),
    'NO_RESULTAT_RN_2': ('SYSCOHADA_Dot_prov_dep_fin',         'balance','previous'),
    'NO_RESULTAT_XF_1': ('SYSCOHADA_Resultat_fin',             'balance','current'),
    'NO_RESULTAT_XF_2': ('SYSCOHADA_Resultat_fin',             'balance','previous'),
    'NO_RESULTAT_XG_1': ('SYSCOHADA_Resultat_AO',              'balance','current'),
    'NO_RESULTAT_XG_2': ('SYSCOHADA_Resultat_AO',              'balance','previous'),
    'NO_RESULTAT_TN_1': ('SYSCOHADA_Prod_cess_immo',           'balance','current'),
    'NO_RESULTAT_TN_2': ('SYSCOHADA_Prod_cess_immo',           'balance','previous'),
    'NO_RESULTAT_TO_1': ('SYSCOHADA_Autres_prod_HAO',          'balance','current'),
    'NO_RESULTAT_TO_2': ('SYSCOHADA_Autres_prod_HAO',          'balance','previous'),
    'NO_RESULTAT_RO_1': ('SYSCOHADA_Val_comp_cess_immo',       'balance','current'),
    'NO_RESULTAT_RO_2': ('SYSCOHADA_Val_comp_cess_immo',       'balance','previous'),
    'NO_RESULTAT_RP_1': ('SYSCOHADA_Autres_chrg_HAO',          'balance','current'),
    'NO_RESULTAT_RP_2': ('SYSCOHADA_Autres_chrg_HAO',          'balance','previous'),
    'NO_RESULTAT_XH_1': ('SYSCOHADA_Resultat_HAO',             'balance','current'),
    'NO_RESULTAT_XH_2': ('SYSCOHADA_Resultat_HAO',             'balance','previous'),
    'NO_RESULTAT_RQ_1': ('SYSCOHADA_Part_trav',                'balance','current'),
    'NO_RESULTAT_RQ_2': ('SYSCOHADA_Part_trav',                'balance','previous'),
    'NO_RESULTAT_RS_1': ('SYSCOHADA_Impots_resultat',          'balance','current'),
    'NO_RESULTAT_RS_2': ('SYSCOHADA_Impots_resultat',          'balance','previous'),
    'NO_RESULTAT_XI_1': ('SYSCOHADA_XI',                       'balance','current'),
    'NO_RESULTAT_XI_2': ('SYSCOHADA_XI',                       'balance','previous'),
}

TFT_MAPPING = {}
for alias in ['ZA','FA','FB','FC','FD','FE','ZB','FF','FG','FH','FI','FJ','ZC',
              'FK','FL','FM','FN','ZD','FO','FP','FQ','ZE','ZF','ZG','ZH']:
    code = f'CI_TFT_{alias}'
    TFT_MAPPING[f'NO_TFT_{alias}_1'] = (code, 'balance', 'current')
    TFT_MAPPING[f'NO_TFT_{alias}_2'] = (code, 'balance', 'previous')

ALL_FINANCIAL_MAPPINGS = {**ACTIF_MAPPING, **PASSIF_MAPPING, **RESULTAT_MAPPING, **TFT_MAPPING}

# Alias sets for ACTIF / PASSIF split
_ACTIF_ALIASES = frozenset([
    'AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AP',
    'AQ','AR','AS','AZ','BA','BB','BG','BH','BI','BJ','BK',
    'BQ','BR','BS','BT','BU','BZ',
])
_PASSIF_ALIASES = frozenset([
    'CA','CB','CD','CE','CF','CG','CH','CJ','CL','CM','CP',
    'DA','DB','DC','DD','DF','DH','DI','DJ','DK','DM','DN','DP',
    'DQ','DR','DT','DV','DZ',
])


class L10nCiLiasseExport(models.AbstractModel):
    _name = 'l10n.ci.liasse.export'
    _description = 'CI Liasse Fiscale XML Export Helper'

    # ──────────────────────────────────────────────────────────
    #  Report data helpers (XML + Excel)
    # ──────────────────────────────────────────────────────────

    def _get_report_options(self, report, date_from, date_to, company, previous=False):
        from dateutil.relativedelta import relativedelta
        if previous:
            date_from = date_from - relativedelta(years=1)
            date_to   = date_to   - relativedelta(years=1)
        return report.get_options({
            'date': {
                'date_from': fields.Date.to_string(date_from),
                'date_to':   fields.Date.to_string(date_to),
                'mode':      'range',
                'filter':    'custom',
            },
            'multi_company': [{'id': company.id, 'name': company.name}],
        })

    def _fetch_report_values(self, report_xmlid, date_from, date_to, company):
        report = self.env.ref(report_xmlid, raise_if_not_found=False)
        if not report:
            return {}, {}

        line_code_by_id = {
            rec.id: rec.code
            for rec in self.env['account.report.line'].search([
                ('report_id', '=', report.id),
                ('code', '!=', False),
            ])
        }

        result_cur, result_prev = {}, {}
        for period, target in [('current', result_cur), ('previous', result_prev)]:
            options = self._get_report_options(report, date_from, date_to, company, period == 'previous')
            lines   = report._get_lines(options)
            col_defs = options.get('columns', [])
            for line in lines:
                line_id = line.get('id')
                code = line_code_by_id.get(line_id) if isinstance(line_id, int) else None
                if not code:
                    continue
                col_vals = {}
                for col, col_def in zip(line.get('columns', []), col_defs):
                    label = col_def.get('expression_label', '')
                    col_vals[label] = col.get('no_format', 0) or 0
                target[code] = col_vals

        return result_cur, result_prev

    def _get_expression_value(self, vals_cur, vals_prev, odoo_code, label, period):
        source = vals_cur if period == 'current' else vals_prev
        return (source.get(odoo_code, {}).get(label, 0) or 0)

    # ──────────────────────────────────────────────────────────
    #  XML generation
    # ──────────────────────────────────────────────────────────

    def generate_xml(self, date_from, date_to, company, liasse_type='NO'):
        from lxml import etree
        import math

        def fmt(val):
            if val is None:
                return ''
            try:
                v = float(val)
                if math.isnan(v) or math.isinf(v):
                    return ''
                return str(int(round(v)))
            except (TypeError, ValueError):
                return str(val)

        bilan_cur, bilan_prev = self._fetch_report_values(
            'l10n_syscohada_reports.account_financial_report_syscohada_bilan',
            date_from, date_to, company,
        )
        cr_cur, cr_prev = self._fetch_report_values(
            'l10n_syscohada_reports.account_financial_report_syscohada_pl',
            date_from, date_to, company,
        )
        tft_cur, tft_prev = self._fetch_report_values(
            'l10n_ci_liasse_fiscale.l10n_ci_tft',
            date_from, date_to, company,
        )

        all_cur  = {**bilan_cur,  **cr_cur,  **tft_cur}
        all_prev = {**bilan_prev, **cr_prev, **tft_prev}

        root = etree.Element('liasse')
        root.set('type', liasse_type)
        root.set('ncc', company.vat or '')
        root.set('exercice', str(date_to.year))

        entete = etree.SubElement(root, 'entete')
        etree.SubElement(entete, 'raison_sociale').text = company.name or ''
        etree.SubElement(entete, 'date_debut').text = fields.Date.to_string(date_from)
        etree.SubElement(entete, 'date_fin').text   = fields.Date.to_string(date_to)
        etree.SubElement(entete, 'monnaie').text    = company.currency_id.name or 'XOF'

        champs = etree.SubElement(root, 'champs')
        for dgi_code, (odoo_code, label, period) in ALL_FINANCIAL_MAPPINGS.items():
            source    = all_cur if period == 'current' else all_prev
            line_data = source.get(odoo_code, {})
            val = line_data.get(label, 0) or 0
            el  = etree.SubElement(champs, 'champ')
            el.set('code', dgi_code)
            el.text = fmt(val)

        company_fields = {
            'NO_FR1_ZA1_1': fields.Date.to_string(date_from),
            'NO_FR1_ZA2_1': fields.Date.to_string(date_to),
            'NO_FR1_ZK4_1': company.city or '',
            'NO_FR1_ZL_1':  company.street or '',
            'NO_FR1_ZK2_1': company.zip or '',
            'NO_FR1_ZK1_1': company.email or '',
        }
        for dgi_code, val in company_fields.items():
            el = etree.SubElement(champs, 'champ')
            el.set('code', dgi_code)
            el.text = str(val)

        return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)

    # ──────────────────────────────────────────────────────────
    #  Excel styling helpers
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _xl_palette():
        return {
            'dark':  '1F4E79',  # deep blue — company / col headers
            'mid':   '2E75B6',  # medium blue — period rows
            'total': 'DEEAF1',  # very light blue — level-0 totals
            'sect':  'BDD7EE',  # light blue — level-1 sections
            'white': 'FFFFFF',
            'fill':  'FFF2CC',  # light yellow — editable cells
            'gray':  'F2F2F2',
        }

    def _xl_hdr(self, cell, bg, fg='FFFFFF', bold=True, sz=10, halign='center'):
        from openpyxl.styles import Font, PatternFill, Alignment
        cell.font      = Font(name='Calibri', bold=bold, color=fg, size=sz)
        cell.fill      = PatternFill(fill_type='solid', fgColor=bg)
        cell.alignment = Alignment(horizontal=halign, vertical='center', wrap_text=True)

    @staticmethod
    def _xl_num(val):
        if val is None:
            return None
        try:
            v = float(val)
            return int(round(v)) if v != 0.0 else None
        except (TypeError, ValueError):
            return None

    # ──────────────────────────────────────────────────────────
    #  Sheet generators: financial reports
    # ──────────────────────────────────────────────────────────

    def _xl_add_sheet_report(self, wb, report_xmlid, sheet_title, date_from_str, date_to_str, company):
        from openpyxl.utils import get_column_letter
        from openpyxl.styles import Alignment
        P = self._xl_palette()

        report = self.env.ref(report_xmlid, raise_if_not_found=False)
        if not report:
            return

        options = report.get_options({
            'date': {
                'date_from': date_from_str,
                'date_to':   date_to_str,
                'mode':      'range',
                'filter':    'custom',
            },
            'multi_company': [{'id': company.id, 'name': company.name}],
        })
        lines    = report._get_lines(options)
        col_defs = options.get('columns', [])
        ncols    = 2 + len(col_defs)

        line_code_map = {
            r.id: r.code
            for r in self.env['account.report.line'].search([
                ('report_id', '=', report.id),
                ('code', '!=', False),
            ])
        }

        ws = wb.create_sheet(title=sheet_title[:31])

        for r, (text, bg) in enumerate([
            (company.name,                                     P['dark']),
            (f"Exercice du {date_from_str} au {date_to_str}", P['mid']),
            (report.name,                                      P['mid']),
        ], start=1):
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
            self._xl_hdr(ws.cell(row=r, column=1, value=text), bg=bg,
                         sz=12 if r == 1 else 10)
            ws.row_dimensions[r].height = 18 if r == 1 else 15

        self._xl_hdr(ws.cell(row=4, column=1, value='Code'), bg=P['dark'])
        self._xl_hdr(ws.cell(row=4, column=2, value='Libellé'), bg=P['dark'], halign='left')
        for ci, cd in enumerate(col_defs):
            self._xl_hdr(ws.cell(row=4, column=3 + ci, value=cd.get('name', '')), bg=P['dark'])
        ws.row_dimensions[4].height = 30

        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 52
        for ci in range(len(col_defs)):
            ws.column_dimensions[get_column_letter(3 + ci)].width = 18

        row = 5
        for line in lines:
            lid   = line.get('id')
            code  = line_code_map.get(lid, '') if isinstance(lid, int) else ''
            name  = line.get('name', '')
            level = line.get('level', 2)
            cols  = line.get('columns', [])

            is_total = (level == 0)
            is_sect  = (level == 1)
            bg   = P['total'] if is_total else (P['sect'] if is_sect else None)
            bold = is_total or is_sect

            c_code = ws.cell(row=row, column=1, value=code or None)
            c_name = ws.cell(row=row, column=2, value='  ' * level + name)
            c_name.alignment = Alignment(horizontal='left', vertical='center')
            if bg:
                self._xl_hdr(c_code, bg=bg, fg='000000', bold=bold, sz=10, halign='center')
                self._xl_hdr(c_name, bg=bg, fg='000000', bold=bold, sz=10, halign='left')

            for ci, col_val in enumerate(cols):
                v = self._xl_num(col_val.get('no_format'))
                c = ws.cell(row=row, column=3 + ci, value=v)
                c.alignment = Alignment(horizontal='right', vertical='center')
                if v is not None:
                    c.number_format = '#,##0'
                if bg:
                    self._xl_hdr(c, bg=bg, fg='000000', bold=bold, sz=10, halign='right')

            row += 1

    def _xl_add_bilan_section(self, wb, sheet_title, section, date_from_str, date_to_str, company):
        """ACTIF or PASSIF tab — filtered subset of the Bilan report."""
        from openpyxl.utils import get_column_letter
        from openpyxl.styles import Alignment
        P = self._xl_palette()

        allowed = _ACTIF_ALIASES if section == 'actif' else _PASSIF_ALIASES

        report = self.env.ref(
            'l10n_syscohada_reports.account_financial_report_syscohada_bilan',
            raise_if_not_found=False,
        )
        if not report:
            return

        options = report.get_options({
            'date': {
                'date_from': date_from_str,
                'date_to':   date_to_str,
                'mode':      'range',
                'filter':    'custom',
            },
            'multi_company': [{'id': company.id, 'name': company.name}],
        })
        all_lines = report._get_lines(options)
        col_defs  = options.get('columns', [])
        ncols     = 2 + len(col_defs)

        line_code_map = {
            r.id: r.code
            for r in self.env['account.report.line'].search([
                ('report_id', '=', report.id),
                ('code', '!=', False),
            ])
        }

        # Keep only lines whose alias is in the allowed set
        lines = []
        for line in all_lines:
            lid   = line.get('id')
            code  = line_code_map.get(lid, '') if isinstance(lid, int) else ''
            alias = code.replace('SYSCOHADA_', '') if code else ''
            if alias in allowed:
                lines.append((line, alias))

        if not lines:
            return

        ws = wb.create_sheet(title=sheet_title[:31])
        section_label = 'ACTIF' if section == 'actif' else 'PASSIF'

        for r, (text, bg) in enumerate([
            (company.name,                                     P['dark']),
            (f"Exercice du {date_from_str} au {date_to_str}", P['mid']),
            (f"BILAN — {section_label}",                      P['mid']),
        ], start=1):
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
            self._xl_hdr(ws.cell(row=r, column=1, value=text), bg=bg,
                         sz=12 if r == 1 else 10)
            ws.row_dimensions[r].height = 18 if r == 1 else 15

        self._xl_hdr(ws.cell(row=4, column=1, value='Code'), bg=P['dark'])
        self._xl_hdr(ws.cell(row=4, column=2, value='Libellé'), bg=P['dark'], halign='left')
        for ci, cd in enumerate(col_defs):
            self._xl_hdr(ws.cell(row=4, column=3 + ci, value=cd.get('name', '')), bg=P['dark'])
        ws.row_dimensions[4].height = 30

        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 52
        for ci in range(len(col_defs)):
            ws.column_dimensions[get_column_letter(3 + ci)].width = 18

        row = 5
        for line, alias in lines:
            name  = line.get('name', '')
            level = line.get('level', 2)
            cols  = line.get('columns', [])

            is_total = (level == 0)
            is_sect  = (level == 1)
            bg   = P['total'] if is_total else (P['sect'] if is_sect else None)
            bold = is_total or is_sect

            c_code = ws.cell(row=row, column=1, value=alias or None)
            c_name = ws.cell(row=row, column=2, value='  ' * level + name)
            c_name.alignment = Alignment(horizontal='left', vertical='center')
            if bg:
                self._xl_hdr(c_code, bg=bg, fg='000000', bold=bold, sz=10, halign='center')
                self._xl_hdr(c_name, bg=bg, fg='000000', bold=bold, sz=10, halign='left')

            for ci, col_val in enumerate(cols):
                v = self._xl_num(col_val.get('no_format'))
                c = ws.cell(row=row, column=3 + ci, value=v)
                c.alignment = Alignment(horizontal='right', vertical='center')
                if v is not None:
                    c.number_format = '#,##0'
                if bg:
                    self._xl_hdr(c, bg=bg, fg='000000', bold=bold, sz=10, halign='right')

            row += 1

    # ──────────────────────────────────────────────────────────
    #  Sheet generators: administrative / identification
    # ──────────────────────────────────────────────────────────

    def _xl_add_couverture(self, wb, company, date_from_str, date_to_str, liasse_type):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='COUVERTURE')

        labels = {'NO': 'SYSTÈME NORMAL', 'SI': 'SYSTÈME SIMPLIFIÉ', 'RS': 'RÉSUMÉ'}
        year = date_to_str[:4]

        rows = [
            ("REPUBLIQUE DE CÔTE D'IVOIRE",                           P['dark'], 16, True,  35),
            ("Union — Discipline — Travail",                           P['dark'], 11, False, 22),
            ("",                                                        P['mid'],  10, False, 10),
            ("MINISTERE DU BUDGET ET DU PORTEFEUILLE DE L'ETAT",      P['mid'],  12, True,  28),
            ("DIRECTION GENERALE DES IMPOTS",                          P['dark'], 14, True,  30),
            ("",                                                        P['dark'], 10, False, 10),
            ("LIASSE FISCALE DGI — CÔTE D'IVOIRE",                    P['dark'], 20, True,  45),
            (labels.get(liasse_type, liasse_type),                     P['mid'],  14, True,  32),
            (f"Exercice {year}",                                        P['mid'],  12, True,  28),
            ("",                                                        P['white'],10, False, 15),
            (f"Dénomination : {company.name}",                         P['white'],13, True,  26),
            (f"NCC : {company.vat or ''}",                             P['white'],11, False, 22),
            (f"Période : du {date_from_str} au {date_to_str}",         P['white'],11, False, 22),
            (f"Monnaie : {company.currency_id.name or 'XOF'}",         P['white'],11, False, 22),
        ]
        for i, (text, bg, sz, bold, ht) in enumerate(rows, start=1):
            ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=8)
            cell = ws.cell(row=i, column=1, value=text)
            fg = '000000' if bg == P['white'] else 'FFFFFF'
            cell.font      = Font(name='Calibri', bold=bold, size=sz, color=fg)
            cell.fill      = PatternFill(fill_type='solid', fgColor=bg)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[i].height = ht

        for ci in 'ABCDEFGH':
            ws.column_dimensions[ci].width = 15

    def _xl_add_garde(self, wb, company, date_from_str, date_to_str, sheet_title='GARDE'):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title=sheet_title[:31])

        ws.column_dimensions['A'].width = 36
        ws.column_dimensions['B'].width = 46

        ws.merge_cells('A1:B1')
        ws.cell(row=1, column=1, value="LIASSE FISCALE DGI CI — FICHE D'IDENTIFICATION")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=13, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 30

        ident_fields = [
            ("Dénomination sociale",                company.name or ''),
            ("N° Compte Contribuable (NCC)",        company.vat or ''),
            ("N° Contribuable (NTD)",               ''),
            ("Adresse du siège social",             company.street or ''),
            ("Ville",                               company.city or ''),
            ("Code postal / Boîte postale",         company.zip or ''),
            ("Téléphone",                           company.phone or ''),
            ("E-mail",                              company.email or ''),
            ("Site web",                            company.website or ''),
            ("Exercice du",                         date_from_str),
            ("au",                                  date_to_str),
            ("Monnaie de tenue des comptes",        company.currency_id.name or 'XOF'),
        ]
        for i, (label, val) in enumerate(ident_fields, start=3):
            ws.cell(row=i, column=1, value=label).font = Font(name='Calibri', bold=True, size=10)
            ws.cell(row=i, column=1).fill              = PatternFill(fill_type='solid', fgColor=P['sect'])
            c = ws.cell(row=i, column=2, value=val)
            c.font = Font(name='Calibri', size=10)
            c.fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[i].height = 17

        sep = 3 + len(ident_fields) + 1
        ws.merge_cells(f'A{sep}:B{sep}')
        ws.cell(row=sep, column=1, value="DOCUMENTS À JOINDRE").font      = Font(name='Calibri', bold=True, size=11, color='FFFFFF')
        ws.cell(row=sep, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=sep, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[sep].height = 22

        docs = [
            "☐  Bilan (Actif / Passif)",
            "☐  Compte de Résultat",
            "☐  Tableau des Flux de Trésorerie (TFT)",
            "☐  Notes annexes 1 à 39",
            "☐  Tableau des amortissements",
            "☐  État récapitulatif de la TVA",
            "☐  Relevé de soldes des comptes",
            "☐  Rapport du commissaire aux comptes",
        ]
        for j, doc in enumerate(docs, start=sep + 1):
            ws.cell(row=j, column=1, value=doc).font = Font(name='Calibri', size=10)
            ws.row_dimensions[j].height = 16

    def _xl_add_recevabilite(self, wb):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='RECEVABILITE')
        ws.column_dimensions['A'].width = 95

        ws.cell(row=1, column=1,
                value="CONDITIONS DE RECEVABILITÉ DE LA LIASSE FISCALE DGI CI")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=13, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 30

        conditions = [
            "",
            "La liasse fiscale est recevable si les conditions ci-après sont remplies :",
            "",
            "1.  La liasse est déposée dans les délais légaux (avant le 30 avril de l'année suivant l'exercice).",
            "2.  Toutes les pages sont renseignées — aucune page blanche.",
            "3.  Les totaux sont équilibrés : Total Actif = Total Passif.",
            "4.  Le résultat du bilan correspond au résultat du Compte de Résultat.",
            "5.  Les notes annexes obligatoires (1 à 39) sont toutes jointes.",
            "6.  Le fichier XML généré (e-impôts DGI) est conforme au schéma DGI CI.",
            "7.  La signature du représentant légal et du comptable agréé sont apposées.",
            "8.  Le cachet de la société est apposé sur chaque page.",
            "",
            "Références légales :",
            "  •  Acte Uniforme OHADA portant organisation et harmonisation des comptabilités des entreprises",
            "  •  SYSCOHADA Révisé (2017)",
            "  •  Code Général des Impôts — Côte d'Ivoire",
            "  •  Circulaire DGI CI relative aux obligations de dépôt de la liasse fiscale",
        ]
        for i, text in enumerate(conditions, start=2):
            ws.cell(row=i, column=1, value=text).font = Font(name='Calibri', size=10)
            ws.row_dimensions[i].height = 15

    def _xl_add_fiche_r1(self, wb, company, date_from_str, date_to_str):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='FICHE R1')

        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 46

        ws.merge_cells('A1:C1')
        ws.cell(row=1, column=1, value="FICHE R1 — IDENTIFICATION DE L'ENTREPRISE")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=13, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 28

        fields_r1 = [
            ('ZA1', "Date de début d'exercice",              date_from_str),
            ('ZA2', "Date de fin d'exercice",                date_to_str),
            ('ZB',  "Dénomination sociale",                  company.name or ''),
            ('ZC',  "Sigle",                                 ''),
            ('ZD',  "Numéro d'immatriculation au RC",        ''),
            ('ZE',  "Date d'immatriculation au RC",          ''),
            ('ZF',  "Numéro Compte Contribuable (NCC)",      company.vat or ''),
            ('ZG',  "Numéro Contribuable (NTD)",             ''),
            ('ZH',  "Adresse du siège social",               company.street or ''),
            ('ZI',  "Commune / Ville",                       company.city or ''),
            ('ZJ',  "Pays",                                  company.country_id.name if company.country_id else "Côte d'Ivoire"),
            ('ZK1', "Code postal / BP",                      company.zip or ''),
            ('ZK2', "Téléphone principal",                   company.phone or ''),
            ('ZK3', "Fax",                                   ''),
            ('ZK4', "E-mail",                                company.email or ''),
            ('ZL',  "Site internet",                         company.website or ''),
            ('ZM',  "Nom du représentant légal",             ''),
            ('ZN',  "Qualité du représentant légal",         ''),
            ('ZO',  "Expert-comptable (nom)",                ''),
            ('ZP',  "N° Agrément expert-comptable",          ''),
            ('ZQ',  "Commissaire aux comptes (nom)",         ''),
        ]
        for i, (code, label, val) in enumerate(fields_r1, start=3):
            ws.cell(row=i, column=1, value=code).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            ws.cell(row=i, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=i, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=i, column=2, value=label).font = Font(name='Calibri', bold=True, size=10)
            ws.cell(row=i, column=2).fill              = PatternFill(fill_type='solid', fgColor=P['sect'])
            c = ws.cell(row=i, column=3, value=val)
            c.font = Font(name='Calibri', size=10)
            c.fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[i].height = 17

    def _xl_add_fiche_r2(self, wb, company):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='FICHE R2')

        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 46
        ws.column_dimensions['C'].width = 40

        ws.merge_cells('A1:C1')
        ws.cell(row=1, column=1,
                value="FICHE R2 — FORME JURIDIQUE, RÉGIME FISCAL ET ACTIVITÉ")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=13, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 28

        rows = [
            ('ZX',  "Forme juridique (code — voir TABLE DES CODES)",   ''),
            ('ZY',  "Régime fiscal (code — voir TABLE DES CODES)",      ''),
            ('ZZ1', "Nombre d'établissements en Côte d'Ivoire",         ''),
            ('ZZ2', "Dont établissements exploités",                    ''),
            ('ZZ3', "Établissements à l'étranger",                      ''),
            ('ZZ4', "Dont établissements exploités à l'étranger",       ''),
            ('',    '', ''),
            ('',    "CLASSIFICATION D'ACTIVITÉ (CIAP)",                 ''),
            ('',    "Code CIAP principal",                               ''),
            ('',    "Libellé de l'activité principale",                  ''),
            ('',    "Code CIAP secondaire (si applicable)",              ''),
            ('',    "Libellé de l'activité secondaire",                  ''),
        ]
        for i, (code, label, val) in enumerate(rows, start=3):
            if code:
                ws.cell(row=i, column=1, value=code).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
                ws.cell(row=i, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
                ws.cell(row=i, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=i, column=2, value=label).font = Font(name='Calibri', bold=True, size=10)
            ws.cell(row=i, column=2).fill              = PatternFill(fill_type='solid', fgColor=P['sect'])
            c = ws.cell(row=i, column=3, value=val)
            c.font = Font(name='Calibri', size=10)
            c.fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[i].height = 17

    def _xl_add_fiche_r3(self, wb, company):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='FICHE R3')

        col_widths = [32, 26, 18, 16, 22]
        for ci, w in enumerate(col_widths, start=1):
            from openpyxl.utils import get_column_letter
            ws.column_dimensions[get_column_letter(ci)].width = w

        ws.merge_cells(f'A1:E1')
        ws.cell(row=1, column=1,
                value="FICHE R3 — DIRIGEANTS ET CONSEIL D'ADMINISTRATION")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=13, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 28

        headers = ['Nom et prénom', 'Qualité / Fonction', 'Nationalité', 'Part soc. (%)', 'Résidence fiscale']
        for ci, h in enumerate(headers, start=1):
            ws.cell(row=3, column=ci, value=h).font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            ws.cell(row=3, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=3, column=ci).alignment      = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[3].height = 24

        for r in range(4, 16):
            for ci in range(1, 6):
                ws.cell(row=r, column=ci).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 18

    def _xl_add_fiche_r4(self, wb, company, date_from_str, date_to_str):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='FICHE R4')

        ws.column_dimensions['A'].width = 48
        ws.column_dimensions['B'].width = 40

        ws.merge_cells('A1:B1')
        ws.cell(row=1, column=1,
                value="FICHE R4 — INFORMATIONS COMPLÉMENTAIRES ET FINANCIÈRES")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=13, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 28

        rows = [
            ("Date de création de l'entreprise",                    ''),
            ("Capital social (FCFA)",                               ''),
            ("Effectif total à la clôture",                         ''),
            ("Effectif moyen de l'exercice",                        ''),
            ("Chiffre d'affaires exercice N (FCFA)",                ''),
            ("Chiffre d'affaires exercice N-1 (FCFA)",              ''),
            ("Résultat net exercice N (FCFA)",                      ''),
            ("Résultat net exercice N-1 (FCFA)",                    ''),
            ("Dividendes distribués au titre de N-1 (FCFA)",        ''),
            ("Exercice précédent clos le",                          ''),
            ("Rapport du commissaire aux comptes",                   ''),
            ("Date de l'assemblée générale ordinaire",               ''),
        ]
        for i, (label, val) in enumerate(rows, start=3):
            ws.cell(row=i, column=1, value=label).font = Font(name='Calibri', bold=True, size=10)
            ws.cell(row=i, column=1).fill              = PatternFill(fill_type='solid', fgColor=P['sect'])
            c = ws.cell(row=i, column=2, value=val)
            c.font = Font(name='Calibri', size=10)
            c.fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[i].height = 18

    # ──────────────────────────────────────────────────────────
    #  Sheet generators: Note 36 reference tables
    # ──────────────────────────────────────────────────────────

    def _xl_add_note36_codes(self, wb):
        """TABLE DES CODES — Formes juridiques et régimes fiscaux CI."""
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='TABLE DES CODES')

        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 50
        ws.column_dimensions['C'].width = 10
        ws.column_dimensions['D'].width = 50

        ws.merge_cells('A1:D1')
        ws.cell(row=1, column=1, value="NOTE 36 — TABLE DES CODES (FORMES JURIDIQUES & RÉGIMES FISCAUX)")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        # Formes juridiques
        ws.merge_cells('A3:B3')
        ws.cell(row=3, column=1, value="FORMES JURIDIQUES").font = Font(name='Calibri', bold=True, size=11, color='FFFFFF')
        ws.cell(row=3, column=1).fill = PatternFill(fill_type='solid', fgColor=P['mid'])
        ws.row_dimensions[3].height = 20

        formes = [
            ('SA',   "Société Anonyme"),
            ('SARL', "Société à Responsabilité Limitée"),
            ('SNC',  "Société en Nom Collectif"),
            ('SCS',  "Société en Commandite Simple"),
            ('SCA',  "Société en Commandite par Actions"),
            ('GIE',  "Groupement d'Intérêt Économique"),
            ('SAS',  "Société par Actions Simplifiée"),
            ('COOP', "Coopérative"),
            ('ASS',  "Association"),
            ('EI',   "Entreprise Individuelle"),
            ('ETAB', "Établissement"),
            ('SUC',  "Succursale de société étrangère"),
            ('ORG',  "Organisme public ou semi-public"),
        ]
        for i, (code, label) in enumerate(formes, start=4):
            ws.cell(row=i, column=1, value=code).font = Font(name='Calibri', bold=True, size=10)
            ws.cell(row=i, column=1).fill              = PatternFill(fill_type='solid', fgColor=P['sect'])
            ws.cell(row=i, column=2, value=label).font = Font(name='Calibri', size=10)
            ws.row_dimensions[i].height = 16

        # Régimes fiscaux
        ws.merge_cells('C3:D3')
        ws.cell(row=3, column=3, value="RÉGIMES FISCAUX").font = Font(name='Calibri', bold=True, size=11, color='FFFFFF')
        ws.cell(row=3, column=3).fill = PatternFill(fill_type='solid', fgColor=P['mid'])

        regimes = [
            ('BIC',  "Bénéfices Industriels et Commerciaux"),
            ('BNC',  "Bénéfices Non Commerciaux"),
            ('BA',   "Bénéfices Agricoles"),
            ('RSI',  "Régime Synthétique d'Imposition"),
            ('RNI',  "Régime du Réel Normal d'Imposition"),
            ('RSI',  "Régime Simplifié d'Imposition"),
            ('IS',   "Impôt sur les Sociétés"),
            ('IR',   "Impôt sur le Revenu"),
            ('IMF',  "Impôt Minimum Forfaitaire"),
            ('TVA',  "Assujetti à la TVA"),
            ('EXON', "Exonéré"),
        ]
        for i, (code, label) in enumerate(regimes, start=4):
            ws.cell(row=i, column=3, value=code).font = Font(name='Calibri', bold=True, size=10)
            ws.cell(row=i, column=3).fill              = PatternFill(fill_type='solid', fgColor=P['sect'])
            ws.cell(row=i, column=4, value=label).font = Font(name='Calibri', size=10)

    def _xl_add_note36_ciap(self, wb):
        """NOTE 36 Suite — Nomenclature CIAP (Classification des Activités)."""
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='Nomenclature CIAP')

        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 72

        ws.merge_cells('A1:B1')
        ws.cell(row=1, column=1,
                value="NOTE 36 Suite — NOMENCLATURE CIAP (Classification Ivoirienne des Activités et Produits)")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        sectors = [
            ('A', "Agriculture, sylviculture et pêche"),
            ('B', "Industries extractives"),
            ('C', "Industries manufacturières"),
            ('D', "Production et distribution d'électricité, de gaz, de vapeur et d'air conditionné"),
            ('E', "Production et distribution d'eau ; assainissement, gestion des déchets et dépollution"),
            ('F', "Construction"),
            ('G', "Commerce de gros et de détail ; réparation de véhicules automobiles"),
            ('H', "Transports et entreposage"),
            ('I', "Hébergement et restauration"),
            ('J', "Information et communication"),
            ('K', "Activités financières et d'assurance"),
            ('L', "Activités immobilières"),
            ('M', "Activités spécialisées, scientifiques et techniques"),
            ('N', "Activités de services administratifs et de soutien"),
            ('O', "Administration publique"),
            ('P', "Enseignement"),
            ('Q', "Santé humaine et action sociale"),
            ('R', "Arts, spectacles et activités récréatives"),
            ('S', "Autres activités de services"),
            ('T', "Activités des ménages en tant qu'employeurs"),
            ('U', "Activités extraterritoriales"),
        ]
        for i, (code, label) in enumerate(sectors, start=3):
            ws.cell(row=i, column=1, value=code).font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            ws.cell(row=i, column=1).fill              = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=i, column=1).alignment         = Alignment(horizontal='center', vertical='center')
            ws.cell(row=i, column=2, value=label).font = Font(name='Calibri', size=10)
            ws.row_dimensions[i].height = 16

    # ──────────────────────────────────────────────────────────
    #  Sheet generator: generic placeholder note
    # ──────────────────────────────────────────────────────────

    def _xl_add_note_placeholder(self, wb, sheet_title, note_ref, description, fields_list=None):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title=sheet_title[:31])

        ws.column_dimensions['A'].width = 52
        ws.column_dimensions['B'].width = 22
        ws.column_dimensions['C'].width = 22

        ws.merge_cells('A1:C1')
        ws.cell(row=1, column=1,
                value=f"NOTE {note_ref} — {description.upper()}")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        if not fields_list:
            ws.cell(row=3, column=1, value="[À compléter manuellement]")
            ws.cell(row=3, column=1).font = Font(name='Calibri', size=10, color='808080', italic=True)
            return

        for ci, h in enumerate(['Description / Libellé', 'Exercice N', 'Exercice N-1'], start=1):
            ws.cell(row=3, column=ci, value=h).font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            ws.cell(row=3, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=3, column=ci).alignment      = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[3].height = 22

        for i, (label, is_header) in enumerate(fields_list, start=4):
            bg = P['sect'] if is_header else P['fill']
            ws.cell(row=i, column=1, value=label).font = Font(name='Calibri', bold=is_header, size=10)
            ws.cell(row=i, column=1).fill              = PatternFill(fill_type='solid', fgColor=bg)
            if is_header:
                ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=3)
            else:
                ws.cell(row=i, column=2).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
                ws.cell(row=i, column=3).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[i].height = 16

    # ──────────────────────────────────────────────────────────
    #  Sheet generators: DGI supplements
    # ──────────────────────────────────────────────────────────

    def _xl_add_comp_charges(self, wb, date_from, date_to, company, date_from_str, date_to_str):
        from openpyxl.styles import Font, PatternFill, Alignment
        from odoo import fields as ofields
        P = self._xl_palette()
        ws = wb.create_sheet(title='COMP-CHARGES')

        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 52
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 20

        ws.merge_cells('A1:D1')
        ws.cell(row=1, column=1, value="COMPLÉMENT — DÉTAIL DES CHARGES PAR NATURE (CLASSE 6)")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        ws.merge_cells('A2:D2')
        ws.cell(row=2, column=1,
                value=f"Exercice du {date_from_str} au {date_to_str} — {company.name}")
        ws.cell(row=2, column=1).font      = Font(name='Calibri', size=10, color='FFFFFF')
        ws.cell(row=2, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['mid'])
        ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')

        for ci, h in enumerate(['N° Compte', 'Intitulé', 'Exercice N', 'Exercice N-1'], start=1):
            ws.cell(row=4, column=ci, value=h).font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            ws.cell(row=4, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=4, column=ci).alignment      = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[4].height = 22

        try:
            from dateutil.relativedelta import relativedelta
            prev_from = date_from - relativedelta(years=1)
            prev_to   = date_to   - relativedelta(years=1)

            def _query(d_from, d_to):
                return self.env['account.move.line'].read_group(
                    domain=[
                        ('account_id.code', 'like', '6%'),
                        ('company_id', '=', company.id),
                        ('date', '>=', ofields.Date.to_string(d_from)),
                        ('date', '<=', ofields.Date.to_string(d_to)),
                        ('move_id.state', '=', 'posted'),
                    ],
                    fields=['account_id', 'balance:sum'],
                    groupby=['account_id'],
                    orderby='account_id',
                )

            groups      = _query(date_from, date_to)
            groups_prev = _query(prev_from, prev_to)
            prev_by_acc = {g['account_id'][0]: g.get('balance', 0) for g in groups_prev}

            row = 5
            for g in groups:
                acc_id   = g['account_id'][0]
                acc_name = g['account_id'][1] or ''
                parts    = acc_name.split(' ', 1)
                acc_code = parts[0]
                acc_lbl  = parts[1] if len(parts) > 1 else acc_name
                bal      = g.get('balance', 0) or 0
                prev_bal = prev_by_acc.get(acc_id, 0) or 0
                val_n  = int(round(-bal))  if bal   != 0 else None
                val_n1 = int(round(-prev_bal)) if prev_bal != 0 else None

                ws.cell(row=row, column=1, value=acc_code)
                ws.cell(row=row, column=2, value=acc_lbl)
                for ci, v in [(3, val_n), (4, val_n1)]:
                    c = ws.cell(row=row, column=ci, value=v)
                    c.alignment = Alignment(horizontal='right', vertical='center')
                    if v is not None:
                        c.number_format = '#,##0'
                row += 1
        except Exception:
            ws.cell(row=5, column=1, value="[Données non disponibles — vérifiez les droits d'accès]")
            ws.cell(row=5, column=1).font = Font(name='Calibri', size=10, color='808080', italic=True)

    def _xl_add_comp_tva(self, wb, sheet_num, date_from, date_to, company, date_from_str, date_to_str):
        from openpyxl.styles import Font, PatternFill, Alignment
        from odoo import fields as ofields
        P = self._xl_palette()

        title_map = {
            1: ('COMP-TVA',    "COMPLÉMENT TVA — TVA COLLECTÉE ET DÉDUCTIBLE"),
            2: ('COMP-TVA (2)',"COMPLÉMENT TVA (2) — TVA SUPPORTÉE NON DÉDUCTIBLE"),
        }
        sheet_name, heading = title_map.get(sheet_num, (f'COMP-TVA ({sheet_num})', 'TVA'))
        ws = wb.create_sheet(title=sheet_name[:31])

        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 48
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 20

        ws.merge_cells('A1:D1')
        ws.cell(row=1, column=1, value=heading)
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        ws.merge_cells('A2:D2')
        ws.cell(row=2, column=1,
                value=f"Exercice du {date_from_str} au {date_to_str} — {company.name}")
        ws.cell(row=2, column=1).font      = Font(name='Calibri', size=10, color='FFFFFF')
        ws.cell(row=2, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['mid'])
        ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')

        for ci, h in enumerate(['N° Compte', 'Intitulé', 'Base HT', 'Montant TVA'], start=1):
            ws.cell(row=4, column=ci, value=h).font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            ws.cell(row=4, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=4, column=ci).alignment      = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[4].height = 22

        prefixes = ['4457', '4456'] if sheet_num == 1 else ['4458']
        try:
            row = 5
            for pfx in prefixes:
                groups = self.env['account.move.line'].read_group(
                    domain=[
                        ('account_id.code', 'like', f'{pfx}%'),
                        ('company_id', '=', company.id),
                        ('date', '>=', ofields.Date.to_string(date_from)),
                        ('date', '<=', ofields.Date.to_string(date_to)),
                        ('move_id.state', '=', 'posted'),
                    ],
                    fields=['account_id', 'balance:sum'],
                    groupby=['account_id'],
                    orderby='account_id',
                )
                for g in groups:
                    acc_name = g['account_id'][1] or ''
                    parts    = acc_name.split(' ', 1)
                    acc_code = parts[0]
                    acc_lbl  = parts[1] if len(parts) > 1 else acc_name
                    bal      = g.get('balance', 0) or 0
                    val = int(round(abs(bal))) if bal != 0 else None
                    ws.cell(row=row, column=1, value=acc_code)
                    ws.cell(row=row, column=2, value=acc_lbl)
                    c = ws.cell(row=row, column=4, value=val)
                    c.alignment = Alignment(horizontal='right', vertical='center')
                    if val:
                        c.number_format = '#,##0'
                    row += 1
        except Exception:
            ws.cell(row=5, column=1, value="[Données non disponibles]")
            ws.cell(row=5, column=1).font = Font(name='Calibri', size=10, color='808080', italic=True)

    def _xl_add_suppl(self, wb, n, date_from_str, date_to_str, company):
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
        P = self._xl_palette()

        configs = {
            1: ("SUPPL1 — COMPLÉMENTS NOTES 32, 27B, 33 ET BIENS D'OCCASION",
                ['Description', 'Montant N', 'Montant N-1']),
            2: ("SUPPL2 — RÉPARTITION RÉSULTAT FISCAL — SOCIÉTÉS DE PERSONNES",
                ['Associé / Actionnaire', 'Part (%)', 'Quote-part bénéfice', 'Quote-part déficit']),
            3: ("SUPPL3 — INFORMATIONS ENTITÉS INDIVIDUELLES",
                ['Rubrique', 'Valeur N', 'Valeur N-1']),
            4: ("SUPPL4 — TABLEAU DES AMORTISSEMENTS — INVENTAIRE IMMOBILISATIONS",
                ['N° immo', 'Désignation', 'Date acquis.', 'Valeur brute', 'Taux (%)',
                 'Dot. exercice', 'Amort. cumulé', 'Valeur nette']),
            5: ("SUPPL5 — FRAIS ACCESSOIRES SUR ACHATS",
                ['Fournisseur', 'Nature des frais', 'Montant HT', 'TVA récupérable']),
            6: ("SUPPL6 — AVANTAGES EN NATURE ET EN ESPÈCES",
                ['Bénéficiaire', 'Qualité', 'Nature de l\'avantage', 'Valeur N', 'Valeur N-1']),
            7: ("SUPPL7 — CRÉANCES ET DETTES ÉCHUES DE L'EXERCICE",
                ['Compte', 'Libellé', 'Montant échu N', 'Dont contentieux N']),
        }
        heading, cols = configs.get(n, (f'SUPPL{n}', ['Description', 'Montant']))
        ncols = len(cols)

        ws = wb.create_sheet(title=f'SUPPL{n}')

        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
        ws.cell(row=1, column=1, value=heading)
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
        ws.cell(row=2, column=1,
                value=f"Exercice du {date_from_str} au {date_to_str} — {company.name}")
        ws.cell(row=2, column=1).font      = Font(name='Calibri', size=10, color='FFFFFF')
        ws.cell(row=2, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['mid'])
        ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')

        for ci, h in enumerate(cols, start=1):
            ws.cell(row=4, column=ci, value=h).font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            ws.cell(row=4, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=4, column=ci).alignment      = Alignment(horizontal='center', vertical='center')
            ws.column_dimensions[get_column_letter(ci)].width = max(16, len(h) + 3)
        ws.row_dimensions[4].height = 22

        for r in range(5, 22):
            for ci in range(1, ncols + 1):
                ws.cell(row=r, column=ci).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 17

    def _xl_add_commentaire(self, wb, company, date_from_str, date_to_str):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='COMMENTAIRE')
        ws.column_dimensions['A'].width = 100

        ws.cell(row=1, column=1,
                value=f"COMMENTAIRES LIBRES — {company.name} — Exercice du {date_from_str} au {date_to_str}")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        ws.cell(row=3, column=1,
                value="[Espace réservé aux commentaires, observations et informations complémentaires]")
        ws.cell(row=3, column=1).font = Font(name='Calibri', size=11, color='808080', italic=True)
        ws.row_dimensions[3].height = 20

        for r in range(4, 35):
            ws.cell(row=r, column=1).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 18

    # ──────────────────────────────────────────────────────────
    #  Main Excel generation
    # ──────────────────────────────────────────────────────────

    def generate_excel(self, date_from, date_to, company, liasse_type='NO'):
        try:
            import openpyxl
        except ImportError:
            from odoo.exceptions import UserError
            raise UserError("openpyxl est requis pour l'export Excel. Installez-le via pip.")

        from io import BytesIO

        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        dfstr = fields.Date.to_string(date_from)
        dtstr = fields.Date.to_string(date_to)

        def safe(fn, *args, **kw):
            try:
                fn(*args, **kw)
            except Exception:
                pass

        # ── Bloc 1 : pages administratives ──────────────────────────
        safe(self._xl_add_couverture,     wb, company, dfstr, dtstr, liasse_type)
        safe(self._xl_add_garde,          wb, company, dfstr, dtstr, 'GARDE')
        safe(self._xl_add_recevabilite,   wb)
        safe(self._xl_add_note36_codes,   wb)
        safe(self._xl_add_note36_ciap,    wb)

        # ── Bloc 2 : fiches d'identification ────────────────────────
        safe(self._xl_add_fiche_r1, wb, company, dfstr, dtstr)
        safe(self._xl_add_fiche_r2, wb, company)
        safe(self._xl_add_fiche_r3, wb, company)

        # ── Bloc 3 : états financiers ────────────────────────────────
        safe(self._xl_add_sheet_report, wb,
             'l10n_syscohada_reports.account_financial_report_syscohada_bilan',
             'BILAN', dfstr, dtstr, company)
        safe(self._xl_add_bilan_section, wb, 'ACTIF',  'actif',  dfstr, dtstr, company)
        safe(self._xl_add_bilan_section, wb, 'PASSIF', 'passif', dfstr, dtstr, company)
        safe(self._xl_add_sheet_report, wb,
             'l10n_syscohada_reports.account_financial_report_syscohada_pl',
             'RESULTAT', dfstr, dtstr, company)
        safe(self._xl_add_sheet_report, wb,
             'l10n_ci_liasse_fiscale.l10n_ci_tft',
             'TFT', dfstr, dtstr, company)
        safe(self._xl_add_fiche_r4, wb, company, dfstr, dtstr)

        # ── Bloc 4 : notes 1–39 ─────────────────────────────────────

        # Notes sans account.report (saisie manuelle)
        safe(self._xl_add_note_placeholder, wb, 'NOTE 1', '1',
             "DETTES GARANTIES ET ENGAGEMENTS FINANCIERS",
             [
                 ("NOTE 1A — Dettes garanties par des sûretés réelles", True),
                 ("Emprunts et dettes financières garantis (16x)",       False),
                 ("Dettes fournisseurs garanties (40x)",                 False),
                 ("Autres dettes garanties",                             False),
                 ("TOTAL dettes garanties",                              False),
                 ("NOTE 1B — Engagements financiers hors bilan",         True),
                 ("Cautions, avals et garanties donnés",                 False),
                 ("Engagements reçus",                                   False),
                 ("Crédits-bails et locations financières",              False),
                 ("Autres engagements hors bilan",                       False),
             ])
        safe(self._xl_add_note_placeholder, wb, 'NOTE 2', '2',
             "MÉTHODES ET PRINCIPES COMPTABLES",
             [
                 ("Méthode de valorisation des stocks",                  False),
                 ("Méthode d'amortissement principal",                   False),
                 ("Méthode de conversion des opérations en devises",     False),
                 ("Méthode d'évaluation des provisions",                 False),
                 ("CHANGEMENTS DE MÉTHODES",                             True),
                 ("Description du changement",                           False),
                 ("Justification du changement",                         False),
                 ("Impact quantifié sur le résultat (FCFA)",             False),
             ])

        # Notes 3A–3E (account.report)
        for xmlid, title in [
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3a',   'NOTE 3A'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3b',   'NOTE 3B'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3c',   'NOTE 3C'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3cbis','NOTE 3C BIS'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3d',   'NOTE 3D'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3e',   'NOTE 3E'),
        ]:
            safe(self._xl_add_sheet_report, wb, xmlid, title, dfstr, dtstr, company)

        # Note 4 (account.report)
        safe(self._xl_add_sheet_report, wb,
             'l10n_ci_liasse_fiscale.l10n_ci_note_4', 'NOTE 4', dfstr, dtstr, company)

        # Notes 5–8 (account.report)
        for n in range(5, 9):
            safe(self._xl_add_sheet_report, wb,
                 f'l10n_ci_liasse_fiscale.l10n_ci_note_{n}',
                 f'NOTE {n}', dfstr, dtstr, company)

        # Notes 8A, 8B, 8C (placeholders)
        safe(self._xl_add_note_placeholder, wb, 'NOTE 8A', '8A',
             "ÉTALEMENT DES CHARGES IMMOBILISÉES",
             [
                 ("Valeur brute en début d'exercice (481)",       False),
                 ("Charges immobilisées de l'exercice",           False),
                 ("Amortissements de l'exercice",                  False),
                 ("Valeur nette en fin d'exercice",               False),
             ])
        safe(self._xl_add_note_placeholder, wb, 'NOTE 8B', '8B',
             "PROVISIONS POUR CHARGES À RÉPARTIR",
             [
                 ("Provisions constituées (191–199)",             False),
                 ("Reprises de l'exercice",                       False),
                 ("Solde en fin d'exercice",                      False),
             ])
        safe(self._xl_add_note_placeholder, wb, 'NOTE 8C', '8C',
             "PROVISIONS POUR ENGAGEMENTS DE RETRAITE",
             [
                 ("Effectif concerné",                            False),
                 ("Provision constituée (196)",                   False),
                 ("Méthode actuarielle utilisée",                 False),
                 ("Taux d'actualisation (%)",                     False),
                 ("Taux de rotation du personnel (%)",            False),
             ])

        # Notes 9–14 (account.report)
        for n in range(9, 15):
            safe(self._xl_add_sheet_report, wb,
                 f'l10n_ci_liasse_fiscale.l10n_ci_note_{n}',
                 f'NOTE {n}', dfstr, dtstr, company)

        # Notes 15A, 15B (placeholders)
        safe(self._xl_add_note_placeholder, wb, 'NOTE 15A', '15A',
             "SUBVENTIONS D'INVESTISSEMENT ET PROVISIONS RÉGLEMENTÉES",
             [
                 ("SUBVENTIONS D'INVESTISSEMENT (14x)",           True),
                 ("Montant brut en début d'exercice",             False),
                 ("Subventions reçues",                           False),
                 ("Virements au compte de résultat",              False),
                 ("Montant brut en fin d'exercice",               False),
                 ("PROVISIONS RÉGLEMENTÉES (15x)",                True),
                 ("Montant en début d'exercice",                  False),
                 ("Dotations de l'exercice",                      False),
                 ("Reprises de l'exercice",                       False),
                 ("Montant en fin d'exercice",                    False),
             ])
        safe(self._xl_add_note_placeholder, wb, 'NOTE 15B', '15B',
             "AUTRES FONDS PROPRES",
             [
                 ("Nature des autres fonds propres",              False),
                 ("Montant en début d'exercice",                  False),
                 ("Augmentations",                                False),
                 ("Diminutions",                                  False),
                 ("Montant en fin d'exercice",                    False),
             ])

        # Note 16A (account.report)
        safe(self._xl_add_sheet_report, wb,
             'l10n_ci_liasse_fiscale.l10n_ci_note_16a', 'NOTE 16A', dfstr, dtstr, company)

        # Notes 16B, 16B BIS, 16C (placeholders)
        safe(self._xl_add_note_placeholder, wb, 'NOTE 16B', '16B',
             "ENGAGEMENTS DE RETRAITE (ACTUARIEL)",
             [
                 ("Obligation au titre des prestations définies", False),
                 ("Juste valeur des actifs du régime",            False),
                 ("Surplus / Déficit",                            False),
                 ("Charge de retraite de l'exercice",             False),
                 ("Taux d'actualisation (%)",                     False),
                 ("Taux de rendement attendu des actifs (%)",     False),
             ])
        safe(self._xl_add_note_placeholder, wb, 'NOTE 16B BIS', '16B BIS',
             "ACTIFS ET PASSIFS DES RÉGIMES FINANCÉS",
             [
                 ("Valeur des actifs du régime en début d'ex.",  False),
                 ("Cotisations employeur",                        False),
                 ("Cotisations salariés",                         False),
                 ("Rendement réel des actifs",                    False),
                 ("Valeur des actifs du régime en fin d'ex.",    False),
             ])
        safe(self._xl_add_note_placeholder, wb, 'NOTE 16C', '16C',
             "ACTIFS ET PASSIFS ÉVENTUELS (LITIGES)",
             [
                 ("ACTIFS ÉVENTUELS",                             True),
                 ("Description du litige",                        False),
                 ("Partie adverse",                               False),
                 ("Montant estimé (FCFA)",                        False),
                 ("PASSIFS ÉVENTUELS",                            True),
                 ("Description du litige",                        False),
                 ("Partie adverse",                               False),
                 ("Montant estimé (FCFA)",                        False),
             ])

        # Notes 17–39 (account.report)
        for n in range(17, 40):
            xmlid = f'l10n_ci_liasse_fiscale.l10n_ci_note_{n}'
            safe(self._xl_add_sheet_report, wb, xmlid, f'NOTE {n}', dfstr, dtstr, company)

        # ── Bloc 5 : suppléments DGI ────────────────────────────────
        safe(self._xl_add_garde, wb, company, dfstr, dtstr, 'GARDE (DGI-INS)')
        safe(self._xl_add_note_placeholder, wb, 'NOTES DGI-INS', 'DGI-INS',
             "NOTES POUR LA DÉCLARATION IMPÔT SUR LES SOCIÉTÉS",
             [
                 ("Résultat comptable (avant impôt)",             False),
                 ("Réintégrations fiscales",                      False),
                 ("Déductions fiscales",                          False),
                 ("Résultat fiscal",                              False),
                 ("Base imposable IS",                            False),
                 ("Taux IS (%)",                                  False),
                 ("IS dû",                                        False),
                 ("Crédit d'impôt / Acomptes versés",            False),
                 ("IS net à payer",                               False),
             ])
        safe(self._xl_add_comp_charges, wb, date_from, date_to, company, dfstr, dtstr)
        safe(self._xl_add_comp_tva, wb, 1, date_from, date_to, company, dfstr, dtstr)
        safe(self._xl_add_comp_tva, wb, 2, date_from, date_to, company, dfstr, dtstr)

        for n in range(1, 8):
            safe(self._xl_add_suppl, wb, n, dfstr, dtstr, company)

        safe(self._xl_add_garde, wb, company, dfstr, dtstr, 'GARDE(3)')
        safe(self._xl_add_commentaire, wb, company, dfstr, dtstr)

        buf = BytesIO()
        wb.save(buf)
        return buf.getvalue()
