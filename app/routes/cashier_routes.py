"""
Blueprint para las rutas relacionadas con sesiones de caja (apertura y cierre).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.cashier_session import CashierSession
from app.models.sale import Sale
from app import db
from datetime import datetime, timedelta
from decimal import Decimal

bp = Blueprint('cashier', __name__, url_prefix='/cashier')

@bp.route('/')
@login_required
def index():
    """
    Muestra la lista de sesiones de caja del usuario actual.
    
    Returns:
        Plantilla con la lista de sesiones de caja
    """
    # Obtener las sesiones de caja del usuario actual
    sessions = CashierSession.query.filter_by(user_id=current_user.id).order_by(CashierSession.open_time.desc()).all()
    
    # Verificar si hay una sesión abierta actualmente
    current_session = CashierSession.get_current_session(current_user.id)
    
    return render_template('cashier/index.html', sessions=sessions, current_session=current_session)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_session():
    """
    Crea una nueva sesión de caja.
    
    Returns:
        GET: Plantilla con formulario para abrir sesión
        POST: Redirección a la vista principal del POS
    """
    # Verificar si ya hay una sesión abierta para el usuario actual
    current_session = CashierSession.get_current_session(current_user.id)
    if current_session:
        flash('Ya tiene una sesión de caja abierta. Cierre la sesión actual antes de abrir una nueva.', 'warning')
        return redirect(url_for('pos.index'))
    
    if request.method == 'POST':
        try:
            # Obtener monto inicial
            initial_cash = Decimal(request.form.get('initial_cash', 0))
            if initial_cash < 0:
                flash('El monto inicial no puede ser negativo.', 'danger')
                return render_template('cashier/new.html')
            
            # Crear la sesión
            session = CashierSession(
                user_id=current_user.id,
                initial_cash=initial_cash,
                notes=request.form.get('notes', '')
            )
            
            db.session.add(session)
            db.session.commit()
            
            flash('Sesión de caja abierta correctamente.', 'success')
            return redirect(url_for('pos.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al abrir la sesión: {str(e)}', 'danger')
            return render_template('cashier/new.html')
    
    return render_template('cashier/new.html')

@bp.route('/close/<int:session_id>', methods=['GET', 'POST'])
@login_required
def close_session(session_id):
    """
    Cierra una sesión de caja.
    
    Args:
        session_id: ID de la sesión a cerrar
        
    Returns:
        GET: Plantilla con formulario para cerrar sesión
        POST: Redirección a la lista de sesiones
    """
    # Obtener la sesión
    session = CashierSession.query.get_or_404(session_id)
    
    # Verificar que la sesión pertenece al usuario actual
    if session.user_id != current_user.id and not current_user.is_admin:
        flash('No tiene permiso para cerrar esta sesión.', 'danger')
        return redirect(url_for('cashier.index'))
    
    # Verificar que la sesión esté abierta
    if session.close_time:
        flash('Esta sesión ya ha sido cerrada.', 'warning')
        return redirect(url_for('cashier.index'))
    
    # Calcular ventas y totales de la sesión
    sales = Sale.query.filter_by(session_id=session.id).all()
    total_sales = sum(sale.final_amount for sale in sales if sale.status == 'completed')
    expected_cash = session.initial_cash + sum(
        sale.final_amount for sale in sales 
        if sale.status == 'completed' and sale.payment_method == 'cash'
    )
    
    if request.method == 'POST':
        try:
            # Obtener monto final
            final_cash = Decimal(request.form.get('final_cash', 0))
            if final_cash < 0:
                flash('El monto final no puede ser negativo.', 'danger')
                return render_template('cashier/close.html', session=session, total_sales=total_sales, expected_cash=expected_cash, sales_count=len(sales))
            
            # Calcular diferencia
            cash_difference = final_cash - expected_cash
            
            # Cerrar la sesión
            session.close_session(
                final_cash=final_cash,
                notes=request.form.get('notes', '')
            )
            
            db.session.commit()
            
            flash('Sesión de caja cerrada correctamente.', 'success')
            return redirect(url_for('cashier.details', session_id=session.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al cerrar la sesión: {str(e)}', 'danger')
            return render_template('cashier/close.html', session=session, total_sales=total_sales, expected_cash=expected_cash, sales_count=len(sales))
    
    return render_template('cashier/close.html', session=session, total_sales=total_sales, expected_cash=expected_cash, sales_count=len(sales))

@bp.route('/details/<int:session_id>')
@login_required
def details(session_id):
    """
    Muestra los detalles de una sesión de caja.
    
    Args:
        session_id: ID de la sesión a mostrar
        
    Returns:
        Plantilla con los detalles de la sesión
    """
    # Obtener la sesión
    session = CashierSession.query.get_or_404(session_id)
    
    # Verificar que la sesión pertenece al usuario actual o es admin
    if session.user_id != current_user.id and not current_user.is_admin:
        flash('No tiene permiso para ver esta sesión.', 'danger')
        return redirect(url_for('cashier.index'))
    
    # Obtener ventas de la sesión
    sales = Sale.query.filter_by(session_id=session.id).order_by(Sale.sale_datetime.desc()).all()
    
    # Calcular estadísticas
    stats = {
        'total_sales': sum(sale.final_amount for sale in sales if sale.status == 'completed'),
        'sales_count': len([s for s in sales if s.status == 'completed']),
        'cash_sales': sum(sale.final_amount for sale in sales if sale.status == 'completed' and sale.payment_method == 'cash'),
        'card_sales': sum(sale.final_amount for sale in sales if sale.status == 'completed' and sale.payment_method == 'card'),
        'transfer_sales': sum(sale.final_amount for sale in sales if sale.status == 'completed' and sale.payment_method == 'transfer'),
        'other_sales': sum(sale.final_amount for sale in sales if sale.status == 'completed' and sale.payment_method not in ['cash', 'card', 'transfer']),
        'cancelled_sales': len([s for s in sales if s.status == 'cancelled'])
    }
    
    return render_template('cashier/details.html', session=session, sales=sales, stats=stats)

@bp.route('/report')
@login_required
def report():
    """
    Genera un reporte de sesiones de caja por período.
    
    Returns:
        Plantilla con el reporte de sesiones de caja
    """
    # Obtener período del reporte
    period = request.args.get('period', 'today')
    start_date = None
    end_date = datetime.now()
    
    if period == 'today':
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'yesterday':
        start_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = (datetime.now() - timedelta(days=7))
    elif period == 'month':
        start_date = (datetime.now() - timedelta(days=30))
    
    # Si se proporcionan fechas específicas
    custom_start = request.args.get('start_date')
    custom_end = request.args.get('end_date')
    
    if custom_start:
        try:
            start_date = datetime.strptime(custom_start, '%Y-%m-%d')
        except ValueError:
            flash('Formato de fecha inválido para fecha inicial.', 'warning')
    
    if custom_end:
        try:
            end_date = datetime.strptime(custom_end + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        except ValueError:
            flash('Formato de fecha inválido para fecha final.', 'warning')
    
    # Consultar sesiones dentro del rango de fechas
    query = CashierSession.query
    
    # Filtrar por usuario si no es admin
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    
    # Filtrar por fechas
    if start_date:
        query = query.filter(CashierSession.open_time >= start_date)
    if end_date:
        query = query.filter(CashierSession.open_time <= end_date)
    
    # Ordenar por fecha de apertura descendente
    sessions = query.order_by(CashierSession.open_time.desc()).all()
    
    # Calcular estadísticas agregadas
    total_initial = sum(session.initial_cash for session in sessions)
    total_final = sum(session.final_cash for session in sessions if session.final_cash is not None)
    total_difference = sum(session.cash_difference for session in sessions if session.cash_difference is not None)
    
    stats = {
        'total_sessions': len(sessions),
        'closed_sessions': len([s for s in sessions if s.close_time is not None]),
        'open_sessions': len([s for s in sessions if s.close_time is None]),
        'total_initial': total_initial,
        'total_final': total_final,
        'total_difference': total_difference
    }
    
    return render_template('cashier/report.html', 
                          sessions=sessions, 
                          stats=stats, 
                          period=period,
                          start_date=start_date,
                          end_date=end_date) 