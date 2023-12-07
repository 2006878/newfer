import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Carregar dados
caminho_do_arquivo = 'data/dataset.xlsx'

# Carregando a tabela específica em um DataFrame
nome_tabela_2 = 'DATA SET 2'
try:
    df = pd.read_excel(caminho_do_arquivo, sheet_name=nome_tabela_2)
except Exception as e:
    print(f"Erro ao importar dados da tabela '{nome_tabela_2}': {str(e)}")

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
        if column.name == 'O2 dry [%]':
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

        elif column.name == 'Time [min]':
            # Calcular Time [min] a partir de Time [sec]
            return np.where(df['Time [sec]'].notna(), df['Time [sec]'] / 60, column)

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

            # Dividir o conjunto de dados em treinamento e teste
            df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)

            if not df_train.empty:
                # Separar colunas de características (X) e alvo (y) no conjunto de treinamento
                X_train = df_train[cols_for_training]
                y_train = df_train[column]

                # Separar colunas de características (X) e alvo (y) no conjunto de teste
                X_test = df_test[cols_for_training]
                y_test = df_test[column]

                # Remover linhas com valores nulos nas colunas de treinamento
                mask_train = X_train[cols_for_training].notna().all(axis=1)
                X_train = X_train[mask_train]
                y_train = y_train[mask_train]

                # Remover linhas com valores nulos nas colunas de teste
                mask_test = X_test[cols_for_training].notna().all(axis=1)
                X_test = X_test[mask_test]
                y_test = y_test[mask_test]

                if not X_train.empty and not X_test.empty:
                    # Treinar o modelo de regressão linear
                    model = LinearRegression()
                    model.fit(X_train, y_train)

                    # Fazer predições nas colunas do conjunto de teste
                    y_pred = model.predict(X_test)

                    # Avaliar o desempenho do modelo (opcional)
                    mse = mean_squared_error(y_test, y_pred)
                    if column == 'Flow rate [Nm³/h] with Error':
                        print(f'Mean Squared Error for {column}: {mse}')
                    print(f'Mean Squared Error for {column}: {mse}')

                    # Fazer predições nas colunas do conjunto de dados original com valores faltantes
                    X_pred = df[df[column].isna()][cols_for_training]

                    if not X_pred.empty:
                        # Remover linhas com valores nulos nas colunas de predição
                        mask_pred = X_pred[cols_for_training].notna().all(axis=1)
                        X_pred = X_pred[mask_pred]

                        if not X_pred.empty:
                            df.loc[df[column].isna(), column] = model.predict(X_pred)

    return df


for column in df[cols_to_plot]:
    df[column] = pd.to_numeric(df[column], errors='coerce')

# Substituir '-' por NaN antes de aplicar as condições acima
df.replace(['-', '0', '0.0', ''], pd.NA, inplace=True)

# Aplicar a função para preenchimento personalizado
df = df.apply(custom_fillna)

df = ml_fillna(df)