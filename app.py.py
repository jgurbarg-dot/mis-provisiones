import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# 1. CONEXIÓN (IMPORTANTE: Verifica el nombre del archivo JSON en tu GitHub)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-29b42419c3.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error de conexión: {e}")

db = firestore.client()

st.set_page_config(page_title="Mi Despensa", layout="wide")
st.title("📦 GESTIÓN DE MI DESPENSA")

# --- SECCIÓN 1: REGISTRO ---
st.header("1. Registrar o Actualizar Producto")
col1, col2, col3 = st.columns(3)

with col1:
    accion = st.selectbox("Acción:", ["Ingreso (Compré)", "Gasto (Consumí)"])
with col2:
    nombre_prod = st.text_input("Nombre del producto:").strip().lower()
with col3:
    cantidad_mov = st.number_input("Cantidad:", min_value=0.0, step=1.0)

if st.button("Confirmar Movimiento", use_container_width=True):
    if nombre_prod:
        # Referencia directa a la colección 'productos' (según tu imagen image_d48462.png)
        doc_ref = db.collection("productos").document(nombre_prod)
        doc = doc_ref.get()
        
        cant_actual = doc.to_dict().get("cantidad", 0) if doc.exists else 0
        
        if "Gasto" in accion:
            nueva_cant = max(0, cant_actual - cantidad_mov)
        else:
            nueva_cant = cant_actual + cantidad_mov
            
        # ESCRITURA FORZADA
        doc_ref.set({
            "nombre": nombre_prod.capitalize(),
            "cantidad": nueva_cant,
            "ultima_actualizacion": datetime.now()
        }, merge=True)
        
        st.cache_data.clear() # ELIMINA LA CACHÉ PARA FORZAR LECTURA NUEVA
        st.success(f"✅ ¡Firebase actualizado! {nombre_prod.capitalize()} ahora tiene {nueva_cant}")
        st.rerun() 
    else:
        st.error("⚠️ Por favor ingresa un nombre.")

st.divider()

# --- SECCIÓN 2: LECTURA SIN CACHÉ ---
st.header("2. Inventario Total (Desde la Nube)")

# Forzamos la consulta a la colección 'productos'
try:
    productos_docs = db.collection("productos").get()
    datos_tabla = []

    for p in productos_docs:
        info = p.to_dict()
        datos_tabla.append({
            "Producto": info.get("nombre", p.id.capitalize()),
            "Stock Actual": info.get("cantidad", 0),
            "ID Documento": p.id
        })

    if datos_tabla:
        df = pd.DataFrame(datos_tabla)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ No se encontraron datos. Verifica que la colección se llame exactamente 'productos' en Firebase.")
except Exception as e:
    st.error(f"Error al leer la base de datos: {e}")
