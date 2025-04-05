from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import login_required, current_user
from app.models import Product, Category, Customer, Sale, SaleItem, InventoryAdjustment
from app import db

bp = Blueprint('pos', __name__, url_prefix='/pos')

@bp.route('/')
@login_required
def index():
    """Vista principal del punto de venta."""
    products = Product.query.filter(Product.current_stock > 0).all()
    categories = Category.query.all()
    customers = Customer.query.all()
    return render_template('pos/index.html', 
                         products=products,
                         categories=categories,
                         customers=customers)

@bp.route('/process-sale', methods=['POST'])
@login_required
def process_sale():
    """Procesa una nueva venta."""
    try:
        data = request.get_json()
        
        if not data or 'items' not in data or not data['items']:
            return jsonify({'success': False, 'message': 'No hay items en el carrito'}), 400
        
        # Crear la venta
        sale = Sale(
            user_id=current_user.id,
            customer_id=data.get('customer_id'),
            payment_method=data.get('payment_method', 'cash'),
            payment_details=data.get('payment_details', {}),
            notes=data.get('notes', ''),
            date=datetime.now()
        )
        db.session.add(sale)
        db.session.flush()  # Para obtener el ID de la venta
        
        subtotal = 0
        
        # Procesar cada item
        for item in data['items']:
            product = Product.query.get(item['id'])
            if not product:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'Producto no encontrado: {item["id"]}'
                }), 404
            
            if product.current_stock < item['quantity']:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'Stock insuficiente para {product.name}'
                }), 400
            
            # Crear el item de venta
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=item['quantity'],
                unit_price=product.sale_price,
                subtotal=product.sale_price * item['quantity']
            )
            db.session.add(sale_item)
            
            # Actualizar el stock
            adjustment = InventoryAdjustment(
                product_id=product.id,
                user_id=current_user.id,
                quantity_change=-item['quantity'],
                previous_stock=product.current_stock,
                reason='sale',
                notes=f'Venta #{sale.id}'
            )
            db.session.add(adjustment)
            
            product.current_stock -= item['quantity']
            subtotal += sale_item.subtotal
        
        # Actualizar totales de la venta
        sale.subtotal = subtotal
        sale.tax = subtotal * 0.16  # IVA 16%
        sale.total = subtotal + sale.tax
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'sale_id': sale.id,
            'message': 'Venta procesada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al procesar la venta: {str(e)}'
        }), 500

@bp.route('/print-ticket/<int:sale_id>')
@login_required
def print_ticket(sale_id):
    """Genera el ticket de venta para imprimir."""
    sale = Sale.query.get_or_404(sale_id)
    
    # Verificar permisos
    if sale.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    return render_template('pos/ticket.html', sale=sale) 