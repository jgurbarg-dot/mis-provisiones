import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión de Despensa", page_icon="📦")

# Debug: Ver archivos en el entorno (puedes borrar esto después)
# st.write("Archivos detectados:", os.listdir())

st.title("📦 GESTIÓN DE MI DESPENSA")

# --- FUNCIÓN DE CONEXIÓN OPTIMIZADA ---
def conectar_firebase():
    # El nombre exacto de tu archivo JSON
    nombre_json = "misprovisionesfirebaseadminsdkfbsvc674f03e169.json"
    
    if not firebase_admin._apps:
        try:
            if not os.path.exists(nombre_json):
                st.error(f"❌ No se encuentra el archivo: {nombre_json}")
                return None
                
            cred = credentials.Certificate(nombre_json)
            firebase_admin.initialize_app(cred)
            return firestore.client()
        except Exception as e:
            st.error(f"❌ Error al inicializar Firebase: {e}")
            return None
    else:
        # Si ya está inicializado, solo devolvemos el cliente
        return firestore.client()

# --- INTERFAZ DE USUARIO ---
st.header("1. Registrar Ingreso o Gasto")
col1, col2, col3 = st.columns(3)

with col1:
    accion = st.selectbox("Acción:", ["Ingreso (Compré)", "Gasto (Consumí)"])

with col2:
    # Limpiamos el texto para evitar errores de espacios
    nombre_prod = st.text_input("Producto:").strip().lower()

with col3:
    cantidad_mov = st.number_input("Cantidad:", min_value=0.1, step=0.5, format="%.2f")

# --- LÓGICA DEL BOTÓN ---
if st.button("Confirmar Movimiento"):
    if nombre_prod == "":
        st.warning("⚠️ Por favor, escribe el nombre de un producto.")
    else:
        # Iniciamos la conexión
        db = conectar_firebase()

        if db is not None:
            with st.spinner('Comunicando con la base de datos...'):
                try:
                    # 1. Referencia al documento
                    doc_ref = db.collection("productos").document(nombre_prod)
                    doc = doc_ref.get()

                    # 2. Obtener cantidad actual
                    if doc.exists:
                        datos_viejos = doc.to_dict()
                        cant_actual = datos_viejos.get("cantidad", 0)
                    else:
                        cant_actual = 0
                        st.info(f"Nuevo producto detectado: {nombre_prod.capitalize()}")

                    # 3. Calcular nueva cantidad
                    if "Gasto" in accion:
                        nueva_cant = cant_actual - cantidad_mov
                    else:
                        nueva_cant = cant_actual + cantidad_mov

                    # Evitar cantidades negativas si es un gasto
                    nueva_cant_final = max(0, nueva_cant)

                    # 4. Guardar en Firebase
                    doc_ref.set({
                        "nombre": nombre_prod.capitalize(),
                        "cantidad": nueva_cant_final,
                        "ultima_actualizacion": firestore.SERVER_TIMESTAMP
                    }, merge=True)

                    st.success(f"✅ ¡Éxito! {nombre_prod.capitalize()}: {cant_actual} ➔ {nueva_cant_final}")
                    
                except Exception as e:
                    st.error(f"❌ Error en la operación: {e}")
        else:
            st.error("❌ No se pudo establecer la conexión con Firebase.")

# --- SECCIÓN EXTRA: VER INVENTARIO (Opcional) ---
if st.checkbox("Ver inventario actual"):
    db = conectar_firebase()
    if db:
        productos = db.collection("productos").stream()
        lista_prod = []
        for p in productos:
            lista_prod.append(p.to_dict())
        
        if lista_prod:
            st.table(lista_prod)
        else:
            st.write("La despensa está vacía.")
