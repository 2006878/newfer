import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from sklearn.preprocessing import MinMaxScaler
from st_pages import Page, show_pages

# Menu das análises
show_pages(
    [
        Page("newfer_st.py", "Product Pellets, DDRS and SDRS", icon="📈"),
        Page("new_fer1_st.py", "Visualization of various process variables", icon="📈")
    ]
)

# Carreguando o ícone da aba
favicon = "img/zayon_icon.jpeg"

# Configurações da página Streamlit
st.set_page_config(page_title="Zayon - NewFer", page_icon=favicon, layout="wide")

# Adicionando a logo da empresa
logo_path = "img/logo_zayon.png"  # Substitua pelo caminho real para a sua logo
logo = Image.open(logo_path)

# Exibindo a logo no Streamlit
st.image(logo, use_column_width=False, width=250)

# Carregar dados
caminho_do_arquivo = 'data/dataset.xlsx'

# Carregando a tabela específica em um DataFrame
nome_tabela_1 = 'DATA SET 1'
try:
    dados = pd.read_excel(caminho_do_arquivo, sheet_name=nome_tabela_1)
except Exception as e:
    st.error(f"Erro ao importar dados da tabela '{nome_tabela_1}': {str(e)}")

# Interface do Streamlit
st.title("Zayon Data Mining - NewFer")

sensibilidade_outlyer = st.slider("Outlyer sensitivity:", min_value=1.0, max_value=7.5, value=4.0)

# Função para remover outliers usando o método IQR
def remove_outliers(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - sensibilidade_outlyer * IQR
    upper_bound = Q3 +  sensibilidade_outlyer * IQR
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

# Criando DataFrame para Plotly
df_plotly = pd.DataFrame({'Date': dates, 'Pellets': pellets, 'DDRS Rejects': ddrs_rejects * 100, 'SDRS Rejects': sdrs_rejects * 100})

# Criando gráfico interativo com Plotly Express
fig1 = px.scatter(df_plotly, x='Pellets', y=['DDRS Rejects', 'SDRS Rejects'],
                 labels={'variable': 'Select view', 'value': 'Percentage'},
                 title='Evolution of DDRS and SDRS in relation to Product Pellets (No Outliers)',
                 hover_data=['Date'], trendline='ols',
                 color_discrete_sequence=['#1f77b4', '#ff7f0e'])  # Defina aqui as cores desejadas

# Adicionando texto explicativo
st.text("The scatter plot above shows the evolution of DDRS and SDRS in relation to Product Pellets. "
        "You can click on the legend to hide or show specific variables.")

# Exibindo o gráfico interativo
st.plotly_chart(fig1, use_container_width=True)

# Criando o gráfico com Plotly Express
fig4 = px.line(dados_filtered, x='Date', y=['Product Pellets'],
              labels={'value': 'Metric', 'variable': 'Category'},
              title='Historical Evolution of Product Pellets',
              line_shape='linear')

# Exibindo o gráfico
st.plotly_chart(fig4, use_container_width=True)

# Normalizando os dados entre 0 e 1
scaler = MinMaxScaler()

dados_filtered['DDRS Rejects/Feed Normalized'] = scaler.fit_transform(dados_filtered[['DDRS Rejects/Feed']])
dados_filtered['SDRS Rejects/Feed Normalized'] = scaler.fit_transform(dados_filtered[['SDRS Rejects/Feed']])
dados_filtered['Product Pellets Normalized'] = scaler.fit_transform(dados_filtered[['Product Pellets']])

# Criando o gráfico com Plotly Express
fig3 = px.line(dados_filtered, x='Date', y=['Product Pellets Normalized', 'DDRS Rejects/Feed Normalized', 'SDRS Rejects/Feed Normalized'],
              labels={'value': 'Metric', 'variable': 'Category'},
              title='Historical Evolution of Product Pellets, BDRS and SDRS (standardized)',
              line_shape='linear')

# Exibindo o gráfico
st.plotly_chart(fig3, use_container_width=True)
