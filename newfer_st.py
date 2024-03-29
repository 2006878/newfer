import streamlit as st
from streamlit import file_uploader
import pandas as pd
import plotly.express as px
from PIL import Image
from sklearn.preprocessing import MinMaxScaler
from st_pages import Page, show_pages
import numpy as np

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

# Interface do Streamlit
st.title("Zayon Data Mining - NewFer")

@st.cache_resource
def load_data(file):
    return file

data = None

# Inicializa a variável de estado se não estiver definida
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

uploaded_file = file_uploader("Choose an xlsx file containing the updated table", type="xlsx")

if uploaded_file:
    
    # Armazenar o arquivo em uma variável de estado
    st.session_state.uploaded_file = uploaded_file

    # Armazenar o arquivo em cache
    data = load_data(st.session_state.uploaded_file)

if st.session_state.uploaded_file is not None:
    
    if data is None:
        data = st.session_state.uploaded_file

    # Carregando a tabela específica em um DataFrame
    nome_tabela_1 = 'DATA SET 1'
    try:
        dados = pd.read_excel(data, sheet_name=nome_tabela_1)
    except Exception as e:
        st.error(f"Erro ao importar dados da tabela '{nome_tabela_1}': {str(e)}")

    st.write("File uploaded: ", st.session_state.uploaded_file.name)

    # sensibilidade_outlier = st.checkbox("Outlier correction", False)
    sensibilidade_outlier = st.slider("Outlier sensitivity (1 = Highest sensitivity / 10 With outlier):", min_value=1.0, max_value=10.0, value=5.0)

    # Função para remover outliers usando o método IQR
    def remove_outliers(data, column):
        if sensibilidade_outlier == 10:
            return data
        else:
            Q1 = data[column].quantile(0.25)
            Q3 = data[column].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((data[column] < (Q1 - sensibilidade_outlier * IQR)) | (data[column] > (Q3 + sensibilidade_outlier * IQR)))

            # Substituir outliers por np.nan
            data.loc[outliers, column] = np.nan

            # Preencher np.nan com valores interpolados
            data[column] = data[column].interpolate()
            return data[column]

    # Remover outliers das colunas relevantes
    for column in dados.columns:
        column = remove_outliers(dados, column)
    
    dados_filtered = dados

    dados_filtered['Date'] = dados['Date']
    
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
                    title='Evolution of DDRS and SDRS in relation to Product Pellets',
                    hover_data=['Date'], trendline='ols',
                    color_discrete_sequence=['#1f77b4', '#ff7f0e'])  # Defina aqui as cores desejadas

    # Adicionando texto explicativo
    st.write("The scatter plot above shows the evolution of DDRS and SDRS in relation to Product Pellets. "
            "You can click on the legend to hide or show specific variables.")

    # Exibindo o gráfico interativo
    st.plotly_chart(fig1, use_container_width=True)

    st.write("##### Mean values of the variables:")
    st.write("Mean DDRS Rejects/Feed: " + str(dados_filtered['DDRS Rejects/Feed'].mean()*100) + "%")
    st.write("Mean SDRS Rejects/Feed: " + str(dados_filtered['SDRS Rejects/Feed'].mean()*100) + "%")
    st.write("Mean Product Pellets: " + str(dados_filtered['Product Pellets'].mean()))

    colunas_desejadas = ['Product Pellets', 'DDRS Rejects/Feed', 'SDRS Rejects/Feed']
    dados_1 = dados_filtered[colunas_desejadas]

    if st.checkbox("Show normalized data with Product Pellets", False):
        # Normalizando os dados entre 0 e 1
        scaler = MinMaxScaler()

        dados_filtered['DDRS Rejects/Feed'] = scaler.fit_transform(dados_filtered[['DDRS Rejects/Feed']])
        dados_filtered['SDRS Rejects/Feed'] = scaler.fit_transform(dados_filtered[['SDRS Rejects/Feed']])
        dados_filtered['Product Pellets'] = scaler.fit_transform(dados_filtered[['Product Pellets']])
        
        # Criando o gráfico com Plotly Express
        fig2 = px.line(dados_filtered, x='Date', y=['DDRS Rejects/Feed', 'SDRS Rejects/Feed', 'Product Pellets'],
                labels={'value': 'Values (%)', 'variable': 'Category'},
                title='Historical Evolution of Product Pellets, DDRS and SDRS (Standardized)',
                line_shape='linear')
        # Exibindo o gráfico
        st.plotly_chart(fig2, use_container_width=True)

    else:
        dados_filtered['DDRS Rejects/Feed'] = dados_filtered[['DDRS Rejects/Feed']]*100
        dados_filtered['SDRS Rejects/Feed'] = dados_filtered[['SDRS Rejects/Feed']]*100
        
        # Preenchendo valores ausentes com 0
        dados_filled = dados_filtered.fillna(0)

        # Criando o gráfico com Plotly Express
        fig2 = px.bar(dados_filled, x='Date', y=['DDRS Rejects/Feed', 'SDRS Rejects/Feed'],
                    labels={'value': 'Values (%)', 'variable': 'Category'},
                    title='Historical Evolution of DDRS and SDRS',
                    barmode='relative')
        
        # Exibindo o gráfico
        st.plotly_chart(fig2, use_container_width=True)

    # Criando o mapa de calor
    correlation_heatmap = dados_1.corr()

    # Exibindo o mapa de calor
    st.write("##### Correlation heat map considering sensitivity to outliers (0 = No correlation / 1 = Maximum Positive Correlation / -1 Maximum Negative Correlation)")
    st.write(correlation_heatmap.style.background_gradient(cmap='coolwarm'))

    st.write("##### Descriptive statistics")
    st.write(dados_filtered.describe())
    st.write("count: The number of non-null observations. This excludes missing values.")
    st.write("mean: The arithmetic mean of the values.")
    st.write("std: The standard deviation, a measure of the dispersion of values around the mean.")
    st.write("min: The minimum value in the column.")
    st.write("25%: The first quartile, representing the value below which 25% of the data is found.")
    st.write("50%: The second quartile, which is the median. It represents the value below which 50% of the data is found.")
    st.write("75%: The third quartile, representing the value below which 75% of the data is found.")
    st.write("max: The maximum value in the column.")
