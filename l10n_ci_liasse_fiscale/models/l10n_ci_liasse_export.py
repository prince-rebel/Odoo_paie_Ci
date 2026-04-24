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


class L10nCiLiasseExport(models.AbstractModel):
    _name = 'l10n.ci.liasse.export'
    _description = 'CI Liasse Fiscale XML Export Helper'

    def _get_report_options(self, report, date_from, date_to, company, previous=False):
        """Build account.report options dict for a given period."""
        from dateutil.relativedelta import relativedelta
        if previous:
            date_from = date_from - relativedelta(years=1)
            date_to = date_to - relativedelta(years=1)
        # get_options (no underscore) is the public API in Odoo 17+
        return report.get_options({
            'date': {
                'date_from': fields.Date.to_string(date_from),
                'date_to': fields.Date.to_string(date_to),
                'mode': 'range',
                'filter': 'custom',
            },
            'multi_company': [{'id': company.id, 'name': company.name}],
        })

    def _fetch_report_values(self, report_xmlid, date_from, date_to, company):
        """
        Returns two dicts: current_vals, previous_vals
        Each dict maps line_code → {label: value}
        """
        report = self.env.ref(report_xmlid, raise_if_not_found=False)
        if not report:
            return {}, {}

        # Build a lookup: account.report.line db-id → code (for all lines of this report)
        line_code_by_id = {
            rec.id: rec.code
            for rec in self.env['account.report.line'].search([
                ('report_id', '=', report.id),
                ('code', '!=', False),
            ])
        }

        result_cur, result_prev = {}, {}

        for period, target in [('current', result_cur), ('previous', result_prev)]:
            previous = (period == 'previous')
            options = self._get_report_options(report, date_from, date_to, company, previous)
            lines = report._get_lines(options)
            col_defs = options.get('columns', [])
            for line in lines:
                line_id = line.get('id')
                code = line_code_by_id.get(line_id) if isinstance(line_id, int) else None
                if not code:
                    continue
                col_vals = {}
                for col, col_def in zip(line.get('columns', []), col_defs):
                    label = col_def.get('expression_label', '')
                    val = col.get('no_format', 0) or 0
                    col_vals[label] = val
                target[code] = col_vals

        return result_cur, result_prev

    def _get_expression_value(self, vals_cur, vals_prev, odoo_code, label, period):
        """Retrieve a single value from pre-fetched report data."""
        source = vals_cur if period == 'current' else vals_prev
        line_data = source.get(odoo_code, {})
        return line_data.get(label, 0) or 0

    def generate_xml(self, date_from, date_to, company, liasse_type='NO'):
        """
        Generate DGI e-impôts XML for the given company and fiscal period.
        Returns the XML string (bytes).
        """
        from lxml import etree
        import math

        def fmt(val):
            """Format numeric value: integer (no decimal), empty string for zero."""
            if val is None:
                return ''
            try:
                v = float(val)
                if math.isnan(v) or math.isinf(v):
                    return ''
                return str(int(round(v)))
            except (TypeError, ValueError):
                return str(val)

        # --- Fetch financial data ---
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

        # Merge into unified lookup by odoo_code
        all_cur = {**bilan_cur, **cr_cur, **tft_cur}
        all_prev = {**bilan_prev, **cr_prev, **tft_prev}

        # --- Build XML ---
        root = etree.Element('liasse')
        root.set('type', liasse_type)
        root.set('ncc', company.vat or '')
        root.set('exercice', str(date_to.year))

        # Header / identification
        entete = etree.SubElement(root, 'entete')
        etree.SubElement(entete, 'raison_sociale').text = company.name or ''
        etree.SubElement(entete, 'date_debut').text = fields.Date.to_string(date_from)
        etree.SubElement(entete, 'date_fin').text = fields.Date.to_string(date_to)
        etree.SubElement(entete, 'monnaie').text = company.currency_id.name or 'XOF'

        # Fixed financial fields
        champs = etree.SubElement(root, 'champs')

        for dgi_code, (odoo_code, label, period) in ALL_FINANCIAL_MAPPINGS.items():
            source = all_cur if period == 'current' else all_prev
            line_data = source.get(odoo_code, {})
            val = line_data.get(label, 0) or 0
            el = etree.SubElement(champs, 'champ')
            el.set('code', dgi_code)
            el.text = fmt(val)

        # FR1 identification fields (company info)
        company_fields = {
            'NO_FR1_ZA1_1': fields.Date.to_string(date_from),
            'NO_FR1_ZA2_1': fields.Date.to_string(date_to),
            'NO_FR1_ZK4_1': company.city or '',
            'NO_FR1_ZL_1': company.street or '',
            'NO_FR1_ZK2_1': company.zip or '',
            'NO_FR1_ZK1_1': company.email or '',
        }
        for dgi_code, val in company_fields.items():
            el = etree.SubElement(champs, 'champ')
            el.set('code', dgi_code)
            el.text = str(val)

        xml_bytes = etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        return xml_bytes

    def generate_excel(self, date_from, date_to, company):
        """
        Generate a multi-sheet XLSX workbook — one tab per financial statement and note.
        Returns bytes.
        """
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            from openpyxl.utils import get_column_letter
        except ImportError:
            from odoo.exceptions import UserError
            raise UserError("openpyxl est requis pour l'export Excel.")

        from io import BytesIO

        # ── Palette ──────────────────────────────────────────────────────────
        BG_DARK   = '1F4E79'   # bleu DGI foncé   → en-têtes société/rapport
        BG_MID    = '2E75B6'   # bleu moyen        → ligne période
        BG_TOTAL  = 'DEEAF1'   # bleu très clair   → lignes total (level 0)
        BG_SECT   = 'BDD7EE'   # bleu clair        → sections (level 1)
        FG_WHITE  = 'FFFFFF'

        def _hdr(cell, bg=BG_DARK, fg=FG_WHITE, bold=True, sz=10, halign='center'):
            cell.font = Font(name='Calibri', bold=bold, color=fg, size=sz)
            cell.fill = PatternFill(fill_type='solid', fgColor=bg)
            cell.alignment = Alignment(horizontal=halign, vertical='center', wrap_text=True)

        def _total(cell, bold=True):
            cell.font = Font(name='Calibri', bold=bold, size=10)
            cell.fill = PatternFill(fill_type='solid', fgColor=BG_TOTAL)

        def _sect(cell):
            cell.font = Font(name='Calibri', bold=True, size=10)
            cell.fill = PatternFill(fill_type='solid', fgColor=BG_SECT)

        def _num(val):
            if val is None:
                return None
            try:
                v = float(val)
                return int(round(v)) if v != 0.0 else None
            except (TypeError, ValueError):
                return None

        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        date_from_str = fields.Date.to_string(date_from)
        date_to_str   = fields.Date.to_string(date_to)

        def _add_sheet(report_xmlid, sheet_title):
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

            # Map line DB-id → code
            line_code_map = {
                r.id: r.code
                for r in self.env['account.report.line'].search([
                    ('report_id', '=', report.id),
                    ('code', '!=', False),
                ])
            }

            ws = wb.create_sheet(title=sheet_title[:31])

            # ── Rows 1-3 : société / période / rapport ─────────────────────
            for r, (text, bg) in enumerate([
                (company.name,                                       BG_DARK),
                (f"Exercice du {date_from_str} au {date_to_str}",   BG_MID),
                (report.name,                                        BG_MID),
            ], start=1):
                ws.merge_cells(start_row=r, start_column=1,
                               end_row=r,   end_column=ncols)
                _hdr(ws.cell(row=r, column=1, value=text), bg=bg,
                     sz=12 if r == 1 else 10)
                ws.row_dimensions[r].height = 18 if r == 1 else 15

            # ── Row 4 : column headers ──────────────────────────────────────
            _hdr(ws.cell(row=4, column=1, value='Code'))
            _hdr(ws.cell(row=4, column=2, value='Libellé'), halign='left')
            for ci, cd in enumerate(col_defs):
                _hdr(ws.cell(row=4, column=3 + ci, value=cd.get('name', '')))
            ws.row_dimensions[4].height = 30

            # Column widths
            ws.column_dimensions['A'].width = 12
            ws.column_dimensions['B'].width = 52
            for ci in range(len(col_defs)):
                ws.column_dimensions[get_column_letter(3 + ci)].width = 18

            # ── Data rows ──────────────────────────────────────────────────
            row = 5
            for line in lines:
                lid   = line.get('id')
                code  = line_code_map.get(lid, '') if isinstance(lid, int) else ''
                name  = line.get('name', '')
                level = line.get('level', 2)
                cols  = line.get('columns', [])

                indent = '  ' * level
                is_total = (level == 0)
                is_sect  = (level == 1)

                apply = _total if is_total else (_sect if is_sect else None)

                c_code = ws.cell(row=row, column=1, value=code or None)
                c_name = ws.cell(row=row, column=2, value=indent + name)
                c_name.alignment = Alignment(horizontal='left', vertical='center')

                if apply:
                    apply(c_code); apply(c_name)

                for ci, col_val in enumerate(cols):
                    v   = _num(col_val.get('no_format'))
                    c   = ws.cell(row=row, column=3 + ci, value=v)
                    c.alignment = Alignment(horizontal='right', vertical='center')
                    if v is not None:
                        c.number_format = '#,##0'
                    if apply:
                        apply(c)

                row += 1

        # ── Sheet list ──────────────────────────────────────────────────────
        SHEETS = [
            ('l10n_syscohada_reports.account_financial_report_syscohada_bilan', 'Bilan'),
            ('l10n_syscohada_reports.account_financial_report_syscohada_pl',    'Compte de Résultat'),
            ('l10n_ci_liasse_fiscale.l10n_ci_tft',      'TFT'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3a',  'Note 3A'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3b',  'Note 3B'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3c',  'Note 3C'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3cbis','Note 3C BIS'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3d',  'Note 3D'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3e',  'Note 3E'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_4',   'Note 4'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_5',   'Note 5'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_6',   'Note 6'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_7',   'Note 7'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_8',   'Note 8'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_9',   'Note 9'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_10',  'Note 10'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_11',  'Note 11'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_12',  'Note 12'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_13',  'Note 13'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_14',  'Note 14'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_16a', 'Note 16A'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_17',  'Note 17'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_18',  'Note 18'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_19',  'Note 19'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_20',  'Note 20'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_21',  'Note 21'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_22',  'Note 22'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_23',  'Note 23'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_24',  'Note 24'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_25',  'Note 25'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_26',  'Note 26'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_27a', 'Note 27A'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_27b', 'Note 27B'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_28',  'Note 28'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_29',  'Note 29'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_30',  'Note 30'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_31',  'Note 31'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_32',  'Note 32'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_33',  'Note 33'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_34',  'Note 34'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_35',  'Note 35'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_36',  'Note 36'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_37',  'Note 37'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_38',  'Note 38'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_39',  'Note 39'),
        ]

        for xmlid, title in SHEETS:
            try:
                _add_sheet(xmlid, title)
            except Exception:
                pass  # skip unavailable reports silently

        buf = BytesIO()
        wb.save(buf)
        return buf.getvalue()
