import streamlit as st
import pandas as pd

# Cargar el DataFrame
df = pd.read_csv('df_sentiment.csv')

# Función para convertir valores numéricos a estrellas
def convert_to_stars(value, max_stars=5):
    stars = '⭐' * int(value)
    value = round(value, 1)
    return f"{stars} ({value})"

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

    total_count = len(df_filtrado)
    side_effects_percentage = (df_filtrado.iloc[:, 15:].apply(pd.to_numeric, errors='coerce').gt(0).sum() / total_count * 100).sort_values(ascending=False).head(20)

    return agregados, side_effects_percentage

# Función para recomendar medicamentos
def recomendar_medicamentos(df, condition, age_range, sex):
    df_filtrado = filtrar_datos(df, condition, age_range, sex)
    if df_filtrado.empty:
        return pd.DataFrame(), pd.DataFrame()

    agregados, efectos_secundarios = agregar_datos(df_filtrado)

    # Ordenar los medicamentos por 'sentiment_score', 'Effectiveness' y 'Satisfaction'
    recomendados = agregados.sort_values(by=['sentiment_score', 'Effectiveness', 'Satisfaction'], ascending=False)

    # Convertir valores de 'sentiment_score', 'Satisfaction' y 'Effectiveness' a estrellas
    recomendados['sentiment_score'] = recomendados['sentiment_score'].apply(convert_to_stars)
    recomendados['Satisfaction'] = recomendados['Satisfaction'].apply(convert_to_stars)
    recomendados['Effectiveness'] = recomendados['Effectiveness'].apply(convert_to_stars)

    # Crear un DataFrame para la tabla de recomendaciones con efectos secundarios
    result_list = []
    efectos_secundarios_indices = efectos_secundarios.index.tolist()

    for _, row in recomendados.iterrows():
        drug_name = row['Drug']
        drug_side_effects = df_filtrado[df_filtrado['Drug'] == drug_name].iloc[:, 15:].apply(pd.to_numeric, errors='coerce').gt(0).sum() / len(df_filtrado) * 100

    result_df = pd.DataFrame(result_list)

    return recomendados, result_df

# Interfaz de usuario con Streamlit
st.title("💊 Sistema de Recomendación de Medicamentos")

# Emojis para cada sección
st.markdown("### 🩺 Seleccione su Condición")

# Dropdown para seleccionar la condición
condition_options = df['Condition'].unique().tolist()
condition = st.selectbox("Seleccione la condición", options=condition_options)

# Filtrar DataFrame basado en la condición seleccionada
filtered_df = df[df['Condition'] == condition]

st.markdown("### 🚻 Seleccione su Sexo")

# Dropdown para seleccionar el sexo basado en la condición seleccionada
sex_options = filtered_df['Sex'].unique().tolist()
sex = st.selectbox("Seleccione el sexo", options=sex_options)

# Filtrar DataFrame basado en la condición y el sexo seleccionados
filtered_df = filtered_df[filtered_df['Sex'] == sex]

st.markdown("### Seleccione su Rango de Edad")

# Dropdown para seleccionar el rango de edad basado en la condición y el sexo seleccionados
age_range_options = filtered_df['Age'].astype(str).unique().tolist()
age_range = st.selectbox("Seleccione el rango de edad", options=age_range_options)

# Botón para ejecutar la recomendación
if st.button("🔍 Recomendar Medicamentos"):
    recomendados, tabla_efectos_secundarios = recomendar_medicamentos(df, condition, age_range, sex)

    st.markdown("## 💊 Recomendaciones de Medicamentos")
    st.markdown(recomendados.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("## 📊 Tabla de Recomendaciones con Efectos Secundarios")

    st.markdown(tabla_efectos_secundarios.to_html(escape=False, index=False), unsafe_allow_html=True)
