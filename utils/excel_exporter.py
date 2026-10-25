"""
utils/excel_exporter.py — Exportateur Excel natif multi-formats
─────────────────────────────────────────────────────────────────
Génère des fichiers Excel directement ouvrables sous Microsoft Excel :
  1. Si openpyxl est disponible : fichier natif .xlsx
  2. Sinon : format XML Spreadsheet 2003 (.xls) avec en-têtes stylisés,
     ou CSV avec encodage UTF-8 avec BOM (utf-8-sig)
"""

import os
import csv
import html
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def export_stock_to_excel(file_path: str, headers: list[str], rows: list[list]) -> None:
    """
    Exporte une liste de données vers un fichier Excel.
    Prend en charge .xlsx, .xls et .csv avec mise en forme complète.
    """
    lower_path = file_path.lower()

    # Tentative d'utilisation de openpyxl si le fichier se termine par .xlsx
    if lower_path.endswith(".xlsx"):
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Stock Laptops"

            # En-tête avec style corporate
            header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="1A5276", end_color="1A5276", fill_type="solid")
            center_align = Alignment(horizontal="center", vertical="center")

            ws.append(headers)
            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_align

            # Données
            data_font = Font(name="Segoe UI", size=10)
            for row_data in rows:
                ws.append(row_data)

            # Ajustement largeur des colonnes
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

            wb.save(file_path)
            logger.info("Stock exported with openpyxl to %s", file_path)
            return
        except ImportError:
            logger.warning("openpyxl not available, generating Excel XML format.")

    # Si le format demandé est .xls ou fallback .xlsx : Génération Excel XML Spreadsheet 2003
    if lower_path.endswith(".xls") or lower_path.endswith(".xlsx"):
        _write_excel_xml(file_path, headers, rows)
        return

    # Sinon format CSV avec BOM pour compatibilité totale avec Excel français/anglais
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(headers)
        for r in rows:
            writer.writerow(r)
    logger.info("Stock exported with CSV (BOM) to %s", file_path)


def _write_excel_xml(file_path: str, headers: list[str], rows: list[list]) -> None:
    """Génère un fichier Excel Spreadsheet XML (.xls) natif sans dépendance externe."""
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<?mso-application progid="Excel.Sheet"?>',
        '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"',
        ' xmlns:o="urn:schemas-microsoft-com:office:office"',
        ' xmlns:x="urn:schemas-microsoft-com:office:excel"',
        ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"',
        ' xmlns:html="http://www.w3.org/TR/REC-html40">',
        '<Styles>',
        ' <Style ss:ID="Header">',
        '  <Font ss:FontName="Segoe UI" ss:Size="11" ss:Color="#FFFFFF" ss:Bold="1"/>',
        '  <Interior ss:Color="#1A5276" ss:Pattern="Solid"/>',
        '  <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>',
        ' </Style>',
        ' <Style ss:ID="Data">',
        '  <Font ss:FontName="Segoe UI" ss:Size="10" ss:Color="#2C3E50"/>',
        '  <Alignment ss:Vertical="Center"/>',
        ' </Style>',
        ' <Style ss:ID="DataCenter">',
        '  <Font ss:FontName="Segoe UI" ss:Size="10" ss:Color="#2C3E50"/>',
        '  <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>',
        ' </Style>',
        '</Styles>',
        '<Worksheet ss:Name="Stock Laptops">',
        '<Table>',
    ]

    # En-têtes
    xml_parts.append('<Row ss:StyleID="Header">')
    for h in headers:
        xml_parts.append(f'<Cell><Data ss:Type="String">{html.escape(str(h))}</Data></Cell>')
    xml_parts.append('</Row>')

    # Données
    for row in rows:
        xml_parts.append('<Row ss:StyleID="Data">')
        for val in row:
            val_str = html.escape(str(val or ""))
            # Détecter si numérique
            if isinstance(val, (int, float)):
                xml_parts.append(f'<Cell ss:StyleID="DataCenter"><Data ss:Type="Number">{val}</Data></Cell>')
            else:
                xml_parts.append(f'<Cell><Data ss:Type="String">{val_str}</Data></Cell>')
        xml_parts.append('</Row>')

    xml_parts.append('</Table>')
    xml_parts.append('</Worksheet>')
    xml_parts.append('</Workbook>')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_parts))
    logger.info("Stock exported as Excel XML to %s", file_path)

