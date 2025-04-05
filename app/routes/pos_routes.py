"""
Blueprint para las rutas relacionadas con el punto de venta (POS).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem
from app.models.cashier_session import CashierSession
from app import db
from datetime import datetime
import json

bp = Blueprint('pos', __name__, url_prefix='/pos')

@bp.route('/')
@login_required
def index():
    """
    Muestra la interfaz principal del punto de venta.
    
    Returns:
        Plantilla con la interfaz de punto de venta
    """
    # Verificar si hay una sesión de caja abierta para el usuario actual
    session = CashierSession.get_current_session(current_user.id)
    if not session:
        flash('Debe abrir una sesión de caja antes de usar el punto de venta.', 'warning')
        return redirect(url_for('cashier.new_session'))
    
    # Obtener productos activos para mostrar en la interfaz
    products = Product.query.filter_by(is_active=True).all()
    
    # Obtener clientes activos para asociar a la venta
    customers = Customer.query.filter_by(is_active=True).all()
    
    return render_template('pos/index.html', products=products, customers=customers, session=session)

@bp.route('/search-products')
@login_required
def search_products():
    """
    Busca productos para el punto de venta.
    
    Returns:
        JSON con los productos encontrados
    """
    query = request.args.get('query', '')
    
    if not query:
        return jsonify([])
    
    # Buscar por nombre, SKU o código de barras
    products = Product.query.filter(
        (Product.name.ilike(f'%{query}%')) | 
        (Product.sku.ilike(f'%{query}%')) |
        (Product.barcode.ilike(f'%{query}%'))
    ).filter_by(is_active=True).all()
    
    # Convertir a formato JSON
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'sale_price': float(product.sale_price),
            'current_stock': product.current_stock,
            'is_in_stock': product.is_in_stock,
            'barcode': product.barcode,
            'sku': product.sku,
            'category': product.category.name if product.category else None
        })
    
    return jsonify(result)

@bp.route('/create-sale', methods=['POST'])
@login_required
def create_sale():
    """
    Procesa una nueva venta.
    
    Returns:
        JSON con el resultado de la operación
    """
    # Verificar si hay una sesión de caja abierta
    session = CashierSession.get_current_session(current_user.id)
    if not session:
        return jsonify({
            'success': False,
            'message': 'No hay una sesión de caja abierta.'
        }), 400
    
    try:
        # Obtener datos de la venta desde el formulario JSON
        data = request.json
        
        # Verificar datos obligatorios
        if not data or 'items' not in data or not data['items']:
            return jsonify({
                'success': False,
                'message': 'No se han proporcionado artículos para la venta.'
            }), 400
        
        # Crear la venta
        sale = Sale(
            user_id=current_user.id,
            customer_id=data.get('customer_id'),
            payment_method=data.get('payment_method', 'cash'),
            status='pending',
            notes=data.get('notes', '')
        )
        
        # Asociar a la sesión de caja
        sale.session_id = session.id
        
        db.session.add(sale)
        db.session.flush()  # Para obtener el ID de la venta
        
        # Procesar los items de la venta
        for item_data in data['items']:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            
            if not product_id or quantity <= 0:
                continue
            
            # Buscar el producto
            product = Product.query.get(product_id)
            if not product:
                continue
            
            # Verificar stock disponible
            if quantity > product.current_stock:
                return jsonify({
                    'success': False,
                    'message': f'Stock insuficiente para {product.name}. Disponible: {product.current_stock}'
                }), 400
            
            # Añadir item a la venta
            sale.add_item(product, quantity)
        
        # Aplicar descuento si existe
        if 'discount_amount' in data:
            sale.discount_amount = float(data['discount_amount'])
        
        # Aplicar impuesto si existe
        if 'tax_amount' in data:
            sale.tax_amount = float(data['tax_amount'])
        
        # Calcular totales
        sale.calculate_totals()
        
        # Completar la venta
        if not sale.complete_sale():
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'Error al procesar la venta. Por favor, inténtelo de nuevo.'
            }), 500
        
        # Retornar éxito
        return jsonify({
            'success': True,
            'message': 'Venta procesada correctamente',
            'sale_id': sale.id,
            'total': float(sale.final_amount),
            'redirect': url_for('pos.receipt', sale_id=sale.id)
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al procesar la venta: {str(e)}'
        }), 500

@bp.route('/receipt/<int:sale_id>')
@login_required
def receipt(sale_id):
    """
    Muestra el recibo de una venta.
    
    Args:
        sale_id: ID de la venta
        
    Returns:
        Plantilla con el recibo de la venta
    """
    sale = Sale.query.get_or_404(sale_id)
    
    # Verificar que el usuario actual es quien realizó la venta o es admin
    if sale.user_id != current_user.id and not current_user.is_admin:
        flash('No tiene permiso para ver este recibo.', 'danger')
        return redirect(url_for('pos.index'))
    
    return render_template('pos/receipt.html', sale=sale)

@bp.route('/cancel-sale/<int:sale_id>', methods=['POST'])
@login_required
def cancel_sale(sale_id):
    """
    Cancela una venta.
    
    Args:
        sale_id: ID de la venta a cancelar
        
    Returns:
        Redirección a la lista de ventas
    """
    sale = Sale.query.get_or_404(sale_id)
    
    # Verificar que el usuario actual es quien realizó la venta o es admin
    if sale.user_id != current_user.id and not current_user.is_admin:
        flash('No tiene permiso para cancelar esta venta.', 'danger')
        return redirect(url_for('sales.index'))
    
    # Verificar que la venta no esté ya cancelada
    if sale.status == 'cancelled':
        flash('Esta venta ya ha sido cancelada.', 'warning')
        return redirect(url_for('sales.index'))
    
    # Intentar cancelar la venta
    if sale.cancel_sale():
        flash('Venta cancelada correctamente.', 'success')
    else:
        flash('Error al cancelar la venta.', 'danger')
    
    return redirect(url_for('sales.index'))

@bp.route('/sales-history')
@login_required
def sales_history():
    """
    Muestra el historial de ventas del día actual para el usuario.
    
    Returns:
        Plantilla con el historial de ventas
    """
    # Obtener fecha actual
    today = datetime.now().date()
    
    # Obtener ventas del día actual para el usuario actual
    sales = Sale.query.filter(
        Sale.user_id == current_user.id,
        Sale.sale_datetime >= today
    ).order_by(Sale.sale_datetime.desc()).all()
    
    return render_template('pos/sales_history.html', sales=sales) 