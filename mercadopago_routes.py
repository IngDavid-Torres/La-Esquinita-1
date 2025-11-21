
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from mercadopago_config import create_preference, get_payment_info, is_test_environment, MP_PUBLIC_KEY
import json

def init_mercadopago_routes(app, db, Carrito, Producto, Pedido, PedidoItem, Usuario, enviar_email_background):
    """
    Inicializa todas las rutas relacionadas con Mercado Pago
    """
    
    @app.route('/pago_mercadopago', methods=['GET', 'POST'])
    def pago_mercadopago():
        """
        Página de checkout con Mercado Pago
        """
        if 'usuario_id' not in session:
            flash("Debes iniciar sesión para continuar", "error")
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
                return render_template('pago_mercadopago.html', 
                                     productos=productos, 
                                     total=total,
                                     mp_public_key=MP_PUBLIC_KEY)
            
            if not correo or '@' not in correo:
                flash("Por favor ingresa un correo válido", "error")
                return render_template('pago_mercadopago.html', 
                                     productos=productos, 
                                     total=total,
                                     mp_public_key=MP_PUBLIC_KEY)
            
            if not direccion or len(direccion) < 10:
                flash("La dirección debe ser más específica (mínimo 10 caracteres)", "error")
                return render_template('pago_mercadopago.html', 
                                     productos=productos, 
                                     total=total,
                                     mp_public_key=MP_PUBLIC_KEY)
            
            
            session['pedido_temp'] = {
                'nombre': nombre,
                'correo': correo,
                'direccion': direccion,
                'total': total,
                'productos': [{'id': p.id, 'cantidad': p.cantidad} for p in productos]
            }
            
            
            if is_test_environment():
                print("🧪 MODO TEST - Simulando pago exitoso")
                return render_template('pago_test_processing.html', 
                                     nombre=nombre, 
                                     correo=correo, 
                                     direccion=direccion, 
                                     total=total,
                                     productos=productos)
            
           
            try:
                external_ref = f"laesquinita-{usuario_id}-{int(datetime.now().timestamp())}"
                
               
                urls = {
                    "success": url_for('pago_exitoso', _external=True),
                    "failure": url_for('pago_fallido', _external=True),
                    "pending": url_for('pago_pendiente', _external=True)
                }
                
                print(f"🔗 URLs generadas para MercadoPago:")
                print(f"   Success: {urls['success']}")
                print(f"   Failure: {urls['failure']}")
                print(f"   Pending: {urls['pending']}")
                
                payer_info = {
                    "name": nombre,
                    "email": correo
                }
                
                print(f"👤 Datos del pagador: {payer_info}")
                print(f"🛒 Items: {len(items_mp)} productos")
                
                preference_response = create_preference(items_mp, payer_info, urls, external_ref)
                
                if preference_response and preference_response["status"] == 201:
                    preference = preference_response["response"]
                    init_point = preference["init_point"]
                    
                    
                    session['mp_preference_id'] = preference["id"]
                    
                    print(f"✅ Preferencia creada: {preference['id']}")
                    print(f"🔗 Redirigiendo a: {init_point}")
                    
                    return redirect(init_point)
                else:
                    print(f"❌ Error creando preferencia: {preference_response}")
                    flash("Error al procesar el pago con MercadoPago", "error")
                    return render_template('pago_mercadopago.html', 
                                         productos=productos, 
                                         total=total,
                                         mp_public_key=MP_PUBLIC_KEY)
                    
            except Exception as e:
                print(f"❌ Excepción creando preferencia: {str(e)}")
                flash(f"Error de conexión con MercadoPago: {str(e)}", "error")
                return render_template('pago_mercadopago.html', 
                                     productos=productos, 
                                     total=total,
                                     mp_public_key=MP_PUBLIC_KEY)
        
       
        return render_template('pago_mercadopago.html', 
                             productos=productos, 
                             total=total,
                             mp_public_key=MP_PUBLIC_KEY)
    
    @app.route('/pago_exitoso')
    def pago_exitoso():
        """
        Callback cuando el pago fue exitoso
        """
        print("✅ PAGO EXITOSO - Procesando...")
        
        
        payment_id = request.args.get('payment_id')
        status = request.args.get('status')
        external_reference = request.args.get('external_reference')
        
        print(f"💳 Payment ID: {payment_id}")
        print(f"📊 Status: {status}")
        print(f"🔖 External Reference: {external_reference}")
        
        if 'usuario_id' not in session:
            flash("Sesión expirada", "error")
            return redirect(url_for('login'))
        
        if 'pedido_temp' not in session:
            flash("No hay datos del pedido", "error")
            return redirect(url_for('carrito'))
        
        try:
            pedido_data = session['pedido_temp']
            usuario_id = session['usuario_id']
            
           
            nuevo_pedido = Pedido(
                usuario_id=usuario_id,
                nombre=pedido_data['nombre'],
                correo=pedido_data['correo'],
                direccion=pedido_data['direccion'],
                metodo_pago="MercadoPago",
                total=pedido_data['total'],
                estado="Confirmado",
                payment_id=payment_id,
                fecha=datetime.now()
            )
            
            db.session.add(nuevo_pedido)
            db.session.flush()  
            
            
            for prod in pedido_data['productos']:
                item = PedidoItem(
                    pedido_id=nuevo_pedido.id,
                    producto_id=prod['id'],
                    cantidad=prod['cantidad']
                )
                db.session.add(item)
            
            
            Carrito.query.filter_by(usuario_id=usuario_id).delete()
            
            db.session.commit()
            
            print(f"✅ Pedido #{nuevo_pedido.id} creado exitosamente")
            
           
            try:
                enviar_email_background(
                    pedido_data['correo'],
                    nuevo_pedido.id,
                    pedido_data['nombre'],
                    pedido_data['direccion'],
                    pedido_data['total'],
                    "MercadoPago",
                    nuevo_pedido.fecha
                )
            except Exception as email_error:
                print(f"⚠️ Error enviando email: {email_error}")
            
            
            session.pop('pedido_temp', None)
            session.pop('mp_preference_id', None)
            
            flash(f"¡Pago confirmado! Pedido #{nuevo_pedido.id} registrado exitosamente", "success")
            return render_template('pago_exitoso.html', 
                                 pedido=nuevo_pedido,
                                 payment_id=payment_id)
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error procesando pago exitoso: {str(e)}")
            flash(f"Error al registrar el pedido: {str(e)}", "error")
            return redirect(url_for('carrito'))
    
    @app.route('/pago_fallido')
    def pago_fallido():
        """
        Callback cuando el pago falló
        """
        print("❌ PAGO FALLIDO")
        
        payment_id = request.args.get('payment_id')
        status = request.args.get('status')
        
        print(f"💳 Payment ID: {payment_id}")
        print(f"📊 Status: {status}")
        
        flash("El pago no pudo ser procesado. Por favor intenta nuevamente.", "error")
        return render_template('pago_fallido.html', 
                             payment_id=payment_id,
                             status=status)
    
    @app.route('/pago_pendiente')
    def pago_pendiente():
        
        print("⏳ PAGO PENDIENTE")
        
        payment_id = request.args.get('payment_id')
        status = request.args.get('status')
        
        print(f"💳 Payment ID: {payment_id}")
        print(f"📊 Status: {status}")
        
        flash("Tu pago está siendo procesado. Te notificaremos cuando se confirme.", "info")
        return render_template('pago_pendiente.html', 
                             payment_id=payment_id,
                             status=status)
    
    @app.route('/webhook/mercadopago', methods=['POST'])
    def webhook_mercadopago():
        """
        Webhook para recibir notificaciones de Mercado Pago
        """
        print("🔔 WEBHOOK RECIBIDO DE MERCADOPAGO")
        
        try:
            data = request.get_json()
            print(f"📦 Data recibida: {json.dumps(data, indent=2)}")
            
           
            x_signature = request.headers.get('X-Signature')
            x_request_id = request.headers.get('X-Request-Id')
            
            print(f"🔐 X-Signature: {x_signature}")
            print(f"🆔 X-Request-Id: {x_request_id}")
            
         
            if data.get('type') == 'payment':
                payment_id = data.get('data', {}).get('id')
                
                if payment_id:
                    print(f"💳 Procesando payment_id: {payment_id}")
                    
                    
                    payment_info = get_payment_info(payment_id)
                    
                    if payment_info:
                        status = payment_info.get('status')
                        external_reference = payment_info.get('external_reference')
                        
                        print(f"📊 Status del pago: {status}")
                        print(f"🔖 External Reference: {external_reference}")
                        
                        # Actualizar pedido si existe
                        if external_reference:
                            pedido = Pedido.query.filter_by(payment_id=str(payment_id)).first()
                            
                            if pedido:
                                if status == 'approved':
                                    pedido.estado = 'Confirmado'
                                elif status == 'rejected':
                                    pedido.estado = 'Rechazado'
                                elif status == 'pending':
                                    pedido.estado = 'Pendiente'
                                
                                db.session.commit()
                                print(f"✅ Pedido {pedido.id} actualizado a: {pedido.estado}")
            
            return jsonify({'status': 'ok'}), 200
            
        except Exception as e:
            print(f"❌ Error procesando webhook: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/simular_pago_exitoso', methods=['POST'])
    def simular_pago_exitoso():
        """
        Ruta para simular un pago exitoso en modo test
        """
        if not is_test_environment():
            return jsonify({'error': 'Solo disponible en modo test'}), 403
        
        print("🧪 SIMULANDO PAGO EXITOSO (TEST)")
        
        try:
            if 'usuario_id' not in session or 'pedido_temp' not in session:
                return jsonify({'error': 'Sesión inválida'}), 400
            
            pedido_data = session['pedido_temp']
            usuario_id = session['usuario_id']
            
          
            nuevo_pedido = Pedido(
                usuario_id=usuario_id,
                nombre=pedido_data['nombre'],
                correo=pedido_data['correo'],
                direccion=pedido_data['direccion'],
                metodo_pago="MercadoPago (TEST)",
                total=pedido_data['total'],
                estado="Confirmado",
                payment_id=f"TEST-{int(datetime.now().timestamp())}",
                fecha=datetime.now()
            )
            
            db.session.add(nuevo_pedido)
            db.session.flush()
            
            
            for prod in pedido_data['productos']:
                item = PedidoItem(
                    pedido_id=nuevo_pedido.id,
                    producto_id=prod['id'],
                    cantidad=prod['cantidad']
                )
                db.session.add(item)
            
           
            Carrito.query.filter_by(usuario_id=usuario_id).delete()
            
            db.session.commit()
            
           
            try:
                enviar_email_background(
                    pedido_data['correo'],
                    nuevo_pedido.id,
                    pedido_data['nombre'],
                    pedido_data['direccion'],
                    pedido_data['total'],
                    "MercadoPago (TEST)",
                    nuevo_pedido.fecha
                )
            except Exception as email_error:
                print(f"⚠️ Error enviando email: {email_error}")
            
         
            session.pop('pedido_temp', None)
            
            return jsonify({
                'success': True,
                'pedido_id': nuevo_pedido.id,
                'redirect': url_for('pago_exitoso', 
                                  payment_id=nuevo_pedido.payment_id,
                                  status='approved',
                                  external_reference=f'test-{nuevo_pedido.id}')
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error simulando pago: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    print("✅ Rutas de Mercado Pago inicializadas")
