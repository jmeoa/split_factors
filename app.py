
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulación Flotación Cu", layout="wide")

st.title("Simulación de Flotación de Cobre - Split Factors")

# --- CONFIGURACIÓN DEL CIRCUITO ---
config = st.selectbox("Selecciona configuración del circuito", [
    "Configuración estándar (R → C → RC)",
    "Recleaner sin recirculación",
    "Scavenger directo a producto final"
])

# --- DIAGRAMA DINÁMICO ---
st.subheader("Diagrama de Flujo del Circuito")
if config == "Configuración estándar (R → C → RC)":
    dot_code = """digraph G {
        rankdir=LR;
        Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> Rougher [style=dashed, label="Conc. S → R"];
        Scavenger -> "Relave Final";
        Recleaner -> Cleaner [style=dashed, label="Cola RC → C"];
        Recleaner -> Rougher [style=dashed, label="Cola RC → R"];
    }"""
elif config == "Recleaner sin recirculación":
    dot_code = """digraph G {
        rankdir=LR;
        Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> "Relave Final";
        Recleaner -> "Relave Final" [label="Cola RC"];
    }"""
else:
    dot_code = """digraph G {
        rankdir=LR;
        Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> "Concentrado Final" [label="Conc. S"];
        Recleaner -> Cleaner [style=dashed, label="Cola RC → C"];
    }"""

st.graphviz_chart(dot_code)

# --- PARÁMETROS DE ENTRADA ---
st.subheader("Parámetros de Alimentación y Split Factors")
col1, col2 = st.columns(2)

with col1:
    feed_tph = st.number_input("Tonelaje alimentación (t/h)", value=100.0)
    feed_cu_pct = st.number_input("Ley de cobre alimentación (%)", value=1.2)

with col2:
    st.markdown("**Split Factors por etapa**")
    rougher_mass, rougher_rec = st.slider("Rougher (Masa, Recuperación)", 0.0, 1.0, (0.25, 0.90))
    scavenger_mass, scavenger_rec = st.slider("Scavenger (Masa, Recuperación)", 0.0, 1.0, (0.5, 0.6))
    cleaner_mass, cleaner_rec = st.slider("Cleaner (Masa, Recuperación)", 0.0, 1.0, (0.9, 0.98))
    recleaner_mass, recleaner_rec = st.slider("Recleaner (Masa, Recuperación)", 0.0, 1.0, (0.95, 0.99))

# --- CÁLCULOS ---
feed_cu_kg = feed_tph * feed_cu_pct / 100 * 1000
rougher_conc_mass = feed_tph * rougher_mass
rougher_cu_kg = feed_cu_kg * rougher_rec
rougher_conc_cu = rougher_cu_kg / rougher_conc_mass / 10 if rougher_conc_mass > 0 else 0

scavenger_feed_mass = feed_tph - rougher_conc_mass
scavenger_feed_cu = feed_cu_kg - rougher_cu_kg
scavenger_conc_mass = scavenger_feed_mass * scavenger_mass
scavenger_cu_kg = scavenger_feed_cu * scavenger_rec
scavenger_conc_cu = scavenger_cu_kg / scavenger_conc_mass / 10 if scavenger_conc_mass > 0 else 0

cleaner_feed_mass = rougher_conc_mass
cleaner_conc_mass = cleaner_feed_mass * cleaner_mass
cleaner_cu_kg = rougher_cu_kg * cleaner_rec
cleaner_conc_cu = cleaner_cu_kg / cleaner_conc_mass / 10 if cleaner_conc_mass > 0 else 0

recleaner_feed_mass = cleaner_conc_mass
recleaner_conc_mass = recleaner_feed_mass * recleaner_mass
recleaner_cu_kg = cleaner_cu_kg * recleaner_rec
recleaner_conc_cu = recleaner_cu_kg / recleaner_conc_mass / 10 if recleaner_conc_mass > 0 else 0

# --- FLUJO FINAL DEPENDIENDO DE CONFIGURACIÓN ---
if config == "Configuración estándar (R → C → RC)":
    total_conc_mass = recleaner_conc_mass + scavenger_conc_mass
    total_cu_kg = recleaner_cu_kg + scavenger_cu_kg
elif config == "Recleaner sin recirculación":
    total_conc_mass = recleaner_conc_mass
    total_cu_kg = recleaner_cu_kg
else:
    total_conc_mass = recleaner_conc_mass + scavenger_conc_mass
    total_cu_kg = recleaner_cu_kg + scavenger_cu_kg

recovery_global = (total_cu_kg / feed_cu_kg * 100) if feed_cu_kg > 0 else 0

# --- TABLA DE RESULTADOS ---
st.subheader("Resultados del Balance")
resumen = pd.DataFrame({
    "Flujo": [
        "Conc. Rougher", "Conc. Scavenger", "Conc. Cleaner", "Conc. Recleaner", "Conc. Total"
    ],
    "Toneladas (t/h)": [
        rougher_conc_mass, scavenger_conc_mass, cleaner_conc_mass,
        recleaner_conc_mass, total_conc_mass
    ],
    "Ley Cu (%)": [
        rougher_conc_cu, scavenger_conc_cu, cleaner_conc_cu, recleaner_conc_cu,
        total_cu_kg / total_conc_mass / 10 if total_conc_mass > 0 else 0
    ]
})

st.dataframe(resumen.round(2))
st.markdown(f"**Recuperación global Cu: {recovery_global:.2f}%**")

# Exportar tabla
csv = resumen.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar resultados CSV", csv, "resultados_flotacion.csv", "text/csv")
