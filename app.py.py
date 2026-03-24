if st.button("Confirmar Movimiento", use_container_width=True):
    if nombre:
        # 1. Referencia al documento (siempre en minúsculas para evitar duplicados)
        doc_id = nombre.lower()
        doc_ref = db.collection("productos").document(doc_id)
        doc = doc_ref.get()
        
        # 2. Obtener cantidad actual (verificando que el campo exista)
        datos_viejos = doc.to_dict() if doc.exists else {}
        cant_previa = datos_viejos.get("cantidad", 0)
        
        # 3. Calcular nueva cantidad
        if "Gasto" in accion:
            nueva_cant = cant_previa - cantidad_op
            if nueva_cant < 0: nueva_cant = 0
            tipo_log = "SALIDA"
        else:
            nueva_cant = cant_previa + cantidad_op
            tipo_log = "ENTRADA"
            
        # 4. GUARDAR EN FIRESTORE (Usamos update para no borrar otros campos como 'unidad')
        if doc.exists:
            doc_ref.update({
                "cantidad": nueva_cant,
                "ultima_actualizacion": datetime.now()
            })
        else:
            doc_ref.set({
                "nombre": nombre,
                "cantidad": nueva_cant,
                "unidad": "unidades", # Valor por defecto
                "ultima_actualizacion": datetime.now()
            })
        
        # 5. Guardar Historial
        db.collection("historial").add({
            "producto": nombre,
            "tipo": tipo_log,
            "cantidad": cantidad_op,
            "fecha": datetime.now()
        })
        
        st.success(f"Actualizado: {nombre} ahora tiene {nueva_cant}")
        
        # 6. FORZAR RECARGA (Para que veas el cambio en la tabla de abajo al instante)
        st.rerun()
    else:
        st.error("Escribe el nombre del producto")
