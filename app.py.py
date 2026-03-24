import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# 1. Conexión con Firebase
if not firebase_admin._apps:
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
    nombre = st.text_input("Producto:").strip().capitalize()
with col3:
    cantidad_op = st.number_input("Cantidad:", min_value=0.0, step=1.0)

if st.button("Confirmar Movimiento", use_container_width=True):
    if nombre:
        doc_ref = db.collection("productos").document(nombre.lower())
        doc = doc_ref.get()
        
        cant_previa = doc.to_dict().get("cantidad", 0) if doc.exists else 0
        
        # Calculamos el nuevo total
        if "Gasto" in accion:
            nueva_cant = cant_previa - cantidad_op
            if nueva_cant < 0: nueva_cant = 0
            tipo_log = "SALIDA"
        else:
            nueva_cant = cant_previa + cantidad_op
            tipo_log = "ENTRADA"
            
        # Guardamos el stock actual
        doc_ref.set({"cantidad": nueva_cant, "ultima_actualizacion": datetime.now()})
        
        # Guardamos el historial (Log)
        db.collection("historial").add({
            "producto": nombre,
            "tipo": tipo_log,
            "cantidad": cantidad_op,
            "fecha": datetime.now()
        })
        
        st.success(f"Movimiento registrado. {nombre} ahora tiene {nueva_cant} unidades.")
    else:
        st.error("Escribe un nombre de producto.")

st.divider()

# --- SECCIÓN 2: DISPONIBILIDAD ACTUAL ---
st.header("2. Inventario Disponible (Cantidades Actuales)")

productos = db.collection("productos").stream()
lista_prod = []
for p in productos:
    d = p.to_dict()
    lista_prod.append({"Producto": p.id.capitalize(), "Stock Actual": d.get("cantidad", 0)})

if lista_prod:
    df_stock = pd.DataFrame(lista_prod)
    st.table(df_stock) # Muestra una tabla limpia
else:
    st.info("No hay productos en el inventario.")

# --- SECCIÓN 3: HISTORIAL DE MOVIMIENTOS ---
st.header("3. ¿En qué se fue el stock? (Historial)")

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
    st.dataframe(pd.DataFrame(lista_hist), use_container_width=True)
# --- INVENTARIO ACTUAL (STOCK DISPONIBLE) ---
st.header("4. Inventario Disponible (Totales)")

# 1. Consultar la colección de productos
productos_ref = db.collection("productos").stream()

inventario_lista = []

for p in productos_ref:
    datos = p.to_dict()
    inventario_lista.append({
        "Producto": p.id.capitalize(),
        "Cantidad disponible": datos.get("cantidad", 0)
    })

# 2. Mostrarlo en una tabla si hay datos
if inventario_lista:
    st.dataframe(pd.DataFrame(inventario_lista), use_container_width=True)
else:
    st.write("No hay productos registrados en el inventario.")
