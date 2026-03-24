import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import os

st.write("Archivos en el entorno:", os.listdir())

st.title("📦 GESTIÓN DE MI DESPENSA")

def conectar_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate("misprovisionesfirebaseadminsdkfbsvc674f03e169.json")
            firebase_admin.initialize_app(cred)
            st.success("✅ Firebase conectado")
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

    if db is not None and nombre_prod != "":
        with st.spinner('Comunicando con Firebase...'):
            try:
                doc_ref = db.collection("productos").document(nombre_prod)
                doc = doc_ref.get()

                if doc.exists:
                    cant_actual = doc.to_dict().get("cantidad", 0)
                else:
                    cant_actual = 0

                if "Gasto" in accion:
                    nueva_cant = cant_actual - cantidad_mov
                else:
                    nueva_cant = cant_actual + cantidad_mov

                doc_ref.set({
                    "nombre": nombre_prod.capitalize(),
                    "cantidad": max(0, nueva_cant)
                }, merge=True)

                st.success(f"✅ Guardado: {nombre_prod} → {max(0, nueva_cant)}")

            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")
