import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Inicialización
if not firebase_admin._apps:
    cred = credentials.Certificate("mis-provisiones-firebase-adminsdk-fbsvc-29b42419c3.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("Prueba de Escritura Directa")

# Formulario ultra-simple
nombre = st.text_input("Producto (usa 'sal'):").lower().strip()
nueva_cantidad = st.number_input("Nueva Cantidad:", min_value=0)

if st.button("FORZAR ACTUALIZACIÓN"):
    try:
        # Referencia a la colección 'productos' y al documento
        doc_ref = db.collection("productos").document(nombre)
        
        # Escritura directa
        doc_ref.set({
            "nombre": nombre.capitalize(),
            "cantidad": nueva_cantidad,
            "unidad": "unidades"
        }, merge=True)
        
        st.success(f"✅ ¡Se envió a Firebase! Revisa el documento '{nombre}' ahora.")
    except Exception as e:
        st.error(f"❌ ERROR DE PERMISO O CONEXIÓN: {e}")
