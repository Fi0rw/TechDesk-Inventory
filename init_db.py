import sqlite3

def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    with open('schema.sql', 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())

    initial_assets = [
        ('IT-2026-001', 'MacBook Pro 16" M2', 'Laptops', 'Disponible', 'Depósito Central', 'N/A', '2027-12-31'),
        ('IT-2026-002', 'Dell XPS 15 9520', 'Laptops', 'Asignado', 'Home Office', 'Carlos Gómez', '2026-11-15'),
        ('IT-2026-003', 'Lenovo ThinkPad T14 Gen 3', 'Laptops', 'Asignado', 'Sucursal Norte', 'María Rodríguez', '2026-08-20'),
        ('IT-2026-004', 'HP EliteBook 840 G8', 'Laptops', 'En Mantenimiento', 'Taller de IT', 'Soporte Técnico Especializado', '2025-05-10'),
        ('IT-2026-005', 'ASUS ZenBook 14', 'Laptops', 'Disponible', 'Depósito Central', 'N/A', '2027-01-10'),

        ('IT-2026-006', 'Dell UltraSharp 27" U2722D', 'Monitores', 'Asignado', 'Sucursal Sur', 'Ana Martínez', '2026-09-30'),
        ('IT-2026-007', 'LG Ergonomic 32" 4K', 'Monitores', 'Disponible', 'Depósito Central', 'N/A', '2027-03-15'),
        ('IT-2026-008', 'Samsung Odyssey G7 28"', 'Monitores', 'Dado de Baja', 'Depósito Scrap', 'N/A', '2024-01-01'),
        ('IT-2026-009', 'BenQ DesignVue 27"', 'Monitores', 'Asignado', 'Home Office', 'Lucas Fernández', '2026-12-01'),

        ('IT-2026-010', 'Teclado Mecánico Logitech MX Keys', 'Periféricos', 'Disponible', 'Depósito Central', 'N/A', '2027-05-01'),
        ('IT-2026-011', 'Mouse Logitech MX Master 3S', 'Periféricos', 'Asignado', 'Home Office', 'Carlos Gómez', '2027-05-01'),
        ('IT-2026-012', 'Docking Station Thunderbolt 4 HP', 'Periféricos', 'En Garantía', 'Proveedor Externo', 'Service Oficial', '2026-12-31'),
        ('IT-2026-013', 'Auriculares Jabra Evolve2 65', 'Periféricos', 'Disponible', 'Depósito Central', 'N/A', '2026-10-10'),

        ('IT-2026-014', 'Switch Cisco Catalyst 9300 48P', 'Redes', 'Disponible', 'Sala de Servidores', 'N/A', '2028-01-01'),
        ('IT-2026-015', 'Router MikroTik CCR1036', 'Redes', 'Asignado', 'Sucursal Norte', 'Sistemas Sucursal', '2027-06-15'),
        ('IT-2026-016', 'Access Point Ubiquiti UniFi AP 6 Pro', 'Redes', 'Disponible', 'Depósito Central', 'N/A', '2027-02-28'),
        ('IT-2026-017', 'Firewall Fortinet FortiGate 60F', 'Redes', 'Asignado', 'Sala de Servidores', 'Seguridad IT', '2028-03-31'),

        ('IT-2026-018', 'Servidor Dell PowerEdge R750', 'Servidores', 'Asignado', 'Sala de Servidores', 'Infraestructura', '2029-01-01'),
        ('IT-2026-019', 'Servidor HPE ProLiant DL380 Gen10', 'Servidores', 'En Mantenimiento', 'Taller de IT', 'Soporte Técnico Especializado', '2026-11-30'),
        ('IT-2026-020', 'NAS Synology RackStation RS2421+', 'Servidores', 'Disponible', 'Depósito Central', 'N/A', '2027-04-15')
    ]

    cursor.executemany('''
        INSERT INTO assets (asset_tag, name, category, status, location, custodian, warranty_expiration)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', initial_assets)

    categories = ['Laptops', 'Monitores', 'Periféricos', 'Redes', 'Servidores']
    for cat in categories:
        cursor.execute('INSERT INTO category_settings (category, min_available) VALUES (?, ?)', (cat, 2))

    cursor.execute('SELECT id, status, location, custodian FROM assets')
    assets = cursor.fetchall()
    for asset in assets:
        cursor.execute('''
            INSERT INTO asset_history (asset_id, action, previous_status, new_status, custodian, location, notes)
            VALUES (?, 'Registro Inicial', 'Nuevo', ?, ?, ?, ?)
        ''', (asset[0], asset[1], asset[3], asset[2], f'Alta inicial en sistema.'))

    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente.")

if __name__ == '__main__':
    init_db()