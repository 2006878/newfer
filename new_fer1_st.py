import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from newfer_st import caminho_do_arquivo


# Carreguando o ícone da aba
favicon = "img/zayon_icon.jpeg"

# Configurações da página Streamlit
st.set_page_config(page_title="Zayon - NewFer", page_icon=favicon, layout="wide")

# Adicionando a logo da empresa
logo_path = "img/logo_zayon.png"  # Substitua pelo caminho real para a sua logo
logo = Image.open(logo_path)

# Exibindo a logo no Streamlit
st.image(logo, use_column_width=False, width=250)

# Carregando a tabela específica em um DataFrame
nome_tabela_2 = 'DATA SET 2'
try:
    df = pd.read_excel(caminho_do_arquivo, sheet_name=nome_tabela_2)
except Exception as e:
    st.error(f"Erro ao importar dados da tabela '{nome_tabela_2}': {str(e)}")

# Função para aplicar a lógica de preenchimento
def custom_fillna(column):
    if column.name == 'pressure (mbar).1':
        # Preencher com a média
        return column.fillna(column.mean())
    elif column.name == 'Flow rate [Nm³/h] with Error':
        # Preencher com 0
        return column.fillna(0)
    else:
        # Manter outros valores como estão
        return column

# Aplicar a função para preenchimento personalizado
df = df.apply(custom_fillna)

# Substituir '-' por NaN antes de aplicar as condições acima, pode fazer algo assim:
df.replace('-', pd.NA, inplace=True)

# Selecionando as colunas relevantes
cols_to_plot = ['Time [min]', 'Zone', 'pressure (mbar)',
       'pressure (mbar).1', 'Flow rate [Nm³/h] with Error',
       'Flow rate [Nm³/h]', 'T SP above', 'T PV above', 'Bed h 40 cm',
       'Bed h 32 cm', 'Bed h 26 cm', 'Bed h 18 cm', 'Bed h 10 cm', 'Bed Tm',
       'Bed Tspread [K]}', 'T SP below [°C]', 'T PV below [°C]', 'O2 dry [%]',
       'O2 wet [%]', 'SO2 [mg/m³]', 'Nox [mg/m³]', 'CO2 [%]', 'CO [mg/m³]']

df_selected = df[cols_to_plot]

for column in df_selected:
    df_selected[column] = pd.to_numeric(df_selected[column], errors='coerce')

# Criando o gráfico interativo
fig2 = px.line(df_selected, x='Time [min]', y=cols_to_plot, title='Time Series Visualization of Process Variables',
              labels={'value': 'Value', 'variable': 'Variable'},
              line_shape='linear')

# Adicionando texto explicativo abaixo do segundo gráfico
st.text("The line plot above shows the time series visualization of various process variables. "
        "You can click on the legend to hide or show specific variables.")

# Exibindo o gráfico
st.plotly_chart(fig2, use_container_width=True)

# Criando o mapa de calor
correlation_heatmap = df_selected.corr()

# Exibindo o mapa de calor
st.write("##### Correlation Heatmap (0 = No correlation / 1 = Maximum Positive Correlation / -1 Maximum Negative Correlation)")
st.write(correlation_heatmap.style.background_gradient(cmap='coolwarm'))

