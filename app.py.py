import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# 1. CONEXIÓN (Solo se inicializa una vez)
if not firebase_admin._apps:
    cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-29b42419c3.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Mi Despensa", layout="wide")
st.title("📦 GESTIÓN DE MI DESPENSA")

# --- SECCIÓN 1: REGISTRO DE PRODUCTOS ---
st.header("1. Registrar o Actualizar Producto")
col1, col2, col3 = st.columns(3)

with col1:
    accion = st.selectbox("Acción:", ["Ingreso (Compré)", "Gasto (Consumí)"])
with col2:
    nombre_prod = st.text_input("Nombre del producto:").strip().lower() # Siempre minúsculas para coincidir con Firebase
with col3:
    cantidad_mov = st.number_input("Cantidad:", min_value=0.0, step=1.0)

if st.button("Confirmar Movimiento", use_container_width=True):
    if nombre_prod:
        # Buscamos el documento exacto en Firebase (ej: 'sal')
        doc_ref = db.collection("productos").document(nombre_prod)
        doc = doc_ref.get()
        
        # Leemos la cantidad actual desde Firebase
        cant_actual = doc.to_dict().get("cantidad", 0) if doc.exists else 0
        
        # Calculamos el nuevo total
        if "Gasto" in accion:
            nueva_cant = cant_actual - cantidad_mov
            if nueva_cant < 0: nueva_cant = 0
        else:
            nueva_cant = cant_actual + cantidad_mov
            
        # ESCRIBIR EN FIREBASE
        doc_ref.set({
            "nombre": nombre_prod.capitalize(),
            "cantidad": nueva_cant,
            "ultima_actualizacion": datetime.now()
        }, merge=True)
        
        # RECARGA FORZADA: Esto es lo que faltaba para que veas el cambio
        st.success(f"✅ ¡Firebase actualizado! {nombre_prod.capitalize()} ahora tiene {nueva_cant}")
        st.rerun() 
    else:
        st.error("⚠️ Por favor ingresa un nombre.")

st.divider()

# --- SECCIÓN 2: LECTURA REAL DE TODA LA DESPENSA ---
st.header("2. Inventario Total (Desde la Nube)")

# Forzamos a Streamlit a pedirle a Firebase todos los documentos cada vez que carga
productos_stream = db.collection("productos").get() # .get() es más seguro que .stream() para tablas estáticas
datos_tabla = []

for p in productos_stream:
    info = p.to_dict()
    datos_tabla.append({
        "Producto": info.get("nombre", p.id.capitalize()),
        "Stock Actual": info.get("cantidad", 0),
        "ID en Firebase": p.id
    })

if datos_tabla:
    df = pd.DataFrame(datos_tabla)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No hay productos detectados en la colección 'productos' de Firebase.")
