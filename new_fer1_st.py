import streamlit as st
import plotly.express as px
from PIL import Image
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.ensemble import HistGradientBoostingRegressor
from streamlit import file_uploader

# Carreguando o ícone da aba
favicon = "img/zayon_icon.jpeg"

# Configurações da página Streamlit
st.set_page_config(page_title="Zayon - NewFer", page_icon=favicon, layout="wide")

# Adicionando a logo da empresa
logo_path = "img/logo_zayon.png"  # Substitua pelo caminho real para a sua logo
logo = Image.open(logo_path)

# Exibindo a logo no Streamlit
st.image(logo, use_column_width=False, width=250)

@st.cache_resource
def load_data(file):
    return file

# Inicializa a variável de estado se não estiver definida
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

uploaded_file = file_uploader("Choose an xlsx file containing the updated table", type="xlsx")

if uploaded_file:
    
    # Armazenar o arquivo em uma variável de estado
    st.session_state.uploaded_file = uploaded_file

    # Armazenar o arquivo em cache
    load_data(st.session_state.uploaded_file)

if not st.session_state.uploaded_file:
    st.write("Please upload a file of type: " + "xlsx")

else:
    # Carregando a tabela específica em um DataFrame
    nome_tabela_2 = 'DATA SET 2'

    # Especifique as colunas desejadas
    colunas_desejadas = ['Time [sec]', 'Time [min]', 'Zone', 'Unnamed', 'pressure (mbar)',
        'pressure (mbar).1', 'Flow rate [Nm³/h] with Error',
        'Flow rate [Nm³/h]', 'T SP above', 'T PV above', 'Bed h 40 cm',
        'Bed h 32 cm', 'Bed h 26 cm', 'Bed h 18 cm', 'Bed h 10 cm', 'Bed Tm',
        'Bed Tspread [K]}', 'T SP below [°C]', 'T PV below [°C]', 'O2 dry [%]',
        'O2 wet [%]', 'SO2 [mg/m³]', 'Nox [mg/m³]', 'CO2 [%]', 'CO [mg/m³]']

    # Carregando o DataFrame a partir da linha 5 e renomeando as colunas
    try:
        df = pd.read_excel(st.session_state.uploaded_file, sheet_name=nome_tabela_2, skiprows=4)
        # st.write(st.session_state.uploaded_file)
        df.columns = colunas_desejadas
    except Exception as e:
        st.error(f"Erro ao importar dados da tabela '{nome_tabela_2}': {str(e)}")

    # Selecionando as colunas relevantes
    cols_to_plot = ['Time [min]', 'pressure (mbar)',
        'pressure (mbar).1', 'Flow rate [Nm³/h] with Error',
        'Flow rate [Nm³/h]', 'T SP above', 'T PV above', 'Bed h 40 cm',
        'Bed h 32 cm', 'Bed h 26 cm', 'Bed h 18 cm', 'Bed h 10 cm', 'Bed Tm',
        'Bed Tspread [K]}', 'T SP below [°C]', 'T PV below [°C]', 'O2 dry [%]',
        'O2 wet [%]', 'SO2 [mg/m³]', 'Nox [mg/m³]', 'CO2 [%]', 'CO [mg/m³]']

    # Função para aplicar a lógica de preenchimento

    def custom_fillna(column):
        if column.isna().any() or (column.astype(str).str.strip() == '0').any() or (column.astype(str).str.strip() == '-').any() or (column.astype(str).str.strip() == '0.0').any():
            if column.name == 'Time [min]':
                # Calcular Time [min] a partir de Time [sec]
                return np.where(df['Time [sec]'].notna(), df['Time [sec]'] / 60, column)
            
            elif column.name == 'O2 dry [%]':
                return np.where((df['Time [min]'].notna()) & (df['% O2 dry [%]'].notna()), np.minimum(df['Time [min]'], df['% O2 dry [%]']), column)

            elif column.name == 'Bed h 40 cm':
                return np.where((df['Time [min]'].notna()) & (df['Bed h 40 cm'].notna()), np.minimum(df['Time [min]'], df['Bed h 40 cm']), column)

            elif column.name == 'Hood':
                return np.where((df['Time [min]'].notna()) & (df['T PV above'].notna()), np.minimum(df['Time [min]'], df['T PV above']), column)

            elif column.name == 'Bed h 10 cm':
                return np.where((df['Time [min]'].notna()) & (df['Bed h 10 cm'].notna()), np.minimum(df['Time [min]'], df['Bed h 10 cm']), column)

            elif column.name == 'Bed Tm':
                # Use o método SÉRIE para buscar dados de outra coluna (assumindo que 'Dashkasan Pot Grate Tests Overview_AH.xlsx' está no mesmo diretório)
                # Certifique-se de ajustar o caminho do arquivo e as referências de coluna conforme necessário
                df_source = pd.read_excel('Dashkasan Pot Grate Tests Overview_AH.xlsx', sheet_name='FONTE ENVIADA PELO FORNECEDOR')
                valid_rows = (df['Time [min]'].notna()) & (df['Bed h 18 cm'].notna()) & (df['Bed h 10 cm'].notna())
                return np.where(valid_rows, df_source.apply(lambda row: np.mean([row['Bed h 18 cm'], row['Bed h 10 cm']]), axis=1), column)

            elif column.name == 'Bed h 32 cm':
                return np.where((df['Time [min]'].notna()) & (df['Bed h 32 cm (COL L)'].notna()), np.minimum(df['Time [min]'], df['Bed h 32 cm (COL L)']), column)

            elif column.name == 'Bed h 26 cm':
                return np.where((df['Time [min]'].notna()) & (df['Bed h 26 cm (COL M)'].notna()), np.minimum(df['Time [min]'], df['Bed h 26 cm (COL M)']), column)

            elif column.name == 'Bed h 18 cm':
                return np.where((df['Time [min]'].notna()) & (df['Bed h 18 cm (COL N)'].notna()), np.minimum(df['Time [min]'], df['Bed h 18 cm (COL N)']), column)

            elif column.name == 'SO2 [mg/m³]':
                return np.where((df['Time [min]'].notna()) & (df['O2 wet [%]'].notna()), np.minimum(df['Time [min]'], df['O2 wet [%]']), column)

            elif column.name == 'Zone':
                # Preservar os valores existentes
                return column

            elif column.name == 'Bed Tm (COL P )':
                # Calcular a média entre Bed h 40 cm e Bed h 10 cm
                return np.where((df['Bed h 40 cm'].notna()) & (df['Bed h 10 cm'].notna()), np.mean([df['Bed h 40 cm'], df['Bed h 10 cm']], axis=0), column)

            elif column.name == 'Bed Tspread [K](COL Q)':
                # Calcular a diferença entre Bed h 40 cm e Bed h 10 cm
                return np.where((df['Bed h 40 cm'].notna()) & (df['Bed h 10 cm'].notna()), np.maximum(df['Bed h 40 cm'], df['Bed h 10 cm']) - np.minimum(df['Bed h 40 cm'], df['Bed h 10 cm']), column)
            else:
                return column
        else:
            return column
        

    def ml_fillna(df):
        
        for column in cols_to_plot:
            column_numeric = pd.to_numeric(df[column], errors='coerce')

            if np.isnan(column_numeric).any() or (df[column].astype(str).str.strip() == '0').any() or (df[column].astype(str).str.strip() == '-').any() or (df[column].astype(str).str.strip() == '0').any():
                cols_for_training = cols_to_plot.copy()

                # Separar colunas de características (X) e alvo (y) no conjunto completo
                X_complete = df[cols_for_training]
                y_complete = df[column]

                # Identificar linhas com valores nulos nas colunas de predição
                mask_missing = y_complete.isna()

                # Imputação usando KNNImputer antes de remover linhas com valores nulos
                imputer = KNNImputer(n_neighbors=5)
                y_complete_imputed = imputer.fit_transform(y_complete.values.reshape(-1, 1))

                # Transformar de volta para uma Série do Pandas
                y_complete_imputed_series = pd.Series(y_complete_imputed.flatten(), index=y_complete.index)

                # Treinar o modelo de HistGradientBoostingRegressor
                model = HistGradientBoostingRegressor()
                model.fit(X_complete, y_complete_imputed_series)

                # Fazer predições nas colunas do conjunto de dados original com valores faltantes
                y_pred = model.predict(X_complete)

                # Imputar os dados preditos diretamente no DataFrame original
                df[column] = y_pred

        return df

    for column in df[cols_to_plot]:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Substituir os valores na coluna 'Time[min]' onde 'Time[sec]' é igual a 0 por 1/60
    df.loc[df['Time [sec]'] == 0, 'Time [min]'] = 1/60

    df.replace({0: np.nan, '': np.nan, '-': np.nan, '0.0': np.nan}, inplace=True)

    df = df.apply(custom_fillna, axis=1)

    df = ml_fillna(df)

    # Substituir valores vazios na coluna "Zone" por "Unnamed"
    df['Zone'].fillna('Unnamed', inplace=True)

    df_selected = df[cols_to_plot].copy()

    for column in df_selected:
        df_selected[column] = pd.to_numeric(df_selected[column], errors='coerce')


    st.write("File uploaded: ", st.session_state.uploaded_file.name)

    # Adicionando um multiselect para escolher as zonas
    selected_zones = st.multiselect("Select Zones", df["Zone"].unique(), default=df["Zone"].unique())

    # Filtrando o DataFrame com base nas zonas selecionadas
    df_filtered = df[df["Zone"].isin(selected_zones)]

    fig2 = px.line(df_filtered[cols_to_plot].melt(id_vars=['Time [min]'], var_name='Variable', value_name='Value'),
                x='Time [min]', y='Value', color='Variable',
                title='Time Series Visualization of Process Variables',
                labels={'Value': 'Value', 'Variable': 'Variable'},
                line_shape='linear')

    # Configurar traces para serem inicialmente invisíveis na legenda
    for trace in fig2.data:
        trace.update(visible='legendonly')

    # Adicionando linhas verticais para marcar os limites entre as zonas selecionadas colocando o nome da zona no meio
    for zone in selected_zones:
        zone_start = df_filtered[df_filtered['Zone'] == zone]['Time [min]'].min()
        zone_end = df_filtered[df_filtered['Zone'] == zone]['Time [min]'].max()
        fig2.add_vline(x=zone_start, line_dash='dash', line_color='gray', annotation_text=zone, annotation_position='top right')
            
    # Adicionando texto explicativo abaixo do segundo gráfico
    st.text("The line plot above shows the time series visualization of various process variables. "
            "You can click on the legend to hide or show specific variables.")

    # Ajuste da altura do layout do gráfico
    fig2.update_layout(height=600)

    # Exibindo o gráfico apenas para as colunas desejadas e zonas selecionadas
    st.plotly_chart(fig2, use_container_width=True)

    # Criando o mapa de calor
    correlation_heatmap = df_filtered[cols_to_plot].corr()

    # Exibindo o mapa de calor
    st.write("##### Correlation Heatmap (0 = No correlation / 1 = Maximum Positive Correlation / -1 Maximum Negative Correlation)")
    st.write(correlation_heatmap.style.background_gradient(cmap='coolwarm'))

    if st.checkbox("Show raw data", False):
        st.subheader('Raw data')
        st.write(df_filtered[cols_to_plot])
