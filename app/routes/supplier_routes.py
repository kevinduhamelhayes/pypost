"""
Rutas para la gestión de proveedores en PyPOS Local.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.supplier import Supplier
from sqlalchemy import desc

bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')


@bp.route('/')
@login_required
def index():
    """
    Muestra la lista de proveedores.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filtros
    search = request.args.get('search', '')
    is_active = request.args.get('is_active')
    
    # Construir query base
    query = Supplier.query
    
    # Aplicar filtros
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Supplier.name.ilike(search_term)) |
            (Supplier.contact_person.ilike(search_term)) |
            (Supplier.email.ilike(search_term)) |
            (Supplier.phone.ilike(search_term)) |
            (Supplier.tax_id.ilike(search_term))
        )
    
    if is_active is not None:
        is_active = is_active.lower() == 'true'
        query = query.filter(Supplier.is_active == is_active)
    
    # Ordenar y paginar
    suppliers = query.order_by(Supplier.name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template(
        'suppliers/index.html',
        suppliers=suppliers,
        search=search,
        is_active=is_active
    )


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Crea un nuevo proveedor.
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        tax_id = request.form.get('tax_id')
        notes = request.form.get('notes')
        payment_terms = request.form.get('payment_terms')
        lead_time = request.form.get('lead_time', type=int)
        is_active = 'is_active' in request.form
        
        # Validaciones
        if not name:
            flash('El nombre del proveedor es obligatorio', 'danger')
            return redirect(url_for('suppliers.create'))
        
        # Verificar si ya existe un proveedor con el mismo nombre
        existing_supplier = Supplier.query.filter(Supplier.name == name).first()
        if existing_supplier:
            flash('Ya existe un proveedor con ese nombre', 'warning')
            return redirect(url_for('suppliers.create'))
        
        # Crear proveedor
        try:
            supplier = Supplier(
                name=name,
                contact_person=contact_person,
                email=email,
                phone=phone,
                address=address,
                tax_id=tax_id,
                notes=notes,
                payment_terms=payment_terms,
                lead_time=lead_time,
                is_active=is_active
            )
            
            db.session.add(supplier)
            db.session.commit()
            
            flash(f'Proveedor "{name}" creado correctamente', 'success')
            return redirect(url_for('suppliers.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el proveedor: {str(e)}', 'danger')
            return redirect(url_for('suppliers.create'))
    
    # GET request - mostrar formulario
    return render_template('suppliers/create.html')


@bp.route('/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit(supplier_id):
    """
    Edita un proveedor existente.
    """
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        tax_id = request.form.get('tax_id')
        notes = request.form.get('notes')
        payment_terms = request.form.get('payment_terms')
        lead_time = request.form.get('lead_time', type=int)
        is_active = 'is_active' in request.form
        
        # Validaciones
        if not name:
            flash('El nombre del proveedor es obligatorio', 'danger')
            return redirect(url_for('suppliers.edit', supplier_id=supplier_id))
        
        # Verificar si ya existe otro proveedor con el mismo nombre
        existing_supplier = Supplier.query.filter(
            Supplier.name == name,
            Supplier.id != supplier_id
        ).first()
        if existing_supplier:
            flash('Ya existe otro proveedor con ese nombre', 'warning')
            return redirect(url_for('suppliers.edit', supplier_id=supplier_id))
        
        # Actualizar proveedor
        try:
            supplier.name = name
            supplier.contact_person = contact_person
            supplier.email = email
            supplier.phone = phone
            supplier.address = address
            supplier.tax_id = tax_id
            supplier.notes = notes
            supplier.payment_terms = payment_terms
            supplier.lead_time = lead_time
            supplier.is_active = is_active
            
            db.session.commit()
            
            flash(f'Proveedor "{name}" actualizado correctamente', 'success')
            return redirect(url_for('suppliers.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el proveedor: {str(e)}', 'danger')
            return redirect(url_for('suppliers.edit', supplier_id=supplier_id))
    
    # GET request - mostrar formulario
    return render_template('suppliers/edit.html', supplier=supplier)


@bp.route('/view/<int:supplier_id>')
@login_required
def view(supplier_id):
    """
    Muestra los detalles de un proveedor.
    """
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Obtener estadísticas
    from app.models.purchase_order import PurchaseOrder
    
    # Órdenes de compra recientes
    recent_orders = PurchaseOrder.query.filter_by(
        supplier_id=supplier_id
    ).order_by(desc(PurchaseOrder.order_date)).limit(5).all()
    
    # Total de órdenes
    total_orders = PurchaseOrder.query.filter_by(supplier_id=supplier_id).count()
    
    return render_template(
        'suppliers/view.html',
        supplier=supplier,
        recent_orders=recent_orders,
        total_orders=total_orders
    )


@bp.route('/toggle-status/<int:supplier_id>', methods=['POST'])
@login_required
def toggle_status(supplier_id):
    """
    Cambia el estado de un proveedor (activo/inactivo).
    """
    supplier = Supplier.query.get_or_404(supplier_id)
    
    try:
        supplier.is_active = not supplier.is_active
        db.session.commit()
        
        status = "activado" if supplier.is_active else "desactivado"
        flash(f'Proveedor "{supplier.name}" {status} correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado del proveedor: {str(e)}', 'danger')
    
    return redirect(url_for('suppliers.index')) 