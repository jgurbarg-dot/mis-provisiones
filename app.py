import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# CONFIGURACIÓN DE CONEXIÓN
if not firebase_admin._apps:
    try:
        # PONE AQUÍ EL NOMBRE DE TU ARCHIVO NUEVO
        cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-1ce1062898.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")

db = firestore.client()

st.title("📦 GESTIÓN DE MI DESPENSA")

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
    if nombre_prod:
        try:
            doc_ref = db.collection("productos").document(nombre_prod)
            doc = doc_ref.get()
            
            # Lógica de suma/resta
            cant_actual = doc.to_dict().get("cantidad", 0) if doc.exists else 0
            nueva_cant = cant_actual - cantidad_mov if "Gasto" in accion else cant_actual + cantidad_mov
            
            # GUARDAR
            doc_ref.set({
                "nombre": nombre_prod.capitalize(),
                "cantidad": max(0, nueva_cant)
            }, merge=True)
            
            st.success(f"✅ ¡Guardado! {nombre_prod} ahora tiene {max(0, nueva_cant)}")
            st.rerun()
        except Exception as e:
            st.error(f"❌ No se pudo guardar en Firebase: {e}")

st.divider()

# TABLA DE INVENTARIO
st.header("2. Inventario Actual")
try:
    docs = db.collection("productos").get()
    datos = [{"Producto": d.to_dict().get("nombre"), "Cantidad": d.to_dict().get("cantidad")} for d in docs]
    if datos:
        st.table(pd.DataFrame(datos))
    else:
        st.write("No hay nada en la despensa.")
except:
    st.error("Error al leer la base de datos.")
