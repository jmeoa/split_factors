
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Simulación Flotación Cu", layout="wide")
st.title("Simulación de Flotación de Cobre - Indicadores Metalúrgicos")

config = st.selectbox("Selecciona configuración del circuito", [
    "Configuración estándar (R → C → RC)",
    "Recleaner sin recirculación",
    "Scavenger directo a producto final"
])

st.subheader("Diagrama del Circuito")
if config == "Configuración estándar (R → C → RC)":
    dot_code = '''digraph G {
        rankdir=LR; Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> Rougher [style=dashed, label="Conc. S → R"];
        Scavenger -> "Relave Final";
        Recleaner -> Cleaner [style=dashed, label="Cola RC → C"];
        Recleaner -> Rougher [style=dashed, label="Cola RC → R"];
    }'''
elif config == "Recleaner sin recirculación":
    dot_code = '''digraph G {
        rankdir=LR; Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> "Relave Final";
        Recleaner -> "Relave Final" [label="Cola RC"];
    }'''
else:
    dot_code = '''digraph G {
        rankdir=LR; Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> "Concentrado Final" [label="Conc. S"];
        Recleaner -> Cleaner [style=dashed, label="Cola RC → C"];
    }'''

st.graphviz_chart(dot_code)

st.subheader("Parámetros de Alimentación y Split Factors")
col1, col2 = st.columns(2)
with col1:
    feed_tph = st.number_input("Tonelaje alimentación (t/h)", value=100.0)
    feed_cu_pct = st.number_input("Ley de cobre alimentación (%)", value=1.2)
with col2:
    rougher_mass, rougher_rec = st.slider("Rougher (Masa, Recuperación)", 0.0, 1.0, (0.25, 0.90))
    scavenger_mass, scavenger_rec = st.slider("Scavenger (Masa, Recuperación)", 0.0, 1.0, (0.5, 0.6))
    cleaner_mass, cleaner_rec = st.slider("Cleaner (Masa, Recuperación)", 0.0, 1.0, (0.9, 0.98))
    recleaner_mass, recleaner_rec = st.slider("Recleaner (Masa, Recuperación)", 0.0, 1.0, (0.95, 0.99))

feed_cu_kg = feed_tph * feed_cu_pct / 100 * 1000
rougher_conc_mass = feed_tph * rougher_mass
rougher_cu_kg = feed_cu_kg * rougher_rec
rougher_cu_pct = rougher_cu_kg / rougher_conc_mass / 10 if rougher_conc_mass else 0

scavenger_conc_mass = (feed_tph - rougher_conc_mass) * scavenger_mass
scavenger_cu_kg = (feed_cu_kg - rougher_cu_kg) * scavenger_rec
scavenger_cu_pct = scavenger_cu_kg / scavenger_conc_mass / 10 if scavenger_conc_mass else 0

cleaner_conc_mass = rougher_conc_mass * cleaner_mass
cleaner_cu_kg = rougher_cu_kg * cleaner_rec
cleaner_cu_pct = cleaner_cu_kg / cleaner_conc_mass / 10 if cleaner_conc_mass else 0

recleaner_conc_mass = cleaner_conc_mass * recleaner_mass
recleaner_cu_kg = cleaner_cu_kg * recleaner_rec
recleaner_cu_pct = recleaner_cu_kg / recleaner_conc_mass / 10 if recleaner_conc_mass else 0

if config == "Configuración estándar (R → C → RC)":
    final_conc_mass = recleaner_conc_mass + scavenger_conc_mass
    final_cu_kg = recleaner_cu_kg + scavenger_cu_kg
elif config == "Recleaner sin recirculación":
    final_conc_mass = recleaner_conc_mass
    final_cu_kg = recleaner_cu_kg
else:
    final_conc_mass = recleaner_conc_mass + scavenger_conc_mass
    final_cu_kg = recleaner_cu_kg + scavenger_cu_kg

final_cu_pct = final_cu_kg / final_conc_mass / 10 if final_conc_mass else 0
recovery_global = final_cu_kg / feed_cu_kg * 100 if feed_cu_kg else 0
razon_concentracion = final_cu_kg / feed_cu_kg if feed_cu_kg else 0
relacion_enriquecimiento = final_cu_pct / feed_cu_pct if feed_cu_pct else 0

st.subheader("Resumen Metalúrgico")
tabla = pd.DataFrame({
    "Indicador": [
        "Tonelaje alimentación (t/h)", "Ley alimentación (%)",
        "Cobre total alimentado (kg/h)",
        "Conc. final (t/h)", "Cobre recuperado (kg/h)", "Ley concentrado (%)",
        "Recuperación global Cu (%)", "Razón de concentración", "Relación de enriquecimiento"
    ],
    "Valor": [
        feed_tph, feed_cu_pct, feed_cu_kg,
        final_conc_mass, final_cu_kg, final_cu_pct,
        recovery_global, razon_concentracion, relacion_enriquecimiento
    ]
})
st.dataframe(tabla.round(2))

fig1 = go.Figure(go.Indicator(mode="gauge+number", value=recovery_global,
    title={"text": "Recuperación Global Cu (%)"}))
st.plotly_chart(fig1, use_container_width=True)

fig2 = go.Figure(data=[go.Bar(x=["Feed", "Conc. Final"], y=[feed_cu_pct, final_cu_pct])])
fig2.update_layout(title="Ley de cobre: Alimentación vs Concentrado", yaxis_title="% Cu")
st.plotly_chart(fig2, use_container_width=True)

csv = tabla.to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar resumen", csv, "resumen_metalurgico.csv", "text/csv")
