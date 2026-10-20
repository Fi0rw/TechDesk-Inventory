import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'techdesk_secret_key_ham'

def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

# Transiciones de estado permitidas según Reglas de Negocio HAM
ALLOWED_TRANSITIONS = {
    'Disponible': ['Asignado', 'En Mantenimiento', 'En Garantía', 'Dado de Baja'],
    'Asignado': ['Disponible'], # Regla HAM: Debe devolverse al depósito antes de ir a Mant./Baja
    'En Mantenimiento': ['Disponible', 'En Garantía', 'Dado de Baja'],
    'En Garantía': ['Disponible', 'Dado de Baja'],
    'Dado de Baja': [] # Estado terminal
}

@app.route('/')
def index():
    conn = get_db_connection()
    
    # Filtros
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
    
    # Obtener métricas rápidas
    metrics = {
        'total': conn.execute('SELECT COUNT(*) FROM assets').fetchone()[0],
        'disponibles': conn.execute("SELECT COUNT(*) FROM assets WHERE status = 'Disponible'").fetchone()[0],
        'asignados': conn.execute("SELECT COUNT(*) FROM assets WHERE status = 'Asignado'").fetchone()[0],
        'mantenimiento': conn.execute("SELECT COUNT(*) FROM assets WHERE status IN ('En Mantenimiento', 'En Garantía')").fetchone()[0],
        'baja': conn.execute("SELECT COUNT(*) FROM assets WHERE status = 'Dado de Baja'").fetchone()[0],
    }

    categories = [row['category'] for row in conn.execute('SELECT DISTINCT category FROM assets').fetchall()]
    statuses = ['Disponible', 'Asignado', 'En Mantenimiento', 'En Garantía', 'Dado de Baja']

    conn.close()
    return render_template('index.html', assets=assets, metrics=metrics, categories=categories, statuses=statuses,
                           selected_cat=category_filter, selected_status=status_filter, search=search_query)


@app.route('/asset/<int:asset_id>')
def asset_detail(asset_id):
    conn = get_db_connection()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()
    
    if not asset:
        flash('El activo solicitado no existe.', 'error')
        conn.close()
        return redirect(url_for('index'))

    history = conn.execute('SELECT * FROM asset_history WHERE asset_id = ? ORDER BY timestamp DESC', (asset_id,)).fetchall()
    conn.close()
    return render_template('asset_detail.html', asset=asset, history=history)


# OPERACIÓN 01: Asignación y entrega a un custodio
@app.route('/op/assign/<int:asset_id>', methods=['POST'])
def assign_asset(asset_id):
    custodian = request.form.get('custodian', '').strip()
    location = request.form.get('location', '').strip()
    notes = request.form.get('notes', '').strip()

    if not custodian or not location:
        flash('Debe especificar el custodio y la ubicación física.', 'error')
        return redirect(url_for('asset_detail', asset_id=asset_id))

    conn = get_db_connection()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()

    if asset['status'] != 'Disponible':
        flash('Regla HAM: Solo se pueden asignar activos en estado "Disponible".', 'error')
        conn.close()
        return redirect(url_for('asset_detail', asset_id=asset_id))

    # Actualizar Estado
    conn.execute('''
        UPDATE assets 
        SET status = 'Asignado', custodian = ?, location = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (custodian, location, asset_id))

    # Registrar Historial
    conn.execute('''
        INSERT INTO asset_history (asset_id, action, previous_status, new_status, notes)
        VALUES (?, 'Asignación de Activo', 'Disponible', 'Asignado', ?)
    ''', (asset_id, f"Asignado a: {custodian} | Ubicación: {location} | Notas: {notes}"))

    conn.commit()
    conn.close()
    flash(f'Activo asignado exitosamente a {custodian}.', 'success')
    return redirect(url_for('asset_detail', asset_id=asset_id))


# OPERACIÓN 02: Devolución o Reingreso
@app.route('/op/return/<int:asset_id>', methods=['POST'])
def return_asset(asset_id):
    condition = request.form.get('condition') # 'good' o 'faulty'
    location = request.form.get('location', 'Depósito Central').strip()
    notes = request.form.get('notes', '').strip()

    conn = get_db_connection()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()

    if asset['status'] != 'Asignado':
        flash('Solo se pueden registrar devoluciones de equipos en estado "Asignado".', 'error')
        conn.close()
        return redirect(url_for('asset_detail', asset_id=asset_id))

    new_status = 'Disponible' if condition == 'good' else 'En Mantenimiento'
    action_name = 'Devolución (Buen Estado)' if condition == 'good' else 'Devolución (Con Falla/Avería)'

    conn.execute('''
        UPDATE assets 
        SET status = ?, custodian = 'N/A', location = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (new_status, location, asset_id))

    conn.execute('''
        INSERT INTO asset_history (asset_id, action, previous_status, new_status, notes)
        VALUES (?, ?, 'Asignado', ?, ?)
    ''', (asset_id, action_name, new_status, f"Ubicación de retorno: {location}. Estado de entrega: {action_name}. Notas: {notes}"))

    conn.commit()
    conn.close()
    flash(f'Devolución procesada correctamente. Nuevo estado: {new_status}.', 'success')
    return redirect(url_for('asset_detail', asset_id=asset_id))


# OPERACIÓN 03: Mantenimiento, Garantía o Baja Definitiva
@app.route('/op/status_change/<int:asset_id>', methods=['POST'])
def status_change(asset_id):
    target_status = request.form.get('target_status')
    location = request.form.get('location', '').strip()
    notes = request.form.get('notes', '').strip()

    conn = get_db_connection()
    asset = conn.execute('SELECT * FROM assets WHERE id = ?', (asset_id,)).fetchone()
    current_status = asset['status']

    # Validación de Regla de Negocio
    if target_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        flash(f'Violación de Regla HAM: No se permite cambiar directo de "{current_status}" a "{target_status}". Realice una devolución primero.', 'error')
        conn.close()
        return redirect(url_for('asset_detail', asset_id=asset_id))

    # Si va a Baja o Garantía/Mantenimiento, actualizar ubicación si se provee
    new_location = location if location else asset['location']
    new_custodian = 'N/A' if target_status in ['Disponible', 'Dado de Baja', 'En Mantenimiento', 'En Garantía'] else asset['custodian']

    conn.execute('''
        UPDATE assets 
        SET status = ?, location = ?, custodian = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (target_status, new_location, new_custodian, asset_id))

    conn.execute('''
        INSERT INTO asset_history (asset_id, action, previous_status, new_status, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (asset_id, f'Cambio de Estado a {target_status}', current_status, target_status, notes))

    conn.commit()
    conn.close()
    flash(f'Estado del activo actualizado a "{target_status}".', 'success')
    return redirect(url_for('asset_detail', asset_id=asset_id))


if __name__ == '__main__':
    app.run(debug=True, port=5000)