"""
Rutas para la gestión de órdenes de compra en PyPOS Local.
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.inventory_adjustment import InventoryAdjustment
from sqlalchemy import desc
import uuid

bp = Blueprint('purchase_orders', __name__, url_prefix='/purchase-orders')


@bp.route('/')
@login_required
def index():
    """
    Muestra la lista de órdenes de compra.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filtros
    supplier_id = request.args.get('supplier_id', type=int)
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Construir query base
    query = PurchaseOrder.query
    
    # Aplicar filtros
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(PurchaseOrder.order_date >= date_from)
        except ValueError:
            flash('Formato de fecha inválido para fecha inicial', 'warning')
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(PurchaseOrder.order_date <= date_to)
        except ValueError:
            flash('Formato de fecha inválido para fecha final', 'warning')
    
    # Ordenar y paginar
    purchase_orders = query.order_by(desc(PurchaseOrder.order_date)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Obtener proveedores para filtro
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    
    return render_template(
        'purchase_orders/index.html',
        purchase_orders=purchase_orders,
        suppliers=suppliers,
        filters={
            'supplier_id': supplier_id,
            'status': status,
            'date_from': date_from,
            'date_to': date_to
        },
        statuses=PurchaseOrder.VALID_STATUSES
    )


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Crea una nueva orden de compra.
    """
    if request.method == 'POST':
        # Obtener datos básicos del formulario
        supplier_id = request.form.get('supplier_id', type=int)
        expected_date = request.form.get('expected_date')
        notes = request.form.get('notes')
        
        # Validaciones
        if not supplier_id:
            flash('Debe seleccionar un proveedor', 'danger')
            return redirect(url_for('purchase_orders.create'))
        
        # Convertir fecha esperada
        expected_date_obj = None
        if expected_date:
            try:
                expected_date_obj = datetime.strptime(expected_date, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha inválido para fecha esperada', 'warning')
                return redirect(url_for('purchase_orders.create'))
        
        # Obtener productos del carrito
        products = []
        i = 0
        while f'product_id_{i}' in request.form:
            product_id = request.form.get(f'product_id_{i}', type=int)
            quantity = request.form.get(f'quantity_{i}', type=int)
            unit_price = request.form.get(f'unit_price_{i}', type=float)
            
            if product_id and quantity and unit_price:
                products.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price
                })
            
            i += 1
        
        if not products:
            flash('Debe agregar al menos un producto a la orden', 'danger')
            return redirect(url_for('purchase_orders.create'))
        
        # Crear orden de compra
        try:
            # Generar número de orden único
            order_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Crear orden
            purchase_order = PurchaseOrder(
                order_number=order_number,
                supplier_id=supplier_id,
                user_id=current_user.id,
                expected_date=expected_date_obj,
                notes=notes,
                status=PurchaseOrder.STATUS_PENDING
            )
            
            db.session.add(purchase_order)
            db.session.flush()  # Para obtener el ID de la orden
            
            # Agregar items a la orden
            for product_data in products:
                item = PurchaseOrderItem(
                    purchase_order_id=purchase_order.id,
                    product_id=product_data['product_id'],
                    quantity=product_data['quantity'],
                    unit_price=product_data['unit_price']
                )
                db.session.add(item)
            
            # Calcular totales
            purchase_order.calculate_totals()
            
            db.session.commit()
            
            flash(f'Orden de compra {order_number} creada correctamente', 'success')
            return redirect(url_for('purchase_orders.view', order_id=purchase_order.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la orden de compra: {str(e)}', 'danger')
            return redirect(url_for('purchase_orders.create'))
    
    # GET request - mostrar formulario
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    
    return render_template(
        'purchase_orders/create.html',
        suppliers=suppliers,
        products=products
    )


@bp.route('/view/<int:order_id>')
@login_required
def view(order_id):
    """
    Muestra los detalles de una orden de compra.
    """
    purchase_order = PurchaseOrder.query.get_or_404(order_id)
    
    return render_template(
        'purchase_orders/view.html',
        purchase_order=purchase_order
    )


@bp.route('/update-status/<int:order_id>', methods=['POST'])
@login_required
def update_status(order_id):
    """
    Actualiza el estado de una orden de compra.
    """
    purchase_order = PurchaseOrder.query.get_or_404(order_id)
    
    new_status = request.form.get('status')
    
    if not new_status or new_status not in PurchaseOrder.VALID_STATUSES:
        flash('Estado no válido', 'danger')
        return redirect(url_for('purchase_orders.view', order_id=order_id))
    
    # Validar cambios de estado permitidos
    if purchase_order.status == PurchaseOrder.STATUS_CANCELLED:
        flash('No se puede cambiar el estado de una orden cancelada', 'warning')
        return redirect(url_for('purchase_orders.view', order_id=order_id))
    
    if purchase_order.status == PurchaseOrder.STATUS_RECEIVED and new_status != PurchaseOrder.STATUS_CANCELLED:
        flash('No se puede cambiar el estado de una orden ya recibida', 'warning')
        return redirect(url_for('purchase_orders.view', order_id=order_id))
    
    # Actualizar estado
    try:
        purchase_order.status = new_status
        
        # Si se está cancelando
        if new_status == PurchaseOrder.STATUS_CANCELLED:
            purchase_order.notes = f"{purchase_order.notes}\n\nCancelada por {current_user.username} el {datetime.now().strftime('%d/%m/%Y %H:%M')}."
        
        db.session.commit()
        
        flash(f'Estado de la orden actualizado a "{PurchaseOrder.get_status_display(new_status)}"', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar el estado de la orden: {str(e)}', 'danger')
    
    return redirect(url_for('purchase_orders.view', order_id=order_id))


@bp.route('/receive/<int:order_id>', methods=['GET', 'POST'])
@login_required
def receive(order_id):
    """
    Recibe productos de una orden de compra.
    """
    purchase_order = PurchaseOrder.query.get_or_404(order_id)
    
    # Verificar estado
    if purchase_order.status == PurchaseOrder.STATUS_CANCELLED:
        flash('No se pueden recibir productos de una orden cancelada', 'warning')
        return redirect(url_for('purchase_orders.view', order_id=order_id))
    
    if purchase_order.status == PurchaseOrder.STATUS_RECEIVED:
        flash('Esta orden ya ha sido recibida completamente', 'warning')
        return redirect(url_for('purchase_orders.view', order_id=order_id))
    
    if purchase_order.status == PurchaseOrder.STATUS_DRAFT:
        flash('No se pueden recibir productos de una orden en borrador', 'warning')
        return redirect(url_for('purchase_orders.view', order_id=order_id))
    
    if request.method == 'POST':
        # Obtener datos del formulario
        all_received = True
        received_items = []
        
        for item in purchase_order.items:
            quantity_received = request.form.get(f'quantity_received_{item.id}', type=int)
            
            if quantity_received is None or quantity_received < 0:
                flash('Las cantidades recibidas deben ser números no negativos', 'danger')
                return redirect(url_for('purchase_orders.receive', order_id=order_id))
            
            if quantity_received > 0:
                received_items.append({
                    'item': item,
                    'quantity': quantity_received
                })
            
            # Verificar si queda algo por recibir
            if item.quantity > (item.quantity_received + (quantity_received or 0)):
                all_received = False
        
        # Verificar que se reciba al menos un producto
        if not received_items:
            flash('Debe recibir al menos un producto', 'danger')
            return redirect(url_for('purchase_orders.receive', order_id=order_id))
        
        # Procesar recepción
        try:
            # Actualizar inventario para cada producto recibido
            for received in received_items:
                item = received['item']
                quantity = received['quantity']
                
                # Actualizar cantidad recibida en el item
                item.receive(quantity)
                
                # Actualizar stock del producto
                product = Product.query.get(item.product_id)
                prev_stock = product.current_stock
                product.current_stock += quantity
                
                # Registrar ajuste de inventario
                adjustment = InventoryAdjustment(
                    product_id=product.id,
                    user_id=current_user.id,
                    quantity_change=quantity,
                    previous_stock=prev_stock,
                    reason=InventoryAdjustment.REASON_PURCHASE,
                    reference=f"Orden: {purchase_order.order_number}",
                    notes=f"Recepción de productos de orden de compra #{purchase_order.order_number}"
                )
                
                db.session.add(adjustment)
            
            # Actualizar estado de la orden
            if all_received:
                purchase_order.status = PurchaseOrder.STATUS_RECEIVED
                purchase_order.received_date = datetime.now()
            else:
                purchase_order.status = PurchaseOrder.STATUS_PARTIAL
            
            db.session.commit()
            
            flash('Productos recibidos correctamente', 'success')
            return redirect(url_for('purchase_orders.view', order_id=order_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar la recepción: {str(e)}', 'danger')
            return redirect(url_for('purchase_orders.receive', order_id=order_id))
    
    # GET request - mostrar formulario
    return render_template(
        'purchase_orders/receive.html',
        purchase_order=purchase_order
    )


@bp.route('/print/<int:order_id>')
@login_required
def print_order(order_id):
    """
    Muestra una versión para imprimir de la orden de compra.
    """
    purchase_order = PurchaseOrder.query.get_or_404(order_id)
    
    return render_template(
        'purchase_orders/print.html',
        purchase_order=purchase_order
    )


@bp.route('/product/<int:product_id>', methods=['GET'])
@login_required
def get_product_info(product_id):
    """
    Obtiene información de un producto para la orden de compra.
    """
    product = Product.query.get_or_404(product_id)
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'current_stock': product.current_stock,
        'purchase_price': float(product.purchase_price)
    }) 