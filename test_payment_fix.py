if MP_ACCESS_TOKEN.startswith("TEST-"):
    print("🧪 MODO TEST: Simulando pago exitoso automático")
    
    # Crear pedido directamente
    nuevo_pedido = Pedido(
        usuario_id=usuario_id,
        estado='Confirmado - TEST',
        total=total,
        fecha=datetime.now(),
        direccion=direccion,
        nombre=nombre,
        correo=correo,
        metodo_pago='MercadoPago TEST',
        payment_id=f"TEST-{int(datetime.now().timestamp())}"
    )
    db.session.add(nuevo_pedido)
    db.session.flush()
    
    
    for producto_info in session['pedido_temp']['productos']:
        pedido_item = PedidoItem(
            pedido_id=nuevo_pedido.id,
            producto_id=producto_info['id'],
            cantidad=producto_info['cantidad']
        )
        db.session.add(pedido_item)
    
    
    Carrito.query.filter_by(usuario_id=usuario_id).delete()
    db.session.commit()
    

    try:
        enviar_confirmacion_pago(correo, nuevo_pedido, 'MercadoPago TEST')
        print("✅ Correo de confirmación enviado")
    except Exception as email_error:
        print(f"⚠️ Error enviando email: {email_error}")
    
    
    session.pop('pedido_temp', None)
    
    flash('🧪 ¡Pago TEST procesado exitosamente! Revisa tu correo.', 'success')
    return render_template('pago_exitoso.html', pedido=nuevo_pedido)
else:
    
    print(f"🔧 DEBUG: Redirigiendo a: {preference['init_point']}")
    return redirect(preference["init_point"])