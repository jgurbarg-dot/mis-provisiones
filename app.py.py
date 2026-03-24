import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# 1. Conexión con Firebase
if not firebase_admin._apps:
    # Asegúrate de que este archivo JSON esté en tu repositorio de GitHub
    cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-29b42419c3.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.set_page_config(page_title="Control de Provisiones", layout="wide")
st.title("📦 GESTIÓN INTEGRAL DE PROVISIONES")

# --- SECCIÓN 1: ENTRADA DE DATOS ---
st.header("1. Registrar Movimiento")
col1, col2, col3 = st.columns(3)

with col1:
    accion = st.selectbox("Acción:", ["Ingreso (Compré)", "Gasto (Consumí)"])
with col2:
    # Usamos un valor vacío por defecto para evitar registros accidentales
    nombre = st.text_input("Producto (ej: Arroz, Leche):").strip().capitalize()
with col3:
    cantidad_op = st.number_input("Cantidad:", min_value=0.0, step=1.0)

if st.button("Confirmar Movimiento", use_container_width=True):
    if nombre:
        doc_ref = db.collection("productos").document(nombre.lower())
        doc = doc_ref.get()
        
        cant_previa = doc.to_dict().get("cantidad", 0) if doc.exists else 0
        
        if "Gasto" in accion:
            nueva_cant = cant_previa - cantidad_op
            if nueva_cant < 0: nueva_cant = 0
            tipo_log = "SALIDA"
        else:
            nueva_cant = cant_previa + cantidad_op
            tipo_log = "ENTRADA"
            
        # Actualizamos Firestore
        doc_ref.set({"cantidad": nueva_cant, "ultima_actualizacion": datetime.now()})
        
        # Guardamos en el historial
        db.collection("historial").add({
            "producto": nombre,
            "tipo": tipo_log,
            "cantidad": cantidad_op,
            "fecha": datetime.now()
        })
        
        st.success(f"✅ ¡Actualizado! {nombre}: {nueva_cant} unidades.")
        # ESTA LÍNEA ES CLAVE: Recarga la app para que la tabla de abajo se actualice sola
        st.rerun() 
    else:
        st.error("⚠️ Por favor, escribe el nombre de un producto.")

st.divider()

# --- SECCIÓN 2: INVENTARIO TOTAL (Toda tu despensa) ---
st.header("2. Inventario Actual (Lo que hay en la despensa)")

# Consultamos todos los productos
productos_ref = db.collection("productos").stream()
inventario_lista = []

for p in productos_ref:
    datos = p.to_dict()
    inventario_lista.append({
        "Producto": p.id.capitalize(),
        "Cantidad Disponible": datos.get("cantidad", 0),
        "Última vez": datos.get("ultima_actualizacion").strftime("%d/%m %H:%M") if datos.get("ultima_actualizacion") else "N/A"
    })

if inventario_lista:
    df_stock = pd.DataFrame(inventario_lista)
    # Mostramos una tabla interactiva que usa todo el ancho
    st.dataframe(df_stock, use_container_width=True, hide_index=True)
else:
    st.info("La despensa está vacía. Registra tu primer producto arriba.")

st.divider()

# --- SECCIÓN 3: HISTORIAL RECIENTE ---
st.header("3. Historial de Movimientos (Últimos 10)")

historial = db.collection("historial").order_by("fecha", direction=firestore.Query.DESCENDING).limit(10).stream()
lista_hist = []

for h in historial:
    d = h.to_dict()
    lista_hist.append({
        "Fecha": d["fecha"].strftime("%d/%m/%Y %H:%M"),
        "Producto": d["producto"],
        "Movimiento": d["tipo"],
        "Cantidad": d["cantidad"]
    })

if lista_hist:
    st.table(pd.DataFrame(lista_hist))
