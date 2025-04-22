
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Simulación Flotación Cu", layout="wide")

st.title("Simulación de Flotación de Cobre - Split Factors")

config = st.selectbox("Selecciona configuración del circuito", [
    "Configuración estándar (R → C → RC)",
    "Recleaner sin recirculación",
    "Scavenger directo a producto final"
])

st.subheader("Diagrama de Flujo del Circuito")
if config == "Configuración estándar (R → C → RC)":
    dot_code = '''digraph G {
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
    }'''
elif config == "Recleaner sin recirculación":
    dot_code = '''digraph G {
        rankdir=LR;
        Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> "Relave Final";
        Recleaner -> "Relave Final" [label="Cola RC"];
    }'''
else:
    dot_code = '''digraph G {
        rankdir=LR;
        Feed -> Rougher;
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
    st.markdown("**Split Factors por etapa**")
    rougher_mass, rougher_rec = st.slider("Rougher (Masa, Recuperación)", 0.0, 1.0, (0.25, 0.90))
    scavenger_mass, scavenger_rec = st.slider("Scavenger (Masa, Recuperación)", 0.0, 1.0, (0.5, 0.6))
    cleaner_mass, cleaner_rec = st.slider("Cleaner (Masa, Recuperación)", 0.0, 1.0, (0.9, 0.98))
    recleaner_mass, recleaner_rec = st.slider("Recleaner (Masa, Recuperación)", 0.0, 1.0, (0.95, 0.99))

# Cálculos
feed_cu_kg = feed_tph * feed_cu_pct / 100 * 1000
rougher_conc_mass = feed_tph * rougher_mass
rougher_cu_kg = feed_cu_kg * rougher_rec
rougher_conc_cu = rougher_cu_kg / rougher_conc_mass / 10 if rougher_conc_mass > 0 else 0

rougher_tail_mass = feed_tph - rougher_conc_mass
rougher_tail_cu_kg = feed_cu_kg - rougher_cu_kg
rougher_tail_cu = rougher_tail_cu_kg / rougher_tail_mass / 10 if rougher_tail_mass > 0 else 0

scavenger_conc_mass = rougher_tail_mass * scavenger_mass
scavenger_cu_kg = rougher_tail_cu_kg * scavenger_rec
scavenger_conc_cu = scavenger_cu_kg / scavenger_conc_mass / 10 if scavenger_conc_mass > 0 else 0

scavenger_tail_mass = rougher_tail_mass - scavenger_conc_mass
scavenger_tail_cu_kg = rougher_tail_cu_kg - scavenger_cu_kg
scavenger_tail_cu = scavenger_tail_cu_kg / scavenger_tail_mass / 10 if scavenger_tail_mass > 0 else 0

cleaner_conc_mass = rougher_conc_mass * cleaner_mass
cleaner_cu_kg = rougher_cu_kg * cleaner_rec
cleaner_conc_cu = cleaner_cu_kg / cleaner_conc_mass / 10 if cleaner_conc_mass > 0 else 0

cleaner_tail_mass = rougher_conc_mass - cleaner_conc_mass
cleaner_tail_cu_kg = rougher_cu_kg - cleaner_cu_kg
cleaner_tail_cu = cleaner_tail_cu_kg / cleaner_tail_mass / 10 if cleaner_tail_mass > 0 else 0

recleaner_conc_mass = cleaner_conc_mass * recleaner_mass
recleaner_cu_kg = cleaner_cu_kg * recleaner_rec
recleaner_conc_cu = recleaner_cu_kg / recleaner_conc_mass / 10 if recleaner_conc_mass > 0 else 0

recleaner_tail_mass = cleaner_conc_mass - recleaner_conc_mass
recleaner_tail_cu_kg = cleaner_cu_kg - recleaner_cu_kg
recleaner_tail_cu = recleaner_tail_cu_kg / recleaner_tail_mass / 10 if recleaner_tail_mass > 0 else 0

# Producto final depende de configuración
if config == "Configuración estándar (R → C → RC)":
    final_conc_mass = recleaner_conc_mass + scavenger_conc_mass
    final_cu_kg = recleaner_cu_kg + scavenger_cu_kg
elif config == "Recleaner sin recirculación":
    final_conc_mass = recleaner_conc_mass
    final_cu_kg = recleaner_cu_kg
else:
    final_conc_mass = recleaner_conc_mass + scavenger_conc_mass
    final_cu_kg = recleaner_cu_kg + scavenger_cu_kg

recovery_global = (final_cu_kg / feed_cu_kg * 100) if feed_cu_kg > 0 else 0

# Tabla
df = pd.DataFrame({
    "Flujo": ["Rougher Conc", "Rougher Colas", "Scavenger Conc", "Scavenger Colas",
              "Cleaner Conc", "Cleaner Colas", "Recleaner Conc", "Recleaner Colas", "Producto Final"],
    "Toneladas (t/h)": [
        rougher_conc_mass, rougher_tail_mass, scavenger_conc_mass, scavenger_tail_mass,
        cleaner_conc_mass, cleaner_tail_mass, recleaner_conc_mass, recleaner_tail_mass, final_conc_mass
    ],
    "Ley Cu (%)": [
        rougher_conc_cu, rougher_tail_cu, scavenger_conc_cu, scavenger_tail_cu,
        cleaner_conc_cu, cleaner_tail_cu, recleaner_conc_cu, recleaner_tail_cu,
        final_cu_kg / final_conc_mass / 10 if final_conc_mass > 0 else 0
    ]
})

st.subheader("Tabla de Flujos del Proceso")
st.dataframe(df.round(2))
st.markdown(f"**Recuperación Global de Cobre: {recovery_global:.2f}%**")

# Graficos
st.subheader("Gráficos de Respuestas Metalúrgicas")

fig1 = go.Figure(go.Bar(x=df["Flujo"], y=df["Toneladas (t/h)"], name="Tonelaje"))
fig1.update_layout(title="Tonelaje por Flujo", xaxis_title="Flujo", yaxis_title="t/h")
st.plotly_chart(fig1, use_container_width=True)

fig2 = go.Figure(go.Bar(x=df["Flujo"], y=df["Ley Cu (%)"], name="Ley Cu", marker_color="orange"))
fig2.update_layout(title="Ley de Cobre por Flujo", xaxis_title="Flujo", yaxis_title="% Cu")
st.plotly_chart(fig2, use_container_width=True)

# Export
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar tabla como CSV", csv, "tabla_flotacion.csv", "text/csv")
