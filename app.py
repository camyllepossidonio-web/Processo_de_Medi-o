import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


def criar_planilha_medicao(nome_arquivo="planilha_medicao.xlsx"):
    # Inicializa o workbook e seleciona a aba ativa
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Medição"

    # Habilitar exibição de linhas de grade
    ws.views.sheetView[0].showGridLines = True

    # Definição de estilos visuais (Paleta Azul Corporativo)
    HEADER_FILL = PatternFill(
        start_color="1F4E78", end_color="1F4E78", fill_type="solid"
    )
    HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    TITLE_FONT = Font(name="Calibri", size=14, bold=True, color="1F4E78")
    BOLD_FONT = Font(name="Calibri", size=11, bold=True)
    REGULAR_FONT = Font(name="Calibri", size=11)

    # Bordas
    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )
    total_border = Border(
        top=Side(style="thin", color="000000"),
        bottom=Side(style="double", color="000000"),
    )

    # Cabeçalho do Projeto / Informações Gerais
    ws["A1"] = "RELATÓRIO DE MEDIÇÃO DE OBRA / SERVIÇO"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:I1")

    ws["A3"] = "Contratante:"
    ws["B3"] = "Nome do Cliente S.A."
    ws["A4"] = "Contratada:"
    ws["B4"] = "Nome da Empresa Executante"
    ws["A5"] = "Medição Nº:"
    ws["B5"] = 1

    for row in range(3, 6):
        ws[f"A{row}"].font = BOLD_FONT
        ws[f"B{row}"].font = REGULAR_FONT

    # Cabeçalhos da Tabela de Medição
    headers = [
        "Item",
        "Descrição dos Serviços",
        "Unidade",
        "Qtd. Contrato",
        "Vlr. Unitário (R$)",
        "Vlr. Total Contrato (R$)",
        "Medido Anterior",
        "Medido Atual",
        "Total Medido",
    ]

    header_row = 7
    for col_num, header_title in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col_num, value=header_title)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )
        cell.border = thin_border
    ws.row_dimensions[header_row].height = 30

    # Dados de Exemplo (Itens da Medição)
    # Formato: (Item, Descrição, Unidade, Qtd Contrato, Vlr Unitário, Medido Anterior, Medido Atual)
    dados = [
        (
            "1.0",
            "Serviços Preliminares e Mobilização",
            "VB",
            1.0,
            15000.00,
            0.0,
            1.0,
        ),
        ("2.0", "Locação da Obra", "m²", 500.0, 15.00, 200.0, 300.0),
        ("3.0", "Escavação Manual de Valas", "m³", 120.0, 85.50, 50.0, 70.0),
        ("4.0", "Concretagem de Fundações (Fck 25MPa)", "m³", 45.0, 650.00, 10.0, 25.0),
    ]

    start_row = 8
    for i, row_data in enumerate(dados):
        current_row = start_row + i
        item, desc, unidade, qtd_contrato, vlr_unit, med_ant, med_atual = row_data

        # Inserção de valores estáticos
        ws.cell(row=current_row, column=1, value=item).alignment = Alignment(
            horizontal="center"
        )
        ws.cell(row=current_row, column=2, value=desc).alignment = Alignment(
            horizontal="left"
        )
        ws.cell(row=current_row, column=3, value=unidade).alignment = Alignment(
            horizontal="center"
        )

        c_qtd = ws.cell(row=current_row, column=4, value=qtd_contrato)
        c_qtd.number_format = "#,##0.00"

        c_vlr = ws.cell(row=current_row, column=5, value=vlr_unit)
        c_vlr.number_format = "R$ #,##0.00"

        # Fórmulas Excel: Vlr Total Contrato = Qtd Contrato * Vlr Unitário
        c_vlr_tot = ws.cell(
            row=current_row, column=6, value=f"=D{current_row}*E{current_row}"
        )
        c_vlr_tot.number_format = "R$ #,##0.00"

        c_med_ant = ws.cell(row=current_row, column=7, value=med_ant)
        c_med_ant.number_format = "#,##0.00"

        c_med_atu = ws.cell(row=current_row, column=8, value=med_atual)
        c_med_atu.number_format = "#,##0.00"

        # Fórmulas Excel: Total Medido = Medido Anterior + Medido Atual
        c_tot_med = ws.cell(
            row=current_row, column=9, value=f"=G{current_row}+H{current_row}"
        )
        c_tot_med.number_format = "#,##0.00"

        # Aplicar fontes e bordas em toda a linha
        for col_num in range(1, 10):
            cell = ws.cell(row=current_row, column=col_num)
            cell.font = REGULAR_FONT
            cell.border = thin_border

    # Linha de Total Geral
    last_data_row = start_row + len(dados) - 1
    total_row = last_data_row + 2

    ws.cell(row=total_row, column=2, value="TOTAL GERAL").font = BOLD_FONT
    ws.cell(row=total_row, column=2).alignment = Alignment(horizontal="right")

    c_tot_contrato = ws.cell(
        row=total_row, column=6, value=f"=SUM(F{start_row}:F{last_data_row})"
    )
    c_tot_contrato.font = BOLD_FONT
    c_tot_contrato.number_format = "R$ #,##0.00"
    c_tot_contrato.border = total_border

    # Ajuste automático inteligente da largura das colunas
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.row < 7:  # Ignorar cabeçalho do projeto no cálculo de largura
                continue
            if cell.value:
                val_str = str(cell.value)
                if len(val_str) > max_len:
                    max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # Salva o arquivo gerado
    wb.save(nome_arquivo)
    print(f"Planilha de medição gerada com sucesso: '{nome_arquivo}'")


if __name__ == "__main__":
    criar_planilha_medicao()
