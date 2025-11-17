@app.route('/pago_mercadopago', methods=['GET', 'POST'])
def pago_mercadopago():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario_id = session['usuario_id']
    carrito_items = Carrito.query.filter_by(usuario_id=usuario_id).all()
    
    if not carrito_items:
        flash("Tu carrito está vacío", "error")
        return redirect(url_for('carrito'))
    
    
    productos = []
    total = 0
    items_mp = []
    
    for item in carrito_items:
        producto = Producto.query.get(item.producto_id)
        if producto:
            producto.cantidad = item.cantidad
            productos.append(producto)
            subtotal = producto.precio * item.cantidad
            total += subtotal
            items_mp.append({
                "title": producto.nombre,
                "quantity": item.cantidad,
                "unit_price": float(producto.precio),
                "currency_id": "MXN"
            })
    
    
    if request.method == 'POST':
        print("🔄 POST recibido en pago_mercadopago")
        
        
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        direccion = request.form.get('direccion', '').strip()
        
        print(f"📝 Datos recibidos: nombre='{nombre}', correo='{correo}', direccion='{direccion}'")
        
        
        if not nombre or len(nombre) < 3:
            flash("El nombre debe tener al menos 3 caracteres", "error")
            return render_template('pago_mercadopago.html', productos=productos, total=total)
        
        if not correo or '@' not in correo:
            flash("Por favor ingresa un correo válido", "error")
            return render_template('pago_mercadopago.html', productos=productos, total=total)
        
        if not direccion or len(direccion) < 10:
            flash("La dirección debe ser más específica (mínimo 10 caracteres)", "error")
            return render_template('pago_mercadopago.html', productos=productos, total=total)
        
        
        session['pedido_temp'] = {
            'nombre': nombre,
            'correo': correo,
            'direccion': direccion,
            'total': total,
            'productos': [{'id': p.id, 'cantidad': p.cantidad} for p in productos]
        }
        
        
        if MP_ACCESS_TOKEN.startswith("TEST-"):
            print("🧪 MODO TEST DETECTADO - Iniciando simulación")
            return render_template('pago_test_processing.html', 
                                 nombre=nombre, correo=correo, 
                                 direccion=direccion, total=total,
                                 productos=productos)
        
        
        preference_data = {
            "items": items_mp,
            "payer": {
                "name": nombre,
                "email": correo
            },
            "back_urls": {
                "success": url_for('pago_exitoso', _external=True),
                "failure": url_for('pago_fallido', _external=True),
                "pending": url_for('pago_pendiente', _external=True)
            },
            "notification_url": url_for('webhook_mercadopago', _external=True),
            "auto_return": "approved",
            "external_reference": f"laesquinita-{usuario_id}-{int(datetime.now().timestamp())}",
            "payment_methods": {
                "excluded_payment_methods": [],
                "excluded_payment_types": [],
                "installments": 12
            },
            "shipments": {
                "cost": 0,
                "mode": "not_specified"
            }
        }
        
        try:
            print(f"🔧 PRODUCCIÓN: Creando preferencia MercadoPago")
            preference_response = sdk.preference().create(preference_data)
            print(f"🔧 DEBUG: Respuesta de MercadoPago: {preference_response}")
            
            if preference_response["status"] == 201:
                preference = preference_response["response"]
                print(f"🔧 DEBUG: Redirigiendo a: {preference['init_point']}")
                return redirect(preference["init_point"])
            else:
                print(f"❌ ERROR: Status no exitoso: {preference_response}")
                flash("Error al procesar el pago con MercadoPago", "error")
                return render_template('pago_mercadopago.html', productos=productos, total=total)
                
        except Exception as e:
            print(f"❌ EXCEPCIÓN: {str(e)}")
            flash(f"Error de conexión con MercadoPago: {str(e)}", "error")
            return render_template('pago_mercadopago.html', productos=productos, total=total)
    
    
    return render_template('pago_mercadopago.html', productos=productos, total=total)