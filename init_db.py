import sqlite3

def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    with open('schema.sql', 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())

    # 20 Activos Iniciales
    initial_assets = [
        # Laptops
        ('TAG-1001', 'MacBook Pro 16" M2', 'Laptops', 'Disponible', 'Depósito Central', 'N/A'),
        ('TAG-1002', 'Dell XPS 15 9520', 'Laptops', 'Asignado', 'Home Office', 'Carlos Gómez'),
        ('TAG-1003', 'Lenovo ThinkPad T14 Gen 3', 'Laptops', 'Asignado', 'Sucursal Norte', 'María Rodríguez'),
        ('TAG-1004', 'HP EliteBook 840 G8', 'Laptops', 'En Mantenimiento', 'Depósito Central', 'N/A'),
        ('TAG-1005', 'ASUS ZenBook 14', 'Laptops', 'Disponible', 'Depósito Central', 'N/A'),

        # Monitores
        ('TAG-2001', 'Dell UltraSharp 27" U2722D', 'Monitores', 'Asignado', 'Sucursal Sur', 'Ana Martínez'),
        ('TAG-2002', 'LG Ergonomic 32" 4K', 'Monitores', 'Disponible', 'Depósito Central', 'N/A'),
        ('TAG-2003', 'Samsung Odyssey G7 28"', 'Monitores', 'Dado de Baja', 'Depósito Central', 'N/A'),
        ('TAG-2004', 'BenQ DesignVue 27"', 'Monitores', 'Asignado', 'Home Office', 'Lucas Fernández'),

        # Periféricos
        ('TAG-3001', 'Teclado Mecánico Logitech MX Keys', 'Periféricos', 'Disponible', 'Depósito Central', 'N/A'),
        ('TAG-3002', 'Mouse Logitech MX Master 3S', 'Periféricos', 'Asignado', 'Home Office', 'Carlos Gómez'),
        ('TAG-3003', 'Docking Station Thunderbolt 4 HP', 'Periféricos', 'En Garantía', 'Servicio Técnico Oficial', 'N/A'),
        ('TAG-3004', 'Auriculares Jabra Evolve2 65', 'Periféricos', 'Disponible', 'Depósito Central', 'N/A'),

        # Redes
        ('TAG-4001', 'Switch Cisco Catalyst 9300 48P', 'Redes', 'Disponible', 'Sala de Servidores', 'Infraestructura'),
        ('TAG-4002', 'Router MikroTik CCR1036', 'Redes', 'Asignado', 'Sucursal Norte', 'Sistemas Sucursal'),
        ('TAG-4003', 'Access Point Ubiquiti UniFi AP 6 Pro', 'Redes', 'Disponible', 'Depósito Central', 'N/A'),
        ('TAG-4004', 'Firewall Fortinet FortiGate 60F', 'Redes', 'Asignado', 'Sala de Servidores', 'Seguridad IT'),

        # Servidores
        ('TAG-5001', 'Servidor Dell PowerEdge R750', 'Servidores', 'Asignado', 'Sala de Servidores', 'Infraestructura'),
        ('TAG-5002', 'Servidor HPE ProLiant DL380 Gen10', 'Servidores', 'En Mantenimiento', 'Sala de Servidores', 'Infraestructura'),
        ('TAG-5003', 'NAS Synology RackStation RS2421+', 'Servidores', 'Disponible', 'Depósito Central', 'N/A')
    ]

    cursor.executemany('''
        INSERT INTO assets (asset_tag, name, category, status, location, custodian)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', initial_assets)

    # Configuración de Mínimos por Defecto por Categoría
    categories = ['Laptops', 'Monitores', 'Periféricos', 'Redes', 'Servidores']
    for cat in categories:
        cursor.execute('INSERT INTO category_settings (category, min_available) VALUES (?, ?)', (cat, 2))

    # Historial Inicial
    cursor.execute('SELECT id, status, location, custodian FROM assets')
    assets = cursor.fetchall()
    for asset in assets:
        cursor.execute('''
            INSERT INTO asset_history (asset_id, action, previous_status, new_status, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (asset[0], 'Registro Inicial', 'Nuevo', asset[1], f'Ubicación inicial: {asset[2]}. Custodio: {asset[3]}'))

    conn.commit()
    conn.close()
    print("✅ Base de datos re-inicializada con soporte para Mínimos y QR.")

if __name__ == '__main__':
    init_db()