import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# 1. CONEXIÓN A LA BASE DE DATOS
if not firebase_admin._apps:
    # REEMPLAZA EL NOMBRE ABAJO POR EL DE TU ARCHIVO NUEVO
    cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-1ce1062898.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Mi Despensa Inteligente", page_icon="📦")
st.title("📦 GESTIÓN DE MI DESPENSA")

# --- SECCIÓN 1: REGISTRO DE MOVIMIENTOS ---
st.header("1. Registrar Ingreso o Gasto")

with st.container():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        accion = st.selectbox("¿Qué hiciste?:", ["Ingreso (Compré)", "Gasto (Consumí)"])
    with col2:
        # Convertimos a minúsculas para que 'Sal' y 'sal' sean lo mismo en la base de datos
        nombre_prod = st.text_input("Producto:").strip().lower()
    with col3:
        cantidad_mov = st.number_input("Cantidad:", min_value=0.1, step=1.0, value=1.0)

    if st.button("Confirmar Movimiento", use_container_width=True):
        if nombre_prod:
            # Buscamos el producto en la colección 'productos'
            doc_ref = db.collection("productos").document(nombre_prod)
            doc = doc_ref.get()
            
            # Si el producto existe traemos su cantidad, si no, empezamos en 0
            cant_actual = doc.to_dict().get("cantidad", 0) if doc.exists else 0
            
            # Calculamos la nueva cantidad
            if "Gasto" in accion:
                nueva_cant = max(0, cant_actual - cantidad_mov)
                mensaje = f"Gastaste {cantidad_mov}. Ahora quedan {nueva_cant} de {nombre_prod}."
            else:
                nueva_cant = cant_actual + cantidad_mov
                mensaje = f"Compraste {cantidad_mov}. Ahora hay {nueva_cant} de {nombre_prod}."
            
            # Guardamos en Firebase
            doc_ref.set({
                "nombre": nombre_prod.capitalize(),
                "cantidad": nueva_cant,
                "ultima_actualizacion": datetime.now()
            }, merge=True)
            
            st.success(f"✅ {mensaje}")
            st.rerun() # Refresca la app para ver los cambios abajo
        else:
            st.error("⚠️ Por favor, escribe el nombre del producto.")

st.divider()

# --- SECCIÓN 2: INVENTARIO EN TIEMPO REAL ---
st.header("2. Mi Despensa Actual")

try:
    # Traemos todos los productos guardados
    productos_docs = db.collection("productos").get()
    lista_inventario = []

    for p in productos_docs:
        datos = p.to_dict()
        lista_inventario.append({
            "Producto": datos.get("nombre", p.id.capitalize()),
            "Cantidad en Stock": datos.get("cantidad", 0)
        })

    if lista_inventario:
        # Convertimos a tabla bonita de Pandas
        df = pd.DataFrame(lista_inventario)
        # Mostramos la tabla sin el índice de números a la izquierda
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Alerta de poco stock
        for item in lista_inventario:
            if item["Cantidad en Stock"] < 2:
                st.warning(f"🪫 ¡Atención! Te queda poco: {item['Producto']}")
    else:
        st.info("Aún no tienes productos registrados. ¡Agrega el primero arriba!")

except Exception as e:
    st.error(f"Hubo un error al leer la base de datos: {e}")
