# Simulación de Circuito de Flotación de Cobre - Streamlit App

Esta aplicación interactiva permite simular un circuito clásico de flotación de cobre (Rougher → Cleaner → Recleaner), incluyendo opciones de configuración, recirculaciones y cálculo de recuperación global. Desarrollada en Python usando Streamlit.

## 🚀 Características principales
- Ajuste dinámico de parámetros de split y recuperación por etapa
- Visualización interactiva del flowsheet mediante Graphviz
- Cálculo automático de flujos de masa, leyes de Cu y recuperación global
- Comparación con datos de muestreo reales (opcional)
- Exportación de resultados a CSV

## 🧰 Requisitos
- Python 3.8 o superior
- `streamlit`
- `pandas`
- `graphviz`
- `plotly`

Instalación de dependencias:
```bash
pip install streamlit pandas graphviz plotly
```

## 📂 Estructura esperada
```
.
├── app.py
├── requirements.txt
├── flowsheet_flotacion.dot (opcional si se quiere usar como referencia)
├── nodos_flotacion.csv (estructura de nodos - opcional)
├── enlaces_flotacion.csv (estructura de enlaces - opcional)
```

## ▶️ Cómo ejecutar localmente
```bash
streamlit run app.py
```

## 🌐 Despliegue en Streamlit Cloud
1. Sube tu repositorio a GitHub.
2. Accede a [Streamlit Cloud](https://streamlit.io/cloud).
3. Conecta tu cuenta de GitHub.
4. Selecciona tu repositorio y el archivo `app.py` como principal.

## 📸 Capturas de pantalla
Puedes agregar aquí imágenes del diagrama dinámico y de los resultados tabulares si deseas.

## 🧪 Prueba y mejora
Si deseas extender esta app:
- Agrega más etapas (e.g. Recleaner 2, columnas)
- Integra modelos cinéticos o split dinámicos
- Conecta con datos reales desde Excel o una base de datos

## 📄 Licencia
MIT License

---

Desarrollado por [Tu Nombre] como modelo de simulación y análisis metalúrgico para plantas concentradoras.