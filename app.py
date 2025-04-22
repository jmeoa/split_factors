
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Simulación de Flotación Cu", layout="wide")
st.title("Simulación de Flotación de Cobre - Split Factors y Métricas")

# 1. Selección de configuración del circuito
config = st.selectbox("Configuración del circuito", [
    "Configuración estándar (R → C → RC)",
    "Recleaner sin recirculación",
    "Scavenger directo a producto final"
])

# 2. Diagrama dinámico
st.subheader("Diagrama del circuito")
if config == "Configuración estándar (R → C → RC)":
    dot = '''digraph G {
        rankdir=LR; Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> Rougher [style=dashed];
        Scavenger -> "Relave Final";
        Recleaner -> Cleaner [style=dashed];
        Recleaner -> Rougher [style=dashed];
    }'''
elif config == "Recleaner sin recirculación":
    dot = '''digraph G {
        rankdir=LR; Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> "Relave Final";
        Recleaner -> "Relave Final";
    }'''
else:
    dot = '''digraph G {
        rankdir=LR; Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> "Concentrado Final";
    }'''
st.graphviz_chart(dot)

# 3. Parámetros ajustables
st.subheader("Parámetros del proceso")
col1, col2 = st.columns(2)
with col1:
    feed_tph = st.number_input("Alimentación (t/h)", value=100.0)
    feed_cu = st.number_input("Ley Cu alimentación (%)", value=1.0)
with col2:
    rougher_mass, rougher_rec = st.slider("Rougher (Masa, Rec)", 0.0, 1.0, (0.25, 0.9))
    scavenger_mass, scavenger_rec = st.slider("Scavenger (Masa, Rec)", 0.0, 1.0, (0.5, 0.6))
    cleaner_mass, cleaner_rec = st.slider("Cleaner (Masa, Rec)", 0.0, 1.0, (0.9, 0.98))
    recleaner_mass, recleaner_rec = st.slider("Recleaner (Masa, Rec)", 0.0, 1.0, (0.95, 0.99))

# 4. Cálculos
feed_cu_kg = feed_tph * feed_cu / 100 * 1000

rougher_conc_mass = feed_tph * rougher_mass
rougher_cu_kg = feed_cu_kg * rougher_rec

scavenger_conc_mass = (feed_tph - rougher_conc_mass) * scavenger_mass
scavenger_cu_kg = (feed_cu_kg - rougher_cu_kg) * scavenger_rec

cleaner_conc_mass = rougher_conc_mass * cleaner_mass
cleaner_cu_kg = rougher_cu_kg * cleaner_rec

recleaner_conc_mass = cleaner_conc_mass * recleaner_mass
recleaner_cu_kg = cleaner_cu_kg * recleaner_rec

# 5. Resultado final según configuración
if config == "Configuración estándar (R → C → RC)":
    final_mass = recleaner_conc_mass + scavenger_conc_mass
    final_cu_kg = recleaner_cu_kg + scavenger_cu_kg
elif config == "Recleaner sin recirculación":
    final_mass = recleaner_conc_mass
    final_cu_kg = recleaner_cu_kg
else:
    final_mass = recleaner_conc_mass + scavenger_conc_mass
    final_cu_kg = recleaner_cu_kg + scavenger_cu_kg

final_cu_pct = final_cu_kg / final_mass / 10 if final_mass else 0
recuperacion_global = final_cu_kg / feed_cu_kg * 100 if feed_cu_kg else 0
razon_conc = final_cu_kg / feed_cu_kg if feed_cu_kg else 0
enriquecimiento = final_cu_pct / feed_cu if feed_cu else 0

# 6. Tabla de resultados
st.subheader("Resumen de resultados")
df = pd.DataFrame({
    "Indicador": [
        "Alimentación (t/h)", "Ley Cu alimentación (%)", "Cu alimentado (kg/h)",
        "Conc. final (t/h)", "Cu recuperado (kg/h)", "Ley Cu concentrado (%)",
        "Recuperación global Cu (%)", "Razón de concentración", "Relación enriquecimiento"
    ],
    "Valor": [
        feed_tph, feed_cu, feed_cu_kg,
        final_mass, final_cu_kg, final_cu_pct,
        recuperacion_global, razon_conc, enriquecimiento
    ]
})
st.dataframe(df.round(2))

# 7. Gráficos
st.subheader("Gráficos")
fig = go.Figure()
fig.add_trace(go.Indicator(mode="number+gauge", value=recuperacion_global,
    title={"text": "Recuperación Global Cu (%)"}, gauge={"axis": {"range": [0, 100]}}))
st.plotly_chart(fig, use_container_width=True)

fig2 = go.Figure(data=[go.Bar(x=["Alimentación", "Concentrado"], y=[feed_cu, final_cu_pct])])
fig2.update_layout(title="Ley de cobre - Alimentación vs Concentrado", yaxis_title="Ley Cu (%)")
st.plotly_chart(fig2, use_container_width=True)

# 8. Exportación
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar resumen", csv, "resumen_flotacion.csv", "text/csv")
