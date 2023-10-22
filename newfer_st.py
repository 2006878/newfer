import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Carreguando o ícone da aba
favicon = "img/logo_zayon.jpeg"

# Configurações da página Streamlit
st.set_page_config(page_title="Zayon Data Mine - NewFer", page_icon=favicon, layout="wide")

# Adicionando a logo da empresa
logo_path = "img/logo.jpeg"  # Caminho real para a logo
logo = Image.open(logo_path)

# Exibindo a logo no Streamlit
st.image(logo, use_column_width=False, width=100)
# Carregar dados
caminho_do_arquivo = 'data/dataset.xlsx'

# Carregando a tabela específica em um DataFrame
nome_tabela_1 = 'DATA SET 1'
try:
    dados = pd.read_excel(caminho_do_arquivo, sheet_name=nome_tabela_1)
except Exception as e:
    st.error(f"Erro ao importar dados da tabela '{nome_tabela_1}': {str(e)}")

# Função para remover outliers usando o método IQR
def remove_outliers(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

# Remover outliers das colunas relevantes
dados_filtered = remove_outliers(dados, 'Product Pellets')
dados_filtered = remove_outliers(dados_filtered, 'DDRS Rejects/Feed')
dados_filtered = remove_outliers(dados_filtered, 'SDRS Rejects/Feed')

# Extraindo as colunas relevantes do DataFrame filtrado
dates = dados_filtered['Date']
pellets = dados_filtered['Product Pellets']
ddrs_rejects = dados_filtered['DDRS Rejects/Feed']
sdrs_rejects = dados_filtered['SDRS Rejects/Feed']

# Interface do Streamlit
st.title("Zayon Data Mine - NewFer")

# Criando DataFrame para Plotly
df_plotly = pd.DataFrame({'Date': dates, 'Pellets': pellets, 'DDRS Rejects': ddrs_rejects * 100, 'SDRS Rejects': sdrs_rejects * 100})

# Criando gráfico interativo com Plotly Express
fig1 = px.scatter(df_plotly, x='Pellets', y=['DDRS Rejects', 'SDRS Rejects'],
                 labels={'variable': 'Select view', 'value': 'Percentage'},
                 title='Evolution of DDRS and SDRS in relation to Product Pellets (No Outliers)',
                 hover_data=['Date'], trendline='ols',
                 color_discrete_sequence=['#1f77b4', '#ff7f0e'])  # Defina aqui as cores desejadas

# Exibindo o gráfico interativo
st.plotly_chart(fig1, use_container_width=True)

# Adicionando texto explicativo
st.text("The scatter plot above shows the evolution of DDRS and SDRS in relation to Product Pellets. "
        "You can click on the legend to hide or show specific variables.")

# Carregando a tabela específica em um DataFrame
nome_tabela_2 = 'DATA SET 2'
try:
    df = pd.read_excel(caminho_do_arquivo, sheet_name=nome_tabela_2)
except Exception as e:
    st.error(f"Erro ao importar dados da tabela '{nome_tabela_2}': {str(e)}")

# Selecionando as colunas relevantes
cols_to_plot = ['Time [min]', 'pressure (mbar)', 'Flow rate [Nm³/h]', 'T SP above', 'T PV above',
                'Bed h 40 cm', 'Bed h 32 cm', 'Bed h 26 cm', 'Bed h 18 cm', 'Bed h 10 cm',
                'Bed Tm', 'Bed Tspread [K]}', 'T SP below [°C]', 'T PV below [°C]',
                'O2 dry [%]', 'O2 wet [%]', 'SO2 [mg/m³]', 'Nox [mg/m³]', 'CO2 [%]', 'CO [mg/m³]']

df_selected = df[cols_to_plot]

# Criando o gráfico interativo
fig2 = px.line(df_selected, x='Time [min]', y=cols_to_plot, title='Time Series Visualization of Process Variables',
              labels={'value': 'Value', 'variable': 'Variable'},
              line_shape='linear')

# Exibindo o gráfico
st.plotly_chart(fig2, use_container_width=True)

# Adicionando texto explicativo abaixo do segundo gráfico
st.text("The line plot above shows the time series visualization of various process variables. "
        "You can click on the legend to hide or show specific variables.")
