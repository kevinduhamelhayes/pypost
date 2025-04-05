"""
Blueprint para las rutas relacionadas con categorías de productos.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.category import Category
from app import db

bp = Blueprint('categories', __name__, url_prefix='/categories')

@bp.route('/')
@login_required
def index():
    """
    Lista todas las categorías.
    
    Returns:
        Plantilla con la lista de categorías renderizada
    """
    # Obtenemos solo las categorías de nivel superior (sin padre)
    root_categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/index.html', categories=root_categories)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """
    Muestra el formulario para crear una nueva categoría y procesa la creación.
    
    Returns:
        GET: Plantilla con formulario para nueva categoría
        POST: Redirección a la lista de categorías después de crear
    """
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        parent_id = request.form.get('parent_id')
        
        if parent_id == '':
            parent_id = None
        elif parent_id:
            parent_id = int(parent_id)
        
        # Validaciones básicas
        if not name:
            flash('El nombre de la categoría es obligatorio', 'danger')
            return render_template('categories/new.html', categories=Category.query.all())
        
        if Category.query.filter_by(name=name).first():
            flash('Ya existe una categoría con ese nombre', 'danger')
            return render_template('categories/new.html', categories=Category.query.all())
        
        # Crear la categoría
        category = Category(
            name=name,
            description=description,
            parent_id=parent_id
        )
        
        db.session.add(category)
        try:
            db.session.commit()
            flash('Categoría creada con éxito', 'success')
            return redirect(url_for('categories.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la categoría: {str(e)}', 'danger')
    
    # Obtener todas las categorías para el selector de categoría padre
    categories = Category.query.all()
    return render_template('categories/new.html', categories=categories)

@bp.route('/<int:id>', methods=['GET'])
@login_required
def show(id):
    """
    Muestra los detalles de una categoría específica y sus subcategorías.
    
    Args:
        id: ID de la categoría a mostrar
        
    Returns:
        Plantilla con los detalles de la categoría
    """
    category = Category.query.get_or_404(id)
    return render_template('categories/show.html', category=category)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Muestra el formulario para editar una categoría y procesa la actualización.
    
    Args:
        id: ID de la categoría a editar
        
    Returns:
        GET: Plantilla con formulario para editar categoría
        POST: Redirección a la lista de categorías después de actualizar
    """
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        parent_id = request.form.get('parent_id')
        is_active = True if request.form.get('is_active') else False
        
        if parent_id == '':
            parent_id = None
        elif parent_id:
            parent_id = int(parent_id)
            
            # Evitar ciclos: una categoría no puede ser padre de sí misma ni de sus padres
            if parent_id == category.id:
                flash('Una categoría no puede ser subcategoría de sí misma', 'danger')
                categories = Category.query.filter(Category.id != category.id).all()
                return render_template('categories/edit.html', category=category, categories=categories)
                
            # Verificar que no se cree un ciclo en la jerarquía
            parent = Category.query.get(parent_id)
            current = parent
            while current and current.parent_id:
                if current.parent_id == category.id:
                    flash('Esto crearía un ciclo en la jerarquía de categorías', 'danger')
                    categories = Category.query.filter(Category.id != category.id).all()
                    return render_template('categories/edit.html', category=category, categories=categories)
                current = current.parent
        
        # Validaciones básicas
        if not name:
            flash('El nombre de la categoría es obligatorio', 'danger')
            categories = Category.query.filter(Category.id != category.id).all()
            return render_template('categories/edit.html', category=category, categories=categories)
        
        # Verificar nombre único, ignorando la categoría actual
        existing = Category.query.filter(Category.name == name, Category.id != category.id).first()
        if existing:
            flash('Ya existe otra categoría con ese nombre', 'danger')
            categories = Category.query.filter(Category.id != category.id).all()
            return render_template('categories/edit.html', category=category, categories=categories)
        
        # Actualizar datos
        category.name = name
        category.description = description
        category.parent_id = parent_id
        category.is_active = is_active
        
        try:
            db.session.commit()
            flash('Categoría actualizada con éxito', 'success')
            return redirect(url_for('categories.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la categoría: {str(e)}', 'danger')
    
    # Obtener todas las categorías excepto la actual y sus hijos para el selector de categoría padre
    categories = Category.query.filter(Category.id != category.id).all()
    return render_template('categories/edit.html', category=category, categories=categories)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    Elimina una categoría de la base de datos.
    
    Args:
        id: ID de la categoría a eliminar
        
    Returns:
        Redirección a la lista de categorías
    """
    category = Category.query.get_or_404(id)
    
    # Verificar si tiene productos asociados
    if category.products:
        flash('No se puede eliminar la categoría porque tiene productos asociados', 'danger')
        return redirect(url_for('categories.index'))
    
    try:
        # Las subcategorías se eliminan automáticamente debido a la opción cascade en la relación
        db.session.delete(category)
        db.session.commit()
        flash('Categoría eliminada con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la categoría: {str(e)}', 'danger')
    
    return redirect(url_for('categories.index'))

# API para usar con AJAX
@bp.route('/api', methods=['GET'])
@login_required
def api_index():
    """
    API que devuelve la lista de categorías en formato JSON.
    
    Returns:
        Lista de categorías en formato JSON
    """
    categories = Category.query.all()
    result = []
    for category in categories:
        result.append({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'parent_id': category.parent_id,
            'full_path': category.full_path,
            'product_count': category.product_count
        })
    return jsonify(result)

@bp.route('/api/<int:id>', methods=['GET'])
@login_required
def api_show(id):
    """
    API que devuelve una categoría específica en formato JSON.
    
    Args:
        id: ID de la categoría a devolver
        
    Returns:
        Datos de la categoría en formato JSON
    """
    category = Category.query.get_or_404(id)
    return jsonify(category.to_dict()) 