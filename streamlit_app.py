import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

df = 'df_sentiment.csv'
df = pd.read_csv(df)

# Función para filtrar los datos
def filtrar_datos(df, condition, age_range, sex):
    df_filtrado = df[(df['Condition'] == condition) &
                     (df['Age'] == age_range) &
                     (df['Sex'] == sex)]
    return df_filtrado

# Función para agregar los datos
def agregar_datos(df_filtrado):
    agregados = df_filtrado.groupby('Drug').agg({
        'sentiment_score': 'mean',
        'Effectiveness': 'mean',
        'Satisfaction': 'mean'
    }).reset_index()

    side_effects = df_filtrado.iloc[:, 15:].sum().sort_values(ascending=False).head(20)

    return agregados, side_effects

# Función para recomendar medicamentos
def recomendar_medicamentos(df, condition, age_range, sex):
    df_filtrado = filtrar_datos(df, condition, age_range, sex)
    if df_filtrado.empty:
        return pd.DataFrame(), pd.DataFrame()

    agregados, efectos_secundarios = agregar_datos(df_filtrado)

    # Ordenar los medicamentos por 'sentiment_score', 'Effectiveness' y 'Satisfaction'
    recomendados = agregados.sort_values(by=['sentiment_score', 'Effectiveness', 'Satisfaction'], ascending=False)

    # Crear un DataFrame para la tabla de recomendaciones con efectos secundarios
    result_list = []

    efectos_secundarios_indices = efectos_secundarios.index.tolist()

    for _, row in recomendados.iterrows():
        drug_name = row['Drug']
        drug_side_effects = df_filtrado[df_filtrado['Drug'] == drug_name].iloc[:, 15:].sum()

        # Asegurarse de que las longitudes coincidan
        drug_side_effects = drug_side_effects.reindex(efectos_secundarios_indices, fill_value=0)

        drug_row = pd.Series([drug_name] + drug_side_effects.tolist(), index=['Drug'] + efectos_secundarios_indices)
        result_list.append(drug_row)

    result_df = pd.DataFrame(result_list)

    return recomendados, result_df

# Interfaz de usuario con Streamlit
st.title("Sistema de Recomendación de Medicamentos")

# Dropdown para seleccionar la condición
condition_options = df['Condition'].unique().tolist()
condition = st.selectbox("Seleccione la condición", options=condition_options)

# # Campo de texto para escribir la condición
# condition_text = st.text_input("O escriba su condición", value="")

# if condition_text:
#     condition = condition_text

# Dropdown para seleccionar el rango de edad
age_range_options = df['Age'].unique().tolist()
age_range = st.selectbox("Seleccione el rango de edad", options=age_range_options)

# Dropdown para seleccionar el sexo
sex_options = df['Sex'].unique().tolist()
sex = st.selectbox("Seleccione el sexo", options=sex_options)

# Botón para ejecutar la recomendación
if st.button("Recomendar Medicamentos"):
    recomendados, tabla_efectos_secundarios = recomendar_medicamentos(df, condition, age_range, sex)

    st.subheader("Recomendaciones de Medicamentos")
    st.dataframe(recomendados)

    st.subheader("Tabla de Recomendaciones con Efectos Secundarios")
    st.dataframe(tabla_efectos_secundarios)
