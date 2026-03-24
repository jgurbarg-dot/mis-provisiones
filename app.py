import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os

st.set_page_config(page_title="Mi Despensa", layout="centered")

# --- CONEXIÓN CACHEADA (Para que no se bloquee) ---
@st.cache_resource
def iniciar_conexion():
    nombre_json = "misprovisionesfirebaseadminsdkfbsvc674f03e169.json"
    if not firebase_admin._apps:
        if os.path.exists(nombre_json):
            cred = credentials.Certificate(nombre_json)
            firebase_admin.initialize_app(cred)
        else:
            return None
    return firestore.client()

db = iniciar_conexion()

st.title("📦 GESTIÓN DE MI DESPENSA")

if db is None:
    st.error("❌ No se encontró el archivo JSON. Verifica que el nombre en GitHub sea exacto.")
else:
    # --- FORMULARIO ---
    with st.form("mi_formulario"):
        accion = st.selectbox("Acción:", ["Ingreso (Compré)", "Gasto (Consumí)"])
        nombre_prod = st.text_input("Producto:").strip().lower()
        cantidad_mov = st.number_input("Cantidad:", min_value=0.1)
        enviado = st.form_submit_button("Confirmar Movimiento")

    if enviado and nombre_prod:
        with st.spinner("Actualizando Firebase..."):
            try:
                doc_ref = db.collection("productos").document(nombre_prod)
                doc = doc_ref.get()
                
                cant_actual = doc.to_dict().get("cantidad", 0) if doc.exists else 0
                nueva_cant = cant_actual - cantidad_mov if "Gasto" in accion else cant_actual + cantidad_mov
                
                doc_ref.set({
                    "nombre": nombre_prod.capitalize(),
                    "cantidad": max(0, nueva_cant)
                }, merge=True)
                
                st.success(f"✅ Actualizado: {nombre_prod} ahora tiene {max(0, nueva_cant)}")
            except Exception as e:
                st.error(f"Error de Firebase: {e}")
