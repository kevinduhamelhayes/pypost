from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from app.models import User, Category, Product, Sale, SaleItem, InventoryAdjustment
from app import db
import pandas as pd
import io
import json

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
def index():
    """Vista principal de informes."""
    users = User.query.all()
    categories = Category.query.all()
    return render_template('reports/index.html',
                         users=users,
                         categories=categories)

@bp.route('/data')
@login_required
def get_report_data():
    """Obtiene los datos para los informes según los filtros aplicados."""
    try:
        # Procesar filtros
        date_range = request.args.get('dateRange', '')
        user_id = request.args.get('user', '')
        category_id = request.args.get('category', '')
        
        # Parsear rango de fechas
        if date_range:
            start_date, end_date = date_range.split(' - ')
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y') + timedelta(days=1)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        
        # Query base para ventas
        sales_query = Sale.query.filter(Sale.date.between(start_date, end_date))
        if user_id:
            sales_query = sales_query.filter(Sale.user_id == user_id)
        
        # Query base para items vendidos
        items_query = db.session.query(
            SaleItem, Product, Category
        ).join(
            Sale, SaleItem.sale_id == Sale.id
        ).join(
            Product, SaleItem.product_id == Product.id
        ).join(
            Category, Product.category_id == Category.id
        ).filter(
            Sale.date.between(start_date, end_date)
        )
        
        if category_id:
            items_query = items_query.filter(Product.category_id == category_id)
        if user_id:
            items_query = items_query.filter(Sale.user_id == user_id)
        
        # Calcular estadísticas generales
        sales = sales_query.all()
        total_sales = sum(sale.total for sale in sales)
        sales_count = len(sales)
        
        items = items_query.all()
        total_products = sum(item[0].quantity for item in items)
        total_cost = sum(item[0].quantity * item[1].purchase_price for item in items)
        
        # Calcular ventas por período
        sales_by_date = db.session.query(
            func.date(Sale.date),
            func.sum(Sale.total)
        ).filter(
            Sale.date.between(start_date, end_date)
        ).group_by(
            func.date(Sale.date)
        ).all()
        
        # Calcular ventas por categoría
        sales_by_category = db.session.query(
            Category.name,
            func.sum(SaleItem.quantity * SaleItem.unit_price)
        ).join(
            Product, SaleItem.product_id == Product.id
        ).join(
            Category, Product.category_id == Category.id
        ).join(
            Sale, SaleItem.sale_id == Sale.id
        ).filter(
            Sale.date.between(start_date, end_date)
        ).group_by(
            Category.name
        ).all()
        
        # Obtener productos más vendidos
        top_products = db.session.query(
            Product,
            func.sum(SaleItem.quantity).label('total_quantity'),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label('total_sales')
        ).join(
            SaleItem, Product.id == SaleItem.product_id
        ).join(
            Sale, SaleItem.sale_id == Sale.id
        ).filter(
            Sale.date.between(start_date, end_date)
        ).group_by(
            Product
        ).order_by(
            desc('total_quantity')
        ).limit(10).all()
        
        # Contar productos con stock bajo
        low_stock_count = Product.query.filter(
            Product.current_stock <= Product.low_stock_threshold
        ).count()
        
        # Preparar datos para la respuesta
        response = {
            'totalSales': total_sales,
            'salesCount': sales_count,
            'totalProducts': total_products,
            'avgTicket': total_sales / sales_count if sales_count > 0 else 0,
            'totalProfit': total_sales - total_cost,
            'profitMargin': ((total_sales - total_cost) / total_sales * 100) if total_sales > 0 else 0,
            'lowStockCount': low_stock_count,
            'salesChart': {
                'labels': [str(date[0]) for date in sales_by_date],
                'data': [float(total) for _, total in sales_by_date]
            },
            'categoryChart': {
                'labels': [cat for cat, _ in sales_by_category],
                'data': [float(total) for _, total in sales_by_category]
            },
            'topProducts': [{
                'name': product.name,
                'category': product.category.name,
                'quantity': int(quantity),
                'total': float(total),
                'stock': product.current_stock,
                'lastMovement': product.last_updated.strftime('%d/%m/%Y %H:%M')
            } for product, quantity, total in top_products]
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@bp.route('/export')
@login_required
def export_data():
    """Exporta los datos del reporte en varios formatos."""
    try:
        # Obtener parámetros
        format = request.args.get('format', 'csv')
        date_range = request.args.get('dateRange', '')
        user_id = request.args.get('user', '')
        category_id = request.args.get('category', '')
        
        # Parsear rango de fechas
        if date_range:
            start_date, end_date = date_range.split(' - ')
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y') + timedelta(days=1)
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        
        # Construir query
        query = db.session.query(
            Product.name.label('Producto'),
            Category.name.label('Categoría'),
            func.sum(SaleItem.quantity).label('Unidades Vendidas'),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label('Total Ventas'),
            Product.current_stock.label('Stock Actual'),
            Product.last_updated.label('Último Movimiento')
        ).join(
            SaleItem, Product.id == SaleItem.product_id
        ).join(
            Sale, SaleItem.sale_id == Sale.id
        ).join(
            Category, Product.category_id == Category.id
        ).filter(
            Sale.date.between(start_date, end_date)
        )
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if user_id:
            query = query.filter(Sale.user_id == user_id)
        
        query = query.group_by(Product.id, Category.name)
        
        # Convertir a DataFrame
        df = pd.read_sql(query.statement, db.session.bind)
        
        # Formatear columnas
        df['Total Ventas'] = df['Total Ventas'].apply(lambda x: f'${x:,.2f}')
        df['Último Movimiento'] = pd.to_datetime(df['Último Movimiento']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Preparar archivo para descarga
        buffer = io.BytesIO()
        
        if format == 'csv':
            df.to_csv(buffer, index=False, encoding='utf-8')
            mimetype = 'text/csv'
            filename = 'reporte_ventas.csv'
        elif format == 'excel':
            df.to_excel(buffer, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'reporte_ventas.xlsx'
        else:  # PDF
            # Crear PDF con reportlab
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            # Convertir DataFrame a lista para la tabla
            data = [df.columns.tolist()] + df.values.tolist()
            
            # Crear tabla
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            mimetype = 'application/pdf'
            filename = 'reporte_ventas.pdf'
        
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500 