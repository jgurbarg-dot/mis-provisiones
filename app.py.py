
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# 1. Mantenemos tu conexión (asegúrate que el JSON esté en la misma carpeta en GitHub)
if not firebase_admin._apps:
    cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-29b42419c3.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. Interfaz de Streamlit (Sustituye al print inicial)
st.title("GESTIÓN DE PROVISIONES")

# 3. Sustituimos los 'input()' por campos de texto y número de Streamlit
nombre = st.text_input("Producto:").strip().capitalize()
cantidad_nueva = st.number_input("¿Cuánta cantidad ingresó?", min_value=0.0, step=1.0)

# 4. Usamos un botón para ejecutar tu lógica (sustituye al flujo del while)
if st.button("Actualizar Inventario"):
    if nombre:
        doc_ref = db.collection("productos").document(nombre.lower())
        doc = doc_ref.get()

        if doc.exists:
            cantidad_actual = doc.to_dict().get("cantidad", 0)
            nueva_total = cantidad_actual + cantidad_nueva
            doc_ref.update({"cantidad": nueva_total})
            # Sustituimos print() por st.success() para que se vea en la web
            st.success(f"Actualizado: Ahora tienes {nueva_total} de {nombre}.")
        else:
            doc_ref.set({
                "nombre": nombre,
                "cantidad": cantidad_nueva,
                "unidad": "unidades"
            })
            st.info(f"Nuevo Producto: {nombre} guardado con {cantidad_nueva}.")
    else:
        st.warning("Por favor, escribe el nombre de un producto.")

# 5. Mostrar el inventario (Tu bloque final de print)
st.subheader("--- INVENTARIO ACTUALIZADO EN LA NUBE ---")
productos = db.collection("productos").stream()
for p in productos:
    datos = p.to_dict()
    # Sustituimos el print final por st.write
    st.write(f"**{datos['nombre']}**: {datos['cantidad']} {datos.get('unidad', '')}")

import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
  ruta_llave="/content/mis-provisiones-firebase-adminsdk-fbsvc-29b42419c3.json"
  cred=credentials.Certificate(ruta_llave)
  firebase_admin.initialize_app(cred)
db=firestore.client()

db.collection("estado").document("conexion").set({"mensaje":"!Hola desde el otro email!","funciona":True})
print("¡Conexión exitosa! Ve a revisar tu pestaña de Firebase.")
