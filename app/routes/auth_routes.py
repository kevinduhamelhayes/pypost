"""
Blueprint para las rutas de autenticación y gestión de usuarios.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta para iniciar sesión.
    
    Returns:
        GET: Plantilla con formulario de login
        POST: Redirección a la página principal después de iniciar sesión
    """
    # Si el usuario ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('home.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Buscar al usuario por nombre de usuario
        user = User.query.filter_by(username=username).first()
        
        # Verificar si el usuario existe y la contraseña es correcta
        if not user or not user.check_password(password):
            flash('Por favor verifica tus credenciales e intenta nuevamente.', 'danger')
            return render_template('auth/login.html')
        
        # Verificar si el usuario está activo
        if not user.is_active:
            flash('Esta cuenta ha sido desactivada. Contacta al administrador.', 'warning')
            return render_template('auth/login.html')
        
        # Iniciar sesión y actualizar último acceso
        login_user(user, remember=remember)
        user.update_last_login()
        
        flash(f'Bienvenido/a, {user.username}!', 'success')
        
        # Redirigir a la página que intentaba acceder o al dashboard
        next_page = request.args.get('next')
        return redirect(next_page or url_for('home.dashboard'))
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Ruta para registrar un nuevo usuario.
    
    Returns:
        GET: Plantilla con formulario de registro
        POST: Redirección a la página de login después de registrarse
    """
    # Si el usuario ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('home.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        full_name = request.form.get('full_name', '')
        
        # Validaciones básicas
        if not username or not email or not password:
            flash('Todos los campos marcados con * son obligatorios.', 'danger')
            return render_template('auth/register.html')
        
        if password != password_confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/register.html')
        
        # Verificar si el usuario o email ya existen
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'danger')
            return render_template('auth/register.html')
        
        # Crear el nuevo usuario (por defecto como cajero)
        user = User(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role='cashier'  # Por defecto todos los usuarios nuevos son cajeros
        )
        
        db.session.add(user)
        try:
            db.session.commit()
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar usuario: {str(e)}', 'danger')
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    """
    Ruta para cerrar sesión.
    
    Returns:
        Redirección a la página de login
    """
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Ruta para ver y editar el perfil del usuario.
    
    Returns:
        GET: Plantilla con el perfil del usuario
        POST: Redirección al perfil después de actualizar
    """
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        password_confirm = request.form.get('password_confirm')
        
        # Verificar si el email ya existe para otro usuario
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('El email ya está en uso por otro usuario.', 'danger')
            return render_template('auth/profile.html')
        
        # Actualizar datos básicos
        current_user.full_name = full_name
        current_user.email = email
        
        # Si se proporciona una nueva contraseña, verificar y actualizar
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('La contraseña actual es incorrecta.', 'danger')
                return render_template('auth/profile.html')
            
            if new_password != password_confirm:
                flash('La nueva contraseña y su confirmación no coinciden.', 'danger')
                return render_template('auth/profile.html')
            
            current_user.set_password(new_password)
            flash('Contraseña actualizada correctamente.', 'success')
        
        try:
            db.session.commit()
            flash('Perfil actualizado correctamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar perfil: {str(e)}', 'danger')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')

# Rutas de administración de usuarios (solo para administradores)
@bp.route('/users', methods=['GET'])
@login_required
def users_list():
    """
    Ruta para listar todos los usuarios (solo admin).
    
    Returns:
        Plantilla con la lista de usuarios
    """
    if not current_user.is_admin:
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('home.dashboard'))
    
    users = User.query.all()
    return render_template('auth/users_list.html', users=users)

@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def user_edit(id):
    """
    Ruta para editar un usuario (solo admin).
    
    Args:
        id: ID del usuario a editar
        
    Returns:
        GET: Plantilla con formulario para editar usuario
        POST: Redirección a la lista de usuarios después de actualizar
    """
    if not current_user.is_admin:
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('home.dashboard'))
    
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name', '')
        role = request.form.get('role')
        is_active = True if request.form.get('is_active') else False
        new_password = request.form.get('new_password')
        
        # Verificar si el nombre de usuario o email ya existen para otro usuario
        if username != user.username and User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return render_template('auth/user_edit.html', user=user)
        
        if email != user.email and User.query.filter_by(email=email).first():
            flash('El email ya está en uso.', 'danger')
            return render_template('auth/user_edit.html', user=user)
        
        # Actualizar datos
        user.username = username
        user.email = email
        user.full_name = full_name
        user.role = role
        user.is_active = is_active
        
        # Si se proporciona una nueva contraseña, actualizarla
        if new_password:
            user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('Usuario actualizado correctamente.', 'success')
            return redirect(url_for('auth.users_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'danger')
    
    return render_template('auth/user_edit.html', user=user)

@bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
def user_delete(id):
    """
    Ruta para eliminar un usuario (solo admin).
    
    Args:
        id: ID del usuario a eliminar
        
    Returns:
        Redirección a la lista de usuarios
    """
    if not current_user.is_admin:
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('home.dashboard'))
    
    user = User.query.get_or_404(id)
    
    # No permitir eliminar el propio usuario
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('auth.users_list'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar usuario: {str(e)}', 'danger')
    
    return redirect(url_for('auth.users_list')) 