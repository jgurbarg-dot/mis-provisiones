import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

st.set_page_config(page_title="Gestión de Despensa", page_icon="📦")

# --- CONEXIÓN A FIREBASE DESDE SECRETS ---
@st.cache_resource
def inicializar_firebase():
    if not firebase_admin._apps:
        try:
            # Buscamos la información que pegaste en Secrets
            secret_json = st.secrets["textkey"]["json"]
            datos_llave = json.loads(secret_json)
            
            cred = credentials.Certificate(datos_llave)
            firebase_admin.initialize_app(cred)
            return firestore.client()
        except Exception as e:
            st.error(f"Error al conectar con la base de datos: {e}")
            return None
    return firestore.client()

db = inicializar_firebase()

# --- TÍTULO ---
st.title("📦 GESTIÓN DE MI DESPENSA")

if db:
    # --- FORMULARIO ---
    with st.form("registro_despensa", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            accion = st.selectbox("Acción:", ["Ingreso (Compré)", "Gasto (Consumí)"])
        with col2:
            producto = st.text_input("Producto:").strip().lower()
        with col3:
            cantidad = st.number_input("Cantidad:", min_value=0.1, step=1.0)
        
        boton = st.form_submit_button("Confirmar Movimiento")

    if boton and producto:
        with st.spinner("Guardando en Firebase..."):
            try:
                doc_ref = db.collection("productos").document(producto)
                doc = doc_ref.get()
                
                # Obtener cantidad actual o 0 si es nuevo
                stock_actual = doc.to_dict().get("cantidad", 0) if doc.exists else 0
                
                # Calcular nuevo stock
                if "Gasto" in accion:
                    nuevo_stock = stock_actual - cantidad
                else:
                    nuevo_stock = stock_actual + cantidad
                
                nuevo_stock = max(0, nuevo_stock) # No permitir negativos

                # Guardar cambios
                doc_ref.set({
                    "nombre": producto.capitalize(),
                    "cantidad": nuevo_stock
                }, merge=True)
                
                st.success(f"✅ ¡Hecho! {producto.capitalize()}: {stock_actual} ➔ {nuevo_stock}")
            except Exception as e:
                st.error(f"Error al actualizar: {e}")

    # --- VER INVENTARIO ---
    if st.checkbox("Ver lista de productos"):
        productos = db.collection("productos").stream()
        lista = [p.to_dict() for p in productos]
        if lista:
            st.table(lista)
        else:
            st.info("Aún no tienes productos registrados.")
else:
    st.warning("⚠️ La conexión con Firebase aún no está lista. Revisa los Secrets.")
