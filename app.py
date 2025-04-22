
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Simulación Flotación Cu", layout="wide")

st.title("Simulación de Flotación con Split Factors y Validación de Muestreo")

flowsheet_config = st.selectbox("Selecciona configuración de circuito", [
    "Configuración estándar (R → C → RC)",
    "Recleaner sin recirculación", 
    "Scavenger directo a producto final"
])

st.subheader("Diagrama de Flujo del Circuito")

if flowsheet_config == "Configuración estándar (R → C → RC)":
    dot_code = """
    digraph G {
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
    }
"""
elif flowsheet_config == "Recleaner sin recirculación":
    dot_code = """
    digraph G {
        rankdir=LR;
        Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> "Relave Final";
        Recleaner -> "Relave Final" [label="Cola RC"];
    }
"""
else:
    dot_code = """
    digraph G {
        rankdir=LR;
        Feed -> Rougher;
        Rougher -> Cleaner [label="Conc. R"];
        Rougher -> Scavenger [label="Cola R"];
        Cleaner -> Recleaner [label="Conc. C"];
        Recleaner -> "Concentrado Final";
        Scavenger -> "Concentrado Final" [label="Conc. S"];
        Recleaner -> Cleaner [style=dashed, label="Cola RC → C"];
    }
"""

st.graphviz_chart(dot_code)

# El resto del código se asume igual que el último generado previamente...
# Para efectos de este ejemplo, lo mantendremos breve.
st.markdown("**[...código de simulación y tablas aquí...]**")
