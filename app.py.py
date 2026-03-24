import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# 1. CONEXIÓN SEGURA A FIREBASE
if not firebase_admin._apps:
    # Asegúrate de que este nombre de archivo sea EXACTO al que subiste a tu repo
    cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-29b42419c3.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Mi Despensa", layout="wide")
st.title("📦 GESTIÓN INTEGRAL DE PROVISIONES")

# --- SECCIÓN 1: REGISTRO DE MOVIMIENTOS ---
st.header("1. Registrar Movimiento")
col1, col2, col3 = st.columns(3)

with col1:
    accion = st.selectbox("Acción:", ["Ingreso (Compré)", "Gasto (Consumí)"])
with col2:
    # Usamos minúsculas para que coincida con tus IDs de Firebase (azucar, sal, pan)
    nombre_input = st.text_input("Producto:").strip().lower()
with col3:
    cantidad_op = st.number_input("Cantidad:", min_value=0.0, step=1.0)

if st.button("Confirmar Movimiento", use_container_width=True):
    if nombre_input:
        # Referencia exacta al documento en la colección 'productos'
        doc_ref = db.collection("productos").document(nombre_input)
        doc = doc_ref.get()
        
        # Obtenemos la cantidad que YA existe en Firebase
        if doc.exists:
            datos_actuales = doc.to_dict()
            cant_en_fire = datos_actuales.get("cantidad", 0)
        else:
            cant_en_fire = 0
        
        # Cálculo del nuevo total
        if "Gasto" in accion:
            nueva_cant = cant_en_fire - cantidad_op
            if nueva_cant < 0: nueva_cant = 0
            tipo_log = "SALIDA"
        else:
            nueva_cant = cant_en_fire + cantidad_op
            tipo_log = "ENTRADA"
            
        # ACTUALIZACIÓN REAL EN FIREBASE
        # Usamos set con merge=True para no borrar campos como 'unidad'
        doc_ref.set({
            "nombre": nombre_input.capitalize(),
            "cantidad": nueva_cant,
            "ultima_actualizacion": datetime.now()
        }, merge=True)
        
        # Guardar en el Historial
        db.collection("historial").add({
            "producto": nombre_input.capitalize(),
            "tipo": tipo_log,
            "cantidad": cantidad_op,
            "fecha": datetime.now()
        })
        
        st.success(f"✅ ¡Firebase actualizado! {nombre_input} ahora tiene {nueva_cant}")
        # FORZAR RECARGA DE LA APP PARA ACTUALIZAR TABLAS
        st.rerun()
    else:
        st.error("Escribe el nombre del producto.")

st.divider()

# --- SECCIÓN 2: VISUALIZACIÓN DE TODA LA DESPENSA ---
st.header("2. Mi Despensa Completa")

# Traemos todos los documentos de la colección 'productos'
productos_fire = db.collection("productos").stream()
lista_completa = []

for p in productos_fire:
    datos = p.to_dict()
    lista_completa.append({
        "Producto": p.id.capitalize(), # Usa el ID del documento (azucar, sal...)
        "Stock Disponible": datos.get("cantidad", 0),
        "Unidad": datos.get("unidad", "unidades")
    })

if lista_completa:
    # Creamos un DataFrame para mostrar todo como una tabla limpia
    df_despensa = pd.DataFrame(lista_completa)
    st.dataframe(df_despensa, use_container_width=True, hide_index=True)
else:
    st.warning("No se encontraron productos en la colección 'productos' de Firebase.")
