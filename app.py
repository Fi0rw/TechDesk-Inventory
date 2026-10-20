import sqlite3
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, flash, Response

app = Flask(__name__)
app.secret_key = 'techdesk_secret_key_ham'

def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

# REGLA HAM: Función central para determinar el custodio automáticamente
def resolve_custodian(target_status, input_custodian=None):
    if target_status == 'Disponible':
        return 'N/A'
    elif target_status == 'Asignado':
        return input_custodian if input_custodian else 'N/A'
    elif target_status == 'En Mantenimiento':
        return 'Soporte Técnico Especializado'
    elif target_status == 'En Garantía':
        return 'Service Oficial'
    elif target_status == 'Dado de Baja':
        return 'N/A'
    return 'N/A'

ALLOWED_TRANSITIONS = {
    'Disponible': ['Asignado', 'En Mantenimiento', 'En Garantía', 'Dado de Baja'],
    'Asignado': ['Disponible'],
    'En Mantenimiento': ['Disponible', 'En Garantía', 'Dado de Baja'],
    'En Garantía': ['Disponible', 'Dado de Baja'],
    'Dado de Baja': []
}

@app.route('/')
def index():
    conn = get_db_connection()
    
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')

    query = 'SELECT * FROM assets WHERE 1=1'
    params = []

    if category_filter:
        query += ' AND category = ?'
        params.append(category_filter)
    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)
    if search_query:
        query += ' AND (name LIKE ? OR asset_tag LIKE ? OR custodian LIKE ?)'
        params.extend([f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])

    query += ' ORDER BY id DESC'
    assets = conn.execute(query, params).fetchall()
    
    metrics = {
        'total': conn.execute('SELECT COUNT(*) FROM assets').fetchone()[0],
        'disponibles': conn.execute("SELECT COUNT(*) FROM assets WHERE status = 'Disponible'").fetchone()[0],
        'asignados': conn.execute("SELECT COUNT(*) FROM assets WHERE status = 'Asignado'").fetchone()[0],
        'mantenimiento': conn.execute("SELECT COUNT(*) FROM assets WHERE status IN ('En Mantenimiento', 'En Garantía')").fetchone()[0],
        'baja': conn.execute("SELECT COUNT(*) FROM assets WHERE status = 'Dado de Baja'").fetchone()[0],
    }

    category_alerts = []
    settings = conn.execute('SELECT * FROM category_settings').fetchall()
    for st in settings:
        cat_name = st['category']
        min_qty = st['min_available']
        available_qty = conn.execute(
            "SELECT COUNT(*) FROM assets WHERE category = ? AND status = 'Disponible'", (cat_name,)
        ).fetchone()[0]
        
        if available_qty < min_qty:
            category_alerts.append({
                'category': cat_name,
                'available': available_qty,
                'min': min_qty
            })

    categories = [row['category'] for row in conn.execute('SELECT DISTINCT category FROM assets').fetchall()]
    statuses = ['Disponible', 'Asignado', 'En Mantenimiento', 'En Garantía', 'Dado de Baja']

    conn.close()
    return render_template('index.html', assets=assets, metrics=metrics, categories=categories, statuses=statuses,
                           selected_cat=category_filter, selected_status=status_filter, search=search_query,
                           category_alerts=category_alerts)


@app.route('/settings/min_stock', methods=['POST'])
def update_min_stock():
    category = request.form.get('category')
    min_qty = int(request.form.get('min_qty', 2))

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO category_settings (category, min_available) VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET min_available = ?
    ''', (category, min_qty, min_qty))
    conn.commit()
    conn.close()
    
    flash(f'Umbral mínimo para "{category}" actualizado a {min_qty} unidades.', 'success')
    return redirect(url_for('index'))


@app.route('/export/csv')
def export_csv():
    conn = get_db_connection()
    assets = conn.execute('SELECT id, asset_tag, name, category, status, location, custodian, warranty_expiration, updated_at FROM assets').fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Asset Tag', 'Nombre/Modelo', 'Categoria', 'Estado', 'Ubicacion', 'Custodio', 'Vencimiento Garantia', 'Ultima Actualizacion'])
    
    for a in assets:
        writer.writerow([a['id'], a['asset_tag'], a['name'], a['category'], a['status'], a['location'], a['custodian'], a['warranty_expiration'], a['updated_at']])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=Reporte_Inventario_HAM.csv"}
    )


@app.route('/asset/<int:asset_id>')
def asset_detail(asset_id):
    conn = get_db_connection()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()
    
    if not asset:
        flash('El activo solicitado no existe.', 'error')
        conn.close()
        return redirect(url_for('index'))

    qr_data = request.host_url.rstrip('/') + url_for('asset_detail', asset_id=asset_id)
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}"

    history = conn.execute('SELECT * FROM asset_history WHERE asset_id = ? ORDER BY timestamp DESC', (asset_id,)).fetchall()
    conn.close()
    return render_template('asset_detail.html', asset=asset, history=history, qr_code_url=qr_code_url)


@app.route('/op/assign/<int:asset_id>', methods=['POST'])
def assign_asset(asset_id):
    custodian = request.form.get('custodian', '').strip()
    location = request.form.get('location', '').strip()
    notes = request.form.get('notes', '').strip()

    if not custodian or not location:
        flash('Debe especificar de forma obligatoria el Custodio/Usuario y la Ubicación.', 'error')
        return redirect(url_for('asset_detail', asset_id=asset_id))

    conn = get_db_connection()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()

    if asset['status'] != 'Disponible':
        flash('Regla HAM: Solo se pueden asignar activos en estado "Disponible".', 'error')
        conn.close()
        return redirect(url_for('asset_detail', asset_id=asset_id))

    conn.execute('''
        UPDATE assets SET status = 'Asignado', custodian = ?, location = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (custodian, location, asset_id))

    conn.execute('''
        INSERT INTO asset_history (asset_id, action, previous_status, new_status, custodian, location, notes)
        VALUES (?, 'Asignación de Activo', 'Disponible', 'Asignado', ?, ?, ?)
    ''', (asset_id, custodian, location, notes))

    conn.commit()
    conn.close()
    flash(f'Activo asignado exitosamente a {custodian}.', 'success')
    return redirect(url_for('asset_detail', asset_id=asset_id))


# OPERACIÓN 02: Devolución / Reingreso al Depósito
@app.route('/op/return/<int:asset_id>', methods=['POST'])
def return_asset(asset_id):
    condition = request.form.get('condition')
    location = request.form.get('location', '').strip()
    notes = request.form.get('notes', '').strip()

    conn = get_db_connection()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()

    if asset['status'] != 'Asignado':
        flash('Regla HAM: Solo se pueden devolver equipos que estén actualmente en estado "Asignado".', 'error')
        conn.close()
        return redirect(url_for('asset_detail', asset_id=asset_id))

    # LÓGICA CORREGIDA Y AUTOMÁTICA DE UBICACIÓN Y CUSTODIO
    if condition == 'good':
        new_status = 'Disponible'
        new_custodian = resolve_custodian(new_status)
        # Si pasa a disponible, por regla obligatoria va al Depósito Central
        final_location = 'Depósito Central'
        action_name = 'Devolución (Buen Estado)'
    else:
        new_status = 'En Mantenimiento'
        new_custodian = resolve_custodian(new_status)
        # Si va a mantenimiento con falla, por defecto va al Taller de IT (a menos que especifiquen otra cosa)
        final_location = location if location and location != 'Depósito Central' else 'Taller de IT'
        action_name = 'Devolución (Con Falla/Avería)'

    conn.execute('''
        UPDATE assets SET status = ?, custodian = ?, location = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (new_status, new_custodian, final_location, asset_id))

    conn.execute('''
        INSERT INTO asset_history (asset_id, action, previous_status, new_status, custodian, location, notes)
        VALUES (?, ?, 'Asignado', ?, ?, ?, ?)
    ''', (asset_id, action_name, new_status, new_custodian, final_location, notes))

    conn.commit()
    conn.close()
    flash(f'Devolución registrada. Estado actual: {new_status} | Ubicación: {final_location} | Custodio: {new_custodian}.', 'success')
    return redirect(url_for('asset_detail', asset_id=asset_id))


# OPERACIÓN 03: Mantenimiento, Garantía o Baja Definitiva corregida
@app.route('/op/status_change/<int:asset_id>', methods=['POST'])
def status_change(asset_id):
    target_status = request.form.get('target_status')
    location = request.form.get('location', '').strip()
    notes = request.form.get('notes', '').strip()

    conn = get_db_connection()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()
    current_status = asset['status']

    if target_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        flash(f'Violación de Regla HAM: No se permite cambiar directamente de "{current_status}" a "{target_status}". Registre una devolución al depósito primero.', 'error')
        conn.close()
        return redirect(url_for('asset_detail', asset_id=asset_id))

    new_custodian = resolve_custodian(target_status)

    # Ubicación inteligente por defecto según el estado de destino
    if target_status == 'En Mantenimiento':
        new_location = location if location else 'Taller de IT'
    elif target_status == 'En Garantía':
        new_location = location if location else 'Proveedor Externo'
    elif target_status == 'Disponible':
        new_location = location if location else 'Depósito Central'
    else:
        new_location = location if location else asset['location']

    conn.execute('''
        UPDATE assets SET status = ?, location = ?, custodian = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (target_status, new_location, new_custodian, asset_id))

    conn.execute('''
        INSERT INTO asset_history (asset_id, action, previous_status, new_status, custodian, location, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (asset_id, f'Cambio de Estado a {target_status}', current_status, target_status, new_custodian, new_location, notes))

    conn.commit()
    conn.close()
    flash(f'Estado cambiado a "{target_status}". Ubicación asignada: "{new_location}" | Custodio: "{new_custodian}".', 'success')
    return redirect(url_for('asset_detail', asset_id=asset_id))


if __name__ == '__main__':
    app.run(debug=True, port=5000)