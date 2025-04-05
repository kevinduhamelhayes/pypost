"""
Blueprint para las rutas relacionadas con la gestión de clientes.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.customer import Customer
from app.models.sale import Sale
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('customers', __name__, url_prefix='/customers')

@bp.route('/')
@login_required
def index():
    """
    Muestra la lista de clientes.
    
    Returns:
        Plantilla con la lista de clientes
    """
    # Obtener parámetros de búsqueda y paginación
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Consultar clientes
    query = Customer.query
    
    # Aplicar filtro de búsqueda si existe
    if search:
        query = query.filter(
            (Customer.name.ilike(f'%{search}%')) |
            (Customer.document.ilike(f'%{search}%')) |
            (Customer.email.ilike(f'%{search}%')) |
            (Customer.phone.ilike(f'%{search}%'))
        )
    
    # Ordenar por nombre
    query = query.order_by(Customer.name)
    
    # Paginar resultados
    customers = query.paginate(page=page, per_page=per_page)
    
    return render_template('customers/index.html', customers=customers, search=search)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Crea un nuevo cliente.
    
    Returns:
        GET: Plantilla con formulario para crear cliente
        POST: Redirección a la lista de clientes
    """
    if request.method == 'POST':
        try:
            # Validar datos obligatorios
            name = request.form.get('name')
            if not name:
                flash('El nombre es obligatorio.', 'danger')
                return render_template('customers/create.html')
            
            # Validar si ya existe un cliente con el mismo documento
            document = request.form.get('document')
            if document:
                existing = Customer.query.filter_by(document=document).first()
                if existing:
                    flash('Ya existe un cliente con ese documento.', 'danger')
                    return render_template('customers/create.html')
            
            # Validar email único
            email = request.form.get('email')
            if email:
                existing = Customer.query.filter_by(email=email).first()
                if existing:
                    flash('Ya existe un cliente con ese email.', 'danger')
                    return render_template('customers/create.html')
            
            # Crear el cliente
            customer = Customer(
                name=name,
                document=document,
                document_type=request.form.get('document_type', 'dni'),
                email=email,
                phone=request.form.get('phone', ''),
                address=request.form.get('address', ''),
                notes=request.form.get('notes', ''),
                created_by=current_user.id
            )
            
            db.session.add(customer)
            db.session.commit()
            
            flash('Cliente creado correctamente.', 'success')
            return redirect(url_for('customers.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el cliente: {str(e)}', 'danger')
            return render_template('customers/create.html')
    
    return render_template('customers/create.html')

@bp.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    """
    Edita un cliente existente.
    
    Args:
        customer_id: ID del cliente a editar
        
    Returns:
        GET: Plantilla con formulario para editar cliente
        POST: Redirección a la lista de clientes
    """
    # Obtener el cliente
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        try:
            # Validar datos obligatorios
            name = request.form.get('name')
            if not name:
                flash('El nombre es obligatorio.', 'danger')
                return render_template('customers/edit.html', customer=customer)
            
            # Validar si ya existe otro cliente con el mismo documento
            document = request.form.get('document')
            if document:
                existing = Customer.query.filter(
                    Customer.document == document,
                    Customer.id != customer_id
                ).first()
                if existing:
                    flash('Ya existe otro cliente con ese documento.', 'danger')
                    return render_template('customers/edit.html', customer=customer)
            
            # Validar email único
            email = request.form.get('email')
            if email:
                existing = Customer.query.filter(
                    Customer.email == email,
                    Customer.id != customer_id
                ).first()
                if existing:
                    flash('Ya existe otro cliente con ese email.', 'danger')
                    return render_template('customers/edit.html', customer=customer)
            
            # Actualizar el cliente
            customer.name = name
            customer.document = document
            customer.document_type = request.form.get('document_type', 'dni')
            customer.email = email
            customer.phone = request.form.get('phone', '')
            customer.address = request.form.get('address', '')
            customer.notes = request.form.get('notes', '')
            customer.is_active = 'is_active' in request.form
            
            db.session.commit()
            
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('customers.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el cliente: {str(e)}', 'danger')
            return render_template('customers/edit.html', customer=customer)
    
    return render_template('customers/edit.html', customer=customer)

@bp.route('/view/<int:customer_id>')
@login_required
def view(customer_id):
    """
    Muestra los detalles de un cliente y su historial de compras.
    
    Args:
        customer_id: ID del cliente a mostrar
        
    Returns:
        Plantilla con los detalles del cliente
    """
    # Obtener el cliente
    customer = Customer.query.get_or_404(customer_id)
    
    # Obtener historial de ventas del cliente
    sales = Sale.query.filter_by(customer_id=customer_id).order_by(Sale.sale_datetime.desc()).all()
    
    # Calcular estadísticas
    total_spent = sum(sale.final_amount for sale in sales if sale.status == 'completed')
    
    # Obtener productos más comprados
    product_stats = {}
    for sale in sales:
        if sale.status != 'completed':
            continue
        for item in sale.items:
            if item.product_id in product_stats:
                product_stats[item.product_id]['quantity'] += item.quantity
                product_stats[item.product_id]['amount'] += item.subtotal
            else:
                product_stats[item.product_id] = {
                    'name': item.product.name,
                    'quantity': item.quantity,
                    'amount': item.subtotal
                }
    
    # Convertir a lista y ordenar por cantidad
    top_products = sorted(
        [{'product_id': k, **v} for k, v in product_stats.items()],
        key=lambda x: x['quantity'],
        reverse=True
    )[:5]  # Top 5 productos
    
    return render_template('customers/view.html', 
                          customer=customer, 
                          sales=sales, 
                          total_spent=total_spent,
                          top_products=top_products)

@bp.route('/search')
@login_required
def search():
    """
    Busca clientes para asociar a una venta.
    
    Returns:
        JSON con los clientes encontrados
    """
    query = request.args.get('query', '')
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Buscar por nombre, documento, email o teléfono
    customers = Customer.query.filter(
        (Customer.name.ilike(f'%{query}%')) |
        (Customer.document.ilike(f'%{query}%')) |
        (Customer.email.ilike(f'%{query}%')) |
        (Customer.phone.ilike(f'%{query}%'))
    ).filter_by(is_active=True).limit(10).all()
    
    # Convertir a formato JSON
    result = []
    for customer in customers:
        result.append({
            'id': customer.id,
            'name': customer.name,
            'document': customer.document,
            'email': customer.email,
            'phone': customer.phone
        })
    
    return jsonify(result)

@bp.route('/toggle-status/<int:customer_id>', methods=['POST'])
@login_required
def toggle_status(customer_id):
    """
    Activa o desactiva un cliente.
    
    Args:
        customer_id: ID del cliente a modificar
        
    Returns:
        Redirección a la lista de clientes
    """
    # Obtener el cliente
    customer = Customer.query.get_or_404(customer_id)
    
    try:
        # Cambiar estado
        customer.is_active = not customer.is_active
        
        db.session.commit()
        
        status = 'activado' if customer.is_active else 'desactivado'
        flash(f'Cliente {status} correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado del cliente: {str(e)}', 'danger')
    
    return redirect(url_for('customers.index'))

@bp.route('/report')
@login_required
def report():
    """
    Genera un reporte de clientes por período.
    
    Returns:
        Plantilla con el reporte de clientes
    """
    # Obtener período del reporte
    period = request.args.get('period', 'all')
    start_date = None
    
    if period == 'month':
        start_date = datetime.now() - timedelta(days=30)
    elif period == 'quarter':
        start_date = datetime.now() - timedelta(days=90)
    elif period == 'year':
        start_date = datetime.now() - timedelta(days=365)
    
    # Consultar clientes
    query = Customer.query
    
    # Filtrar por fecha de creación si aplica
    if start_date:
        query = query.filter(Customer.created_at >= start_date)
    
    # Ordenar por fecha de creación descendente
    customers = query.order_by(Customer.created_at.desc()).all()
    
    # Calcular estadísticas
    stats = {
        'total_customers': len(customers),
        'active_customers': len([c for c in customers if c.is_active]),
        'inactive_customers': len([c for c in customers if not c.is_active])
    }
    
    # Para clientes con más compras, necesitamos consultar las ventas
    top_customers = []
    if customers:
        # Consultar las ventas por cliente
        customer_sales = db.session.query(
            Sale.customer_id,
            func.count(Sale.id).label('sale_count'),
            func.sum(Sale.final_amount).label('total_amount')
        ).filter(
            Sale.customer_id.isnot(None),
            Sale.status == 'completed'
        ).group_by(Sale.customer_id).order_by(
            func.sum(Sale.final_amount).desc()
        ).limit(10).all()
        
        # Obtener datos de clientes
        for cs in customer_sales:
            customer = Customer.query.get(cs.customer_id)
            if customer:
                top_customers.append({
                    'id': customer.id,
                    'name': customer.name,
                    'sale_count': cs.sale_count,
                    'total_amount': cs.total_amount
                })
    
    return render_template('customers/report.html', 
                          customers=customers, 
                          stats=stats, 
                          period=period,
                          top_customers=top_customers) 