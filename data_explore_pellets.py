# %%
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

# Especifique o caminho do arquivo Excel
caminho_do_arquivo = 'data/dataset.xlsx'

# %%
# Substitua 'nome_da_tabela' pelo nome da tabela específica que você deseja importar
nome_tabela_1 = 'DATA SET 1'

# Carregando a tabela específica em um DataFrame
try:
    dados = pd.read_excel(caminho_do_arquivo, sheet_name=nome_tabela_1)
    print(f"Dados da tabela '{nome_tabela_1}' importados com sucesso.")
    # Exiba o DataFrame ou realize outras operações com os dados, se necessário
except Exception as e:
    print(f"Erro ao importar dados da tabela '{nome_tabela_1}': {str(e)}")

# %%
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

# Criando DataFrame para Plotly
df_plotly = pd.DataFrame({'Date': dates, 'Pellets': pellets, 'DDRS Rejects': ddrs_rejects * 100, 'SDRS Rejects': sdrs_rejects * 100})

# Criando gráfico interativo com Plotly Express
fig = px.scatter(df_plotly, x='Pellets', y=['DDRS Rejects', 'SDRS Rejects'],
                 labels={'variable': 'Select view', 'value': 'Percentage'},
                 title='Evolution of DDRS and SDRS in relation to Product Pellets (No Outliers)',
                 hover_data=['Date'], trendline='ols')

# Exibindo o gráfico interativo
fig.show()


# %%
# Substitua 'nome_da_tabela' pelo nome da tabela específica que você deseja importar
nome_tabela_2 = 'DATA SET 2'

# Carregando a tabela específica em um DataFrame
try:
    df = pd.read_excel(caminho_do_arquivo, sheet_name=nome_tabela_2)
    print(f"Dados da tabela '{nome_tabela_2}' importados com sucesso.")
    # Exiba o DataFrame ou realize outras operações com os dados, se necessário
except Exception as e:
    print(f"Erro ao importar dados da tabela '{nome_tabela_2}': {str(e)}")

# Título da tabela "Bed height measured form grate"


# # %%
# df.info()

# # %%
# df.describe()

# %%
# Selecionando as colunas relevantes
cols_to_plot = ['Time [min]', 'pressure (mbar)', 'Flow rate [Nm³/h]', 'T SP above', 'T PV above',
                'Bed h 40 cm', 'Bed h 32 cm', 'Bed h 26 cm', 'Bed h 18 cm', 'Bed h 10 cm',
                'Bed Tm', 'Bed Tspread [K]}', 'T SP below [°C]', 'T PV below [°C]',
                'O2 dry [%]', 'O2 wet [%]', 'SO2 [mg/m³]', 'Nox [mg/m³]', 'CO2 [%]', 'CO [mg/m³]']

df_selected = df[cols_to_plot]

# Criando o gráfico interativo
fig = px.line(df_selected, x='Time [min]', y=cols_to_plot, title='Time Series Visualization of Process Variables',
              labels={'value': 'Value', 'variable': 'Variable'},
              line_shape='linear')

# Exibindo o gráfico
fig.show()



