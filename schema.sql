DROP TABLE IF EXISTS asset_history;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS category_settings;

CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_tag TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Disponible', 'Asignado', 'En Mantenimiento', 'En Garantía', 'Dado de Baja')),
    location TEXT NOT NULL,
    custodian TEXT DEFAULT 'N/A',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE asset_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets (id)
);

CREATE TABLE category_settings (
    category TEXT PRIMARY KEY,
    min_available INTEGER DEFAULT 2
);