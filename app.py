import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

st.title("📦 GESTIÓN DE MI DESPENSA")

# Función para conectar (solo si no está conectada)
def conectar_firebase():
    if not firebase_admin._apps:
        try:
            # VERIFICA QUE ESTE NOMBRE SEA EXACTO AL DE GITHUB
            cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-1ce1062898.json")
            firebase_admin.initialize_app(cred)
            return firestore.client()
        except Exception as e:
            st.error(f"❌ Error crítico de conexión: {e}")
            return None
    return firestore.client()

# REGISTRO
st.header("1. Registrar Ingreso o Gasto")
col1, col2, col3 = st.columns(3)
with col1:
    accion = st.selectbox("Acción:", ["Ingreso (Compré)", "Gasto (Consumí)"])
with col2:
    nombre_prod = st.text_input("Producto:").strip().lower()
with col3:
    cantidad_mov = st.number_input("Cantidad:", min_value=1.0)

if st.button("Confirmar Movimiento"):
    db = conectar_firebase()
    if db and nombre_prod:
        with st.spinner('Comunicando con Firebase...'):
            try:
                doc_ref = db.collection("productos").document(nombre_prod)
                doc = doc_ref.get()
                
                cant_actual = doc.to_dict().get("cantidad", 0) if doc.exists else 0
                nueva_cant = cant_actual - cantidad_mov if "Gasto" in accion else cant_actual + cantidad_mov
                
                doc_ref.set({
                    "nombre": nombre_prod.capitalize(),
                    "cantidad": max(0, nueva_cant)
                }, merge=True)
                
                st.success(f"✅ ¡Guardado! {nombre_prod} tiene {max(0, nueva_cant)}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")

st.divider()

# TABLA DE INVENTARIO
st.header("2. Inventario Actual")
db_lectura = conectar_firebase()
if db_lectura:
    try:
        docs = db_lectura.collection("productos").get()
        datos = [{"Producto": d.to_dict().get("nombre"), "Cantidad": d.to_dict().get("cantidad")} for d in docs]
        if datos:
            st.table(pd.DataFrame(datos))
        else:
            st.info("La despensa está vacía en Firebase.")
    except Exception as e:
        st.error(f"Error al leer: {e}")
