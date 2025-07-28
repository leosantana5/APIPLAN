import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages
from io import BytesIO
import sys
import os

def carregar_configuracoes(df: pd.DataFrame):
    """Valida as configurações do DataFrame de configuração"""
    try:
        # Padronizar nomes das colunas
        df.columns = df.columns.str.strip().str.upper()

        # Verificar colunas obrigatórias
        colunas_obrigatorias = [
            'CODPLANOGRAMA', 'GDL_QTDE', 'GDL_LARGURA', 'GDL_PRATELEIRA', 'GDL_ALTURA',
            'CAO-PETISCO', 'CAO-UMIDO', 'CAO-SECO', 'GATO-PETISCO', 'GATO-UMIDO', 'GATO-SECO'
        ]

        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        if colunas_faltantes:
            raise ValueError(f"Colunas faltantes: {', '.join(colunas_faltantes)}")

        if len(df) < 1:
            raise ValueError("DataFrame de configuração está vazio")

        return df.iloc[0]  # Retorna a primeira linha como Series

    except Exception as e:
        print(f"\nERRO NO ARQUIVO DE CONFIGURAÇÃO: {str(e)}")
        print("\nO arquivo deve conter estas colunas EXATAS:")
        print("CODPLANOGRAMA, GDL_QTDE, GDL_LARGURA, GDL_PRATELEIRA, GDL_ALTURA")
        print("CAO-PETISCO, CAO-UMIDO, CAO-SECO, GATO-PETISCO, GATO-UMIDO, GATO-SECO")
        print("\nExemplo válido (pode usar ; ou , como separador):")
        print("CODPLANOGRAMA,GDL_QTDE,GDL_LARGURA,GDL_PRATELEIRA,GDL_ALTURA,CAO-PETISCO,CAO-UMIDO,CAO-SECO,GATO-PETISCO,GATO-UMIDO,GATO-SECO")
        print("Meu Planograma,8,100,5,40,10,15,20,10,10,15")
        raise

def gerar_planograma(config_df, produtos_df):
    # Carregar configurações (retorna uma Series)
    config = carregar_configuracoes(config_df)

    # Garantir que cor_rgb esteja em string "R,G,B"
    produtos_df["cor_rgb"] = produtos_df["cor_rgb"].apply(
        lambda x: ",".join(str(i) for i in x) if isinstance(x, (list, tuple)) else str(x)
    )

    
    # Extrair valores
    try:
        qtde_gondolas_total = int(config['GDL_QTDE'])
        qtde_prateleiras = int(config['GDL_PRATELEIRA'])
        largura_gondola = int(config['GDL_LARGURA'])
        altura_prateleira = int(config['GDL_ALTURA'])
        titulo_planograma = str(config['CODPLANOGRAMA'])
        espaco_entre_gondolas = 3
        
        num_gondolas_cao = round(qtde_gondolas_total * 0.6)
        num_gondolas_gato = qtde_gondolas_total - num_gondolas_cao
        
    except KeyError as e:
        print(f"\nERRO: Configuração faltando: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        print(f"\nERRO: Valor inválido: {str(e)}")
        sys.exit(1)

    # === Carregar produtos ===
    try:

        produtos_df['tipo'] = produtos_df['tipo'].str.upper()
        produtos_df['grupo'] = produtos_df['grupo'].str.upper()
        produtos_df['TIPO_TECNOLOGIA'] = produtos_df['tipo'] + '-' + produtos_df['grupo']
        
        # Mapear larguras - USANDO config (Series) aqui
        produtos_df['largura'] = produtos_df['TIPO_TECNOLOGIA'].map(
            lambda x: config[x] if x in config else None
        )
        
        if produtos_df['largura'].isnull().any():
            missing = produtos_df[produtos_df['largura'].isnull()]['TIPO_TECNOLOGIA'].unique()
            raise ValueError(f"Configurações faltando para: {', '.join(missing)}")
            
        produtos_df['cor_hex'] = produtos_df['cor_rgb'].apply(
            lambda rgb: f"#{int(rgb.split(',')[0]):02X}{int(rgb.split(',')[1]):02X}{int(rgb.split(',')[2]):02X}" 
            if pd.notnull(rgb) else '#CCCCCC'
        )
            
    except Exception as e:
        print(f"\nERRO AO CARREGAR PRODUTOS: {str(e)}")
        sys.exit(1)

    # === Cálculo de frentes necessárias ===
    frentes_por_prateleira = {
        'CAO-PETISCO': largura_gondola // config['CAO-PETISCO'],
        'CAO-UMIDO': largura_gondola // config['CAO-UMIDO'],
        'CAO-SECO': largura_gondola // config['CAO-SECO'],
        'GATO-PETISCO': largura_gondola // config['GATO-PETISCO'],
        'GATO-UMIDO': largura_gondola // config['GATO-UMIDO'],
        'GATO-SECO': largura_gondola // config['GATO-SECO'],
    }

    df_por_prateleira = pd.DataFrame.from_dict(frentes_por_prateleira, orient='index', columns=['Prat_Frentes'])
    df_por_prateleira.index.name = 'TIPO_TECNOLOGIA'
    df_por_prateleira['Prat_Qtd'] = qtde_prateleiras
    df_por_prateleira['Mod_Qtde'] = df_por_prateleira.index.map(
        lambda x: num_gondolas_cao if x.startswith('CAO') else num_gondolas_gato
    )

    # Cálculo de participação
    participacao_total_por_tipo = produtos_df.groupby('tipo')['participacao'].sum()
    participacao_por_categoria = (
        produtos_df.groupby(['tipo', 'grupo'])['participacao'].sum()
        .div(participacao_total_por_tipo, level='tipo')
        .rename('Participacao')
    )
    participacao_por_categoria.index = participacao_por_categoria.index.map(lambda x: f"{x[0]}-{x[1]}")
    df_por_prateleira['Participacao'] = participacao_por_categoria

    # Cálculo de prateleiras necessárias
    for tipo in ['CAO', 'GATO']:
        df_tipo = df_por_prateleira[df_por_prateleira.index.str.startswith(tipo)]
        total_prat = df_tipo['Prat_Qtd'].iloc[0] * df_tipo['Mod_Qtde'].iloc[0]
        
        temp = (df_tipo['Prat_Qtd'] * df_tipo['Mod_Qtde'] * df_tipo['Participacao']).round()
        df_por_prateleira.loc[df_tipo.index, 'Prat_Necessarias'] = temp.fillna(0).astype(int)
        
        soma_prat = df_por_prateleira.loc[df_tipo.index, 'Prat_Necessarias'].sum()
        diff = total_prat - soma_prat
        if diff > 0:
            # idx_ajuste = df_tipo['Participacao'].idxmax()
            # df_por_prateleira.loc[idx_ajuste, 'Prat_Necessarias'] += diff

            if not df_tipo.empty:
                idx_ajuste = df_tipo['Participacao'].idxmax()
                if pd.notna(idx_ajuste):
                    df_por_prateleira.loc[idx_ajuste, 'Prat_Necessarias'] += diff

    # Frentes totais
    df_por_prateleira['Frentes_Total'] = df_por_prateleira['Prat_Frentes'] * df_por_prateleira['Prat_Necessarias']

    # Frentes distribuídas por produto
    frentes_totais = df_por_prateleira['Frentes_Total']
    produtos_df['participacao_normalizada'] = produtos_df.groupby('TIPO_TECNOLOGIA')['participacao'].transform(lambda x: x / x.sum())
    produtos_df['Frentes_Distribuidas'] = (produtos_df['participacao_normalizada'] * produtos_df['TIPO_TECNOLOGIA'].map(frentes_totais)).round().astype(int)
    produtos_df.loc[(produtos_df['Frentes_Distribuidas'] < 2) & (produtos_df['Frentes_Distribuidas'] > 0), 'Frentes_Distribuidas'] = 2

    # Ajuste para diferenças de arredondamento
    soma_frentes_distribuidas = produtos_df.groupby('TIPO_TECNOLOGIA')['Frentes_Distribuidas'].sum()
    diferencas = frentes_totais - soma_frentes_distribuidas
    for tipo_tec, diff in diferencas.items():
        if diff == 0 or tipo_tec not in produtos_df['TIPO_TECNOLOGIA'].values:
            continue
        idx_maior = produtos_df.loc[produtos_df['TIPO_TECNOLOGIA'] == tipo_tec, 'Frentes_Distribuidas'].idxmax()
        produtos_df.loc[idx_maior, 'Frentes_Distribuidas'] += diff

    # === Distribuição dos produtos ===
    alocacoes = []
    ultima_posicao = {'CAO': {'gondola': 0, 'prateleira': 0}, 'GATO': {'gondola': num_gondolas_cao, 'prateleira': 0}}

    for tipo in ['CAO', 'GATO']:
        gondola_inicio = 0 if tipo == 'CAO' else num_gondolas_cao
        gondola_fim = gondola_inicio + (num_gondolas_cao if tipo == 'CAO' else num_gondolas_gato)
        
        for grupo in ['PETISCO', 'UMIDO', 'SECO']:
            tipo_grupo = f"{tipo}-{grupo}"
            max_frentes_por_prateleira = df_por_prateleira.loc[tipo_grupo, 'Prat_Frentes']
            largura_frente = config[tipo_grupo]  # USANDO config aqui
            
            produtos_tipo_grupo = produtos_df[(produtos_df['tipo'] == tipo) & (produtos_df['grupo'] == grupo)].to_dict('records')
            
            g = ultima_posicao[tipo]['gondola']
            p = ultima_posicao[tipo]['prateleira']
            
            if p >= qtde_prateleiras:
                g += 1
                p = 0
            
            while g < gondola_fim and len(produtos_tipo_grupo) > 0:
                gondola_x = g * (largura_gondola + espaco_entre_gondolas)
                y_base = (qtde_prateleiras - 1 - p) * altura_prateleira + 5
                x_cursor = gondola_x
                frentes_alocadas = 0
                
                produtos_na_prateleira = []
                for produto in produtos_tipo_grupo:
                    if produto['Frentes_Distribuidas'] <= 0:
                        continue
                        
                    frentes_possiveis = min(produto['Frentes_Distribuidas'], max_frentes_por_prateleira - frentes_alocadas)
                    
                    if frentes_possiveis <= 0:
                        continue
                        
                    for _ in range(frentes_possiveis):
                        alocacoes.append({
                            'gondola': g + 1,
                            'prateleira': p + 1,
                            'x': x_cursor,
                            'y': y_base,
                            'largura': largura_frente,
                            'cor': produto['cor_hex'],
                            'marca': produto['marca'],
                            'fabricante': produto['fabricante'],
                            'tipo': tipo,
                            'grupo': grupo
                        })
                        x_cursor += largura_frente
                        frentes_alocadas += 1
                        produto['Frentes_Distribuidas'] -= 1
                    
                    if produto['Frentes_Distribuidas'] > 0:
                        produtos_na_prateleira.append(produto)
                    
                    if frentes_alocadas >= max_frentes_por_prateleira:
                        break
                
                produtos_tipo_grupo = [p for p in produtos_tipo_grupo if p['Frentes_Distribuidas'] > 0]
                produtos_tipo_grupo = produtos_na_prateleira + [p for p in produtos_tipo_grupo if p not in produtos_na_prateleira]
                
                ultima_posicao[tipo]['gondola'] = g
                ultima_posicao[tipo]['prateleira'] = p + 1
                
                if p + 1 >= qtde_prateleiras:
                    g += 1
                    p = 0
                else:
                    p += 1

    # === Gerar PDF ===
    # with PdfPages('planograma_final_distribuido.pdf') as pdf:

    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
    # with PdfPages(output_path) as pdf:
        # Página 1: Planograma visual
        fig, ax = plt.subplots(figsize=(22, 10))
        ax.set_xlim(0, qtde_gondolas_total * (largura_gondola + espaco_entre_gondolas))
        ax.set_ylim(0, qtde_prateleiras * altura_prateleira + 30)
        ax.axis('off')

        # Desenhar gôndolas
        for g in range(qtde_gondolas_total):
            tipo_texto = 'CAO' if g < num_gondolas_cao else 'GATO'
            cor_fundo = '#FF8F6B' if tipo_texto == 'CAO' else '#A259FF'
            gondola_x = g * (largura_gondola + espaco_entre_gondolas)
            centro_x = gondola_x + largura_gondola / 2
            y_topo = qtde_prateleiras * altura_prateleira + 10
            ax.add_patch(patches.Rectangle((gondola_x, y_topo - 1), largura_gondola, 10, edgecolor='black', facecolor=cor_fundo))
            ax.text(centro_x, y_topo + 2, tipo_texto, ha='center', va='bottom', fontsize=10, fontweight='bold', color='white')

        # Desenhar produtos
        for item in alocacoes:
            border_color = {'PETISCO': "#7C7C78", 'UMIDO': '#7C7C78', 'SECO': "#7C7C78"}.get(item['grupo'], 'black')
            ret = patches.Rectangle((item['x'], item['y']), item['largura'], altura_prateleira - 2, 
                                  facecolor=item['cor'], edgecolor=border_color, linewidth=1.5)
            ax.add_patch(ret)
            ax.text(item['x'] + item['largura'] / 2, item['y'] + (altura_prateleira - 2) / 2, 
                   item['grupo'], ha='center', va='center', fontsize=6, rotation=90, fontweight='bold')

        # Legenda
        marcas_legenda = produtos_df[['marca', 'cor_hex']].drop_duplicates().sort_values(by='marca')
        handles = [
            Line2D([0], [0], marker='s', color='w', label=marca, markerfacecolor=cor, markersize=10)
            for marca, cor in zip(marcas_legenda['marca'], marcas_legenda['cor_hex'])
        ]
        ax.legend(handles=handles,
                loc='lower center',
                bbox_to_anchor=(0.5, -0.08),
                ncol=8,  # ajuste conforme o número de marcas
                fontsize=8,
                #title='Legenda (Marcas)',
                title_fontsize=9,
                frameon=False)

        plt.title(titulo_planograma, fontsize=10, fontweight='bold')
        plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.1)
        pdf.savefig(fig)
        plt.close()

        # Página 3: Tabela de produtos (com célula colorida)
        fig, ax = plt.subplots(figsize=(11, 8))
        ax.axis('off')

        # Preparar dados
        produtos_display = produtos_df[['cor_hex', 'marca', 'fabricante', 'tipo', 'grupo', 'participacao', 'Frentes_Distribuidas']].copy()
        produtos_display = produtos_display.rename(columns={
            'cor_hex': 'Cor',
            'marca': 'Marca',
            'fabricante': 'Fabricante',
            'tipo': 'Tipo',
            'grupo': 'Grupo',
            'participacao': 'Participação',
            'Frentes_Distribuidas': 'Frentes'
        }).reset_index(drop=True)

        from matplotlib.table import Table

        table = Table(ax, bbox=[0, 0, 1, 1])
        nrows, ncols = produtos_display.shape
        base_width = 1.0 / (ncols - 1 + 0.25)
        col_widths = [base_width * 0.25] + [base_width] * (ncols - 1)
        row_height = 1.0 / (nrows + 1)

        # Cabeçalhos
        for i, col_name in enumerate(produtos_display.columns):
            cell = table.add_cell(0, i, col_widths[i], row_height, text=col_name, loc='center', facecolor='lightgray')
            cell.get_text().set_fontweight('bold')

        # Linhas de dados
        for row in range(nrows):
            for col in range(ncols):
                value = produtos_display.iat[row, col]
                if col == 0:  # Coluna de cor
                    table.add_cell(row + 1, col, col_widths[col], row_height, text='', facecolor=value)
                else:
                    cell = table.add_cell(row + 1, col, col_widths[col], row_height, text=str(value), loc='center', facecolor='white')
                    text = cell.get_text()
                    if text is not None:
                        text.set_fontsize(8)
                        text.set_color('black')

        ax.add_table(table)
        plt.title('Distribuição de Frentes por Produto', fontsize=12, fontweight='bold', y=1.08)
        pdf.savefig(fig)
        plt.close()


        # Página 2: Tabela de cálculos (com cabeçalho estilizado)
        fig, ax = plt.subplots(figsize=(11, 8))
        ax.axis('off')

        # Dados da tabela
        df_display = df_por_prateleira.reset_index()[['TIPO_TECNOLOGIA', 'Prat_Frentes', 'Prat_Qtd', 'Mod_Qtde', 'Participacao', 'Prat_Necessarias', 'Frentes_Total']]
        df_display = df_display.round(2).reset_index(drop=True)

        from matplotlib.table import Table

        table = Table(ax, bbox=[0, 0, 1, 1])
        nrows, ncols = df_display.shape
        col_widths = [1.0 / ncols] * ncols
        row_height = 1.0 / (nrows + 1)

        # Cabeçalhos
        for i, col_name in enumerate(df_display.columns):
            cell = table.add_cell(0, i, col_widths[i], row_height, text=col_name, loc='center', facecolor='lightgray')
            cell.get_text().set_fontweight('bold')

        # Linhas de dados
        for row in range(nrows):
            for col in range(ncols):
                value = df_display.iat[row, col]
                cell = table.add_cell(row + 1, col, col_widths[col], row_height, text=str(value), loc='center', facecolor='white')
                cell.get_text().set_fontsize(8)

        ax.add_table(table)
        plt.title('Resumo por Tecnologia', fontsize=14, y=1.08)
        pdf.savefig(fig)
        plt.close()

                # Página 4: Configuração do Planograma (config_planograma.csv)
        fig, ax = plt.subplots(figsize=(11, 8))
        ax.axis('off')

        config_dict = config.to_dict()
        config_items = list(config_dict.items())
        nrows = len(config_items)
        ncols = 2
        col_widths = [0.4, 0.6]
        row_height = 1.0 / (nrows + 1)

        from matplotlib.table import Table
        table = Table(ax, bbox=[0, 0, 1, 1])

        # Cabeçalho
        headers = ['Parâmetro', 'Valor']
        for i, col_name in enumerate(headers):
            cell = table.add_cell(0, i, col_widths[i], row_height, text=col_name, loc='center', facecolor='lightgray')
            cell.get_text().set_fontweight('bold')

        # Linhas da tabela
        for row, (key, value) in enumerate(config_items):
            table.add_cell(row + 1, 0, col_widths[0], row_height, text=str(key), loc='left', facecolor='white')
            table.add_cell(row + 1, 1, col_widths[1], row_height, text=str(value), loc='center', facecolor='white')

        ax.add_table(table)
        plt.title('Parâmetros do Arquivo de Configuração (config_planograma.csv)', fontsize=12, fontweight='bold', y=1.08)
        pdf.savefig(fig)
        plt.close()

    buffer.seek(0)  # volta para o início
    return buffer  # ✅ retorna o PDF em memória


    print(f"Planograma '{titulo_planograma}' gerado com sucesso!")

# if __name__ == "__main__":
#     gerar_planograma()
