"""
Rutas para la gestión avanzada de inventario en PyPOS Local.
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.inventory_adjustment import InventoryAdjustment
from app.models.inventory_alert import InventoryAlert
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from sqlalchemy import func, desc

bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@bp.route('/')
@login_required
def index():
    """
    Muestra el panel principal de gestión de inventario.
    """
    # Obtener estadísticas de inventario
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= Product.low_stock_threshold
    ).count()
    out_of_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= 0
    ).count()
    
    # Obtener alertas pendientes
    pending_alerts = InventoryAlert.query.filter_by(is_resolved=False).order_by(desc(InventoryAlert.alert_datetime)).limit(5).all()
    
    # Obtener últimos ajustes
    recent_adjustments = InventoryAdjustment.query.order_by(desc(InventoryAdjustment.adjustment_datetime)).limit(5).all()
    
    return render_template(
        'inventory/index.html',
        stats={
            'total_products': total_products,
            'active_products': active_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products
        },
        pending_alerts=pending_alerts,
        recent_adjustments=recent_adjustments
    )


@bp.route('/low-stock')
@login_required
def low_stock():
    """
    Muestra la lista de productos con stock bajo.
    """
    # Obtener productos con stock bajo
    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= Product.low_stock_threshold,
        Product.current_stock > 0
    ).order_by(Product.current_stock.asc()).all()
    
    # Obtener productos sin stock
    out_of_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.current_stock <= 0
    ).order_by(Product.name.asc()).all()
    
    return render_template(
        'inventory/low_stock.html',
        low_stock_products=low_stock_products,
        out_of_stock_products=out_of_stock_products
    )


@bp.route('/adjustments')
@login_required
def adjustments():
    """
    Muestra la lista de ajustes de inventario.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filtros
    product_id = request.args.get('product_id', type=int)
    user_id = request.args.get('user_id', type=int)
    reason = request.args.get('reason')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Construir query base
    query = InventoryAdjustment.query
    
    # Aplicar filtros
    if product_id:
        query = query.filter(InventoryAdjustment.product_id == product_id)
    if user_id:
        query = query.filter(InventoryAdjustment.user_id == user_id)
    if reason:
        query = query.filter(InventoryAdjustment.reason == reason)
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(InventoryAdjustment.adjustment_datetime >= date_from)
        except ValueError:
            flash('Formato de fecha inválido para fecha inicial', 'warning')
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(InventoryAdjustment.adjustment_datetime <= date_to)
        except ValueError:
            flash('Formato de fecha inválido para fecha final', 'warning')
    
    # Ordenar y paginar
    adjustments = query.order_by(desc(InventoryAdjustment.adjustment_datetime)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Obtener productos para filtro
    products = Product.query.order_by(Product.name).all()
    
    return render_template(
        'inventory/adjustments.html',
        adjustments=adjustments,
        products=products,
        filters={
            'product_id': product_id,
            'user_id': user_id,
            'reason': reason,
            'date_from': date_from,
            'date_to': date_to
        },
        reasons=InventoryAdjustment.VALID_REASONS
    )


@bp.route('/adjustment/new', methods=['GET', 'POST'])
@login_required
def new_adjustment():
    """
    Crea un nuevo ajuste de inventario.
    """
    if request.method == 'POST':
        product_id = request.form.get('product_id', type=int)
        quantity_change = request.form.get('quantity_change', type=int)
        reason = request.form.get('reason')
        reference = request.form.get('reference')
        notes = request.form.get('notes')
        
        # Validaciones
        if not product_id:
            flash('Debe seleccionar un producto', 'danger')
            return redirect(url_for('inventory.new_adjustment'))
        
        if not quantity_change:
            flash('Debe especificar una cantidad válida', 'danger')
            return redirect(url_for('inventory.new_adjustment'))
        
        if not reason or reason not in InventoryAdjustment.VALID_REASONS:
            flash('Debe seleccionar un motivo válido', 'danger')
            return redirect(url_for('inventory.new_adjustment'))
        
        # Obtener producto
        product = Product.query.get_or_404(product_id)
        
        # Crear ajuste
        try:
            adjustment = InventoryAdjustment(
                product_id=product_id,
                user_id=current_user.id,
                quantity_change=quantity_change,
                previous_stock=product.current_stock,
                reason=reason,
                reference=reference,
                notes=notes
            )
            
            # Actualizar stock del producto
            product.current_stock += quantity_change
            
            # Crear alerta si es necesario
            if product.is_low_stock and not product.current_stock <= 0:
                # Verificar si ya existe una alerta pendiente
                existing_alert = InventoryAlert.query.filter_by(
                    product_id=product_id,
                    alert_type=InventoryAlert.ALERT_TYPE_LOW_STOCK,
                    is_resolved=False
                ).first()
                
                if not existing_alert:
                    alert = InventoryAlert(
                        product_id=product_id,
                        alert_type=InventoryAlert.ALERT_TYPE_LOW_STOCK,
                        threshold=product.low_stock_threshold,
                        current_value=product.current_stock,
                        notes=f"Stock bajo detectado tras ajuste de inventario."
                    )
                    db.session.add(alert)
            
            if product.current_stock <= 0:
                # Verificar si ya existe una alerta pendiente
                existing_alert = InventoryAlert.query.filter_by(
                    product_id=product_id,
                    alert_type=InventoryAlert.ALERT_TYPE_STOCK_OUT,
                    is_resolved=False
                ).first()
                
                if not existing_alert:
                    alert = InventoryAlert(
                        product_id=product_id,
                        alert_type=InventoryAlert.ALERT_TYPE_STOCK_OUT,
                        current_value=0,
                        notes=f"Sin stock detectado tras ajuste de inventario."
                    )
                    db.session.add(alert)
            
            db.session.add(adjustment)
            db.session.commit()
            
            flash(f'Ajuste de inventario creado correctamente. Nuevo stock de {product.name}: {product.current_stock}', 'success')
            return redirect(url_for('inventory.adjustments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el ajuste de inventario: {str(e)}', 'danger')
            return redirect(url_for('inventory.new_adjustment'))
    
    # GET request - mostrar formulario
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    return render_template(
        'inventory/new_adjustment.html',
        products=products,
        reasons=InventoryAdjustment.VALID_REASONS
    )


@bp.route('/alerts')
@login_required
def alerts():
    """
    Muestra la lista de alertas de inventario.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filtros
    product_id = request.args.get('product_id', type=int)
    alert_type = request.args.get('alert_type')
    is_resolved = request.args.get('is_resolved')
    
    # Construir query base
    query = InventoryAlert.query
    
    # Aplicar filtros
    if product_id:
        query = query.filter(InventoryAlert.product_id == product_id)
    if alert_type:
        query = query.filter(InventoryAlert.alert_type == alert_type)
    if is_resolved is not None:
        is_resolved = is_resolved.lower() == 'true'
        query = query.filter(InventoryAlert.is_resolved == is_resolved)
    
    # Ordenar y paginar
    alerts = query.order_by(desc(InventoryAlert.alert_datetime)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Obtener productos para filtro
    products = Product.query.order_by(Product.name).all()
    
    return render_template(
        'inventory/alerts.html',
        alerts=alerts,
        products=products,
        filters={
            'product_id': product_id,
            'alert_type': alert_type,
            'is_resolved': is_resolved
        },
        alert_types=InventoryAlert.VALID_ALERT_TYPES
    )


@bp.route('/alert/resolve/<int:alert_id>', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """
    Marca una alerta como resuelta.
    """
    alert = InventoryAlert.query.get_or_404(alert_id)
    
    if alert.is_resolved:
        flash('Esta alerta ya ha sido resuelta', 'warning')
        return redirect(url_for('inventory.alerts'))
    
    notes = request.form.get('resolution_notes')
    
    try:
        alert.resolve(current_user.id, notes)
        db.session.commit()
        flash('Alerta marcada como resuelta correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al resolver la alerta: {str(e)}', 'danger')
    
    return redirect(url_for('inventory.alerts'))


@bp.route('/check-critical-stock')
@login_required
def check_critical_stock():
    """
    Verifica y genera alertas para productos con stock crítico.
    """
    # Obtener productos con stock bajo que no tengan alertas activas
    low_stock_products = db.session.query(Product).filter(
        Product.is_active == True,
        Product.current_stock <= Product.low_stock_threshold,
        Product.current_stock > 0,
        ~Product.id.in_(
            db.session.query(InventoryAlert.product_id).filter(
                InventoryAlert.is_resolved == False,
                InventoryAlert.alert_type == InventoryAlert.ALERT_TYPE_LOW_STOCK
            )
        )
    ).all()
    
    # Obtener productos sin stock que no tengan alertas activas
    out_of_stock_products = db.session.query(Product).filter(
        Product.is_active == True,
        Product.current_stock <= 0,
        ~Product.id.in_(
            db.session.query(InventoryAlert.product_id).filter(
                InventoryAlert.is_resolved == False,
                InventoryAlert.alert_type == InventoryAlert.ALERT_TYPE_STOCK_OUT
            )
        )
    ).all()
    
    # Generar alertas de stock bajo
    for product in low_stock_products:
        alert = InventoryAlert(
            product_id=product.id,
            alert_type=InventoryAlert.ALERT_TYPE_LOW_STOCK,
            threshold=product.low_stock_threshold,
            current_value=product.current_stock,
            notes=f"Stock bajo detectado en verificación programada."
        )
        db.session.add(alert)
    
    # Generar alertas de sin stock
    for product in out_of_stock_products:
        alert = InventoryAlert(
            product_id=product.id,
            alert_type=InventoryAlert.ALERT_TYPE_STOCK_OUT,
            current_value=0,
            notes=f"Sin stock detectado en verificación programada."
        )
        db.session.add(alert)
    
    # Guardar cambios
    if low_stock_products or out_of_stock_products:
        try:
            db.session.commit()
            flash(f'Se generaron {len(low_stock_products)} alertas de stock bajo y {len(out_of_stock_products)} alertas de sin stock', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al generar alertas: {str(e)}', 'danger')
    else:
        flash('No se encontraron productos con stock crítico sin alertas activas', 'info')
    
    return redirect(url_for('inventory.alerts'))


@bp.route('/stock-report')
@login_required
def stock_report():
    """
    Genera un reporte de stock.
    """
    # Filtros
    category_id = request.args.get('category_id', type=int)
    stock_status = request.args.get('stock_status')
    
    # Construir query base
    query = Product.query.filter_by(is_active=True)
    
    # Aplicar filtros
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if stock_status:
        if stock_status == 'low':
            query = query.filter(
                Product.current_stock <= Product.low_stock_threshold,
                Product.current_stock > 0
            )
        elif stock_status == 'out':
            query = query.filter(Product.current_stock <= 0)
        elif stock_status == 'ok':
            query = query.filter(Product.current_stock > Product.low_stock_threshold)
    
    # Ordenar por nombre
    products = query.order_by(Product.name).all()
    
    # Estadísticas para el reporte
    total_products = len(products)
    total_value = sum(float(product.current_stock * product.purchase_price) for product in products)
    low_stock_count = len([p for p in products if p.is_low_stock and p.current_stock > 0])
    out_of_stock_count = len([p for p in products if p.current_stock <= 0])
    
    from app.models.category import Category
    categories = Category.query.order_by(Category.name).all()
    
    return render_template(
        'inventory/stock_report.html',
        products=products,
        categories=categories,
        filters={
            'category_id': category_id,
            'stock_status': stock_status
        },
        stats={
            'total_products': total_products,
            'total_value': total_value,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count
        }
    ) 