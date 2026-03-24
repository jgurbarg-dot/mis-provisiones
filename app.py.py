import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# 1. Configuración de conexión con Firebase
if not firebase_admin._apps:
    # Asegúrate de que este nombre de archivo sea exacto al que subiste a GitHub
    cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-29b42419c3.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Configuración de la página
st.set_page_config(page_title="Control de Provisiones", layout="wide")
st.title("📦 GESTIÓN INTEGRAL DE PROVISIONES")

# --- SECCIÓN 1: REGISTRO ---
st.header("1. Registrar Movimiento")
col1, col2, col3 = st.columns(3)

with col1:
    accion = st.selectbox("Acción:", ["Ingreso (Compré)", "Gasto (Consumí)"])
with col2:
    nombre_input = st.text_input("Producto:").strip().capitalize()
with col3:
    cantidad_op = st.number_input("Cantidad:", min_value=0.0, step=1.0)

if st.button("Confirmar Movimiento", use_container_width=True):
    if nombre_input:
        # Referencia al documento en minúsculas para evitar duplicados como "Sal" y "sal"
        doc_ref = db.collection("productos").document(nombre_input.lower())
        doc = doc_ref.get()
        
        # Obtener cantidad actual (si el producto ya existe)
        datos_previos = doc.to_dict() if doc.exists else {}
        cant_previa = datos_previos.get("cantidad", 0)
        
        # Calcular nuevo total
        if "Gasto" in accion:
            nueva_cant = cant_previa - cantidad_op
            if nueva_cant < 0: nueva_cant = 0
            tipo_log = "SALIDA"
        else:
            nueva_cant = cant_previa + cantidad_op
            tipo_log = "ENTRADA"
            
        # Actualizar stock en la colección 'productos'
        doc_ref.set({
            "nombre": nombre_input,
            "cantidad": nueva_cant,
            "ultima_actualizacion": datetime.now()
        }, merge=True)
        
        # Registrar en el historial
        db.collection("historial").add({
            "producto": nombre_input,
            "tipo": tipo_log,
            "cantidad": cantidad_op,
            "fecha": datetime.now()
        })
        
        st.success(f"✅ Movimiento registrado. {nombre_input} ahora tiene {nueva_cant} unidades.")
        st.rerun() # Refresca la app para mostrar los datos nuevos abajo
    else:
        st.error("⚠️ Por favor, escribe el nombre de un producto.")

st.divider()

# --- SECCIÓN 2: INVENTARIO COMPLETO ---
st.header("2. Inventario Disponible (Toda la Despensa)")

productos_stream = db.collection("productos").stream()
lista_inventario = []

for p in productos_stream:
    d = p.to_dict()
    lista_inventario.append({
        "Producto": d.get("nombre", p.id.capitalize()),
        "Cantidad Actual": d.get("cantidad", 0)
    })

if lista_inventario:
    df_inv = pd.DataFrame(lista_inventario)
    st.dataframe(df_inv, use_container_width=True, hide_index=True)
else:
    st.info("No hay productos registrados aún.")

st.divider()

# --- SECCIÓN 3: HISTORIAL RECIENTE ---
st.header("3. Historial de Movimientos")

historial_stream = db.collection("historial").order_by("fecha", direction=firestore.Query.DESCENDING).limit(10).stream()
lista_h = []

for h in historial_stream:
    d = h.to_dict()
    lista_h.append({
        "Fecha": d["fecha"].strftime("%d/%m/%Y %H:%M"),
        "Producto": d["producto"],
        "Tipo": d["tipo"],
        "Cant.": d["cantidad"]
    })

if lista_h:
    st.table(pd.DataFrame(lista_h))
