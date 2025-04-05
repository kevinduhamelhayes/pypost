"""
Blueprint para las rutas relacionadas con productos.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models.product import Product
from app import db

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('/')
@login_required
def index():
    """
    Lista todos los productos.
    
    Returns:
        Plantilla con la lista de productos renderizada
    """
    products = Product.query.all()
    return render_template('products/index.html', products=products)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """
    Muestra el formulario para crear un nuevo producto y procesa la creación.
    
    Returns:
        GET: Plantilla con formulario para nuevo producto
        POST: Redirección a la lista de productos después de crear
    """
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        sku = request.form.get('sku', '')
        barcode = request.form.get('barcode', '')
        try:
            purchase_price = float(request.form.get('purchase_price', 0))
        except ValueError:
            purchase_price = 0.0
        try:
            sale_price = float(request.form.get('sale_price'))
        except ValueError:
            flash('El precio de venta debe ser un número válido', 'error')
            return render_template('products/new.html')
        
        try:
            current_stock = int(request.form.get('current_stock', 0))
        except ValueError:
            current_stock = 0
            
        # Validaciones básicas
        if not name:
            flash('El nombre del producto es obligatorio', 'error')
            return render_template('products/new.html')
        
        if sale_price <= 0:
            flash('El precio de venta debe ser mayor que cero', 'error')
            return render_template('products/new.html')
        
        # Crear el producto
        product = Product(
            name=name,
            description=description,
            sku=sku,
            barcode=barcode,
            purchase_price=purchase_price,
            sale_price=sale_price,
            current_stock=current_stock
        )
        
        db.session.add(product)
        try:
            db.session.commit()
            flash('Producto creado con éxito', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el producto: {str(e)}', 'error')
    
    return render_template('products/new.html')

@bp.route('/<int:id>', methods=['GET'])
@login_required
def show(id):
    """
    Muestra los detalles de un producto específico.
    
    Args:
        id: ID del producto a mostrar
        
    Returns:
        Plantilla con los detalles del producto
    """
    product = Product.query.get_or_404(id)
    return render_template('products/show.html', product=product)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Muestra el formulario para editar un producto y procesa la actualización.
    
    Args:
        id: ID del producto a editar
        
    Returns:
        GET: Plantilla con formulario para editar producto
        POST: Redirección a la lista de productos después de actualizar
    """
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description', '')
        product.sku = request.form.get('sku', '')
        product.barcode = request.form.get('barcode', '')
        
        try:
            product.purchase_price = float(request.form.get('purchase_price', 0))
        except ValueError:
            product.purchase_price = 0.0
            
        try:
            product.sale_price = float(request.form.get('sale_price'))
        except ValueError:
            flash('El precio de venta debe ser un número válido', 'error')
            return render_template('products/edit.html', product=product)
        
        try:
            product.current_stock = int(request.form.get('current_stock', 0))
        except ValueError:
            product.current_stock = 0
            
        # Validaciones básicas
        if not product.name:
            flash('El nombre del producto es obligatorio', 'error')
            return render_template('products/edit.html', product=product)
        
        if product.sale_price <= 0:
            flash('El precio de venta debe ser mayor que cero', 'error')
            return render_template('products/edit.html', product=product)
        
        try:
            db.session.commit()
            flash('Producto actualizado con éxito', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el producto: {str(e)}', 'error')
    
    return render_template('products/edit.html', product=product)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    Elimina un producto de la base de datos.
    
    Args:
        id: ID del producto a eliminar
        
    Returns:
        Redirección a la lista de productos
    """
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Producto eliminado con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
    
    return redirect(url_for('products.index'))

# API para usar con AJAX
@bp.route('/api', methods=['GET'])
@login_required
def api_index():
    """
    API que devuelve la lista de productos en formato JSON.
    
    Returns:
        Lista de productos en formato JSON
    """
    products = Product.query.all()
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'barcode': product.barcode,
            'purchase_price': float(product.purchase_price),
            'sale_price': float(product.sale_price),
            'current_stock': product.current_stock
        })
    return jsonify(result)

@bp.route('/api/<int:id>', methods=['GET'])
@login_required
def api_show(id):
    """
    API que devuelve un producto específico en formato JSON.
    
    Args:
        id: ID del producto a devolver
        
    Returns:
        Datos del producto en formato JSON
    """
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'sku': product.sku,
        'barcode': product.barcode,
        'purchase_price': float(product.purchase_price),
        'sale_price': float(product.sale_price),
        'current_stock': product.current_stock
    }) 