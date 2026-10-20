# TechDesk Inventory (HAM)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-green?style=flat-square&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?style=flat-square&logo=sqlite)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?style=flat-square&logo=tailwind-css)

Aplicación web MVP para la gestión de activos tecnológicos (Hardware Asset Management - HAM). Permite controlar el ciclo de vida de los equipos, asignaciones, garantías, alertas de stock e historial de movimientos.

---

## Características

- **Gestión de activos:** Control de laptops, monitores, periféricos, servidores y redes.
- **Ciclo de vida HAM:** Operaciones de Asignación, Devolución y Mantenimiento/Baja.
- **Reglas automáticas:** Asignación automática de custodios y ubicaciones según el estado del equipo.
- **Alertas de stock:** Avisos visuales en categorías con bajo stock disponible.
- **Etiquetas QR:** Generación de códigos QR imprimibles por equipo.
- **Reportes:** Exportación del inventario completo a formato CSV.
- **Bitácora:** Registro inmutable de cambios de estado y movimientos.

---

## Stack Tecnológico

- **Backend:** Python 3.8+ con Flask
- **Base de datos:** SQLite
- **Frontend:** HTML5 + Tailwind CSS (vía CDN)
- **Automatización:** PowerShell (`.ps1`)

---

## Estructura del Proyecto

```text
techdesk_inventory/
│
├── app.py                  # Servidor Flask, rutas y lógica principal
├── schema.sql              # Esquema relacional de la base de datos (SQLite)
├── inventory.db            # Base de datos
├── init_db.py              # Script para crear la BD e insertar datos iniciales
├── iniciar_techdesk.ps1    # Script de automatización para ejecución en Windows
├── requirements.txt        # Dependencias del proyecto
│
├── templates/              # Plantillas HTML 
│   ├── base.html           # Layout principal y CDN de Tailwind CSS
│   ├── index.html          # Dashboard principal, métricas y tabla
│   └── asset_detail.html   # Ficha técnica, código QR, operaciones e historial
│
└── assets/                 # Recursos y capturas para documentación
```

---

## Stack Tecnológico

- **Backend:** Python 3.8+ con Flask
- **Base de datos:** SQLite
- **Frontend:** HTML5 + Tailwind CSS (vía CDN)
- **Automatización:** PowerShell (`.ps1`)

---

## Ejecución

### Opción 1: Automática (Windows)

Ejecuta el script de PowerShell haciendo clic derecho -> **Ejecutar con PowerShell**:
```powershell
.\iniciar_techdesk.ps1
```
El script verifica la instalación de Python y Flask, inicializa la base de datos y abre la aplicación en `http://127.0.0.1:5000`.

### Opción 2: Manual

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicializar la base de datos:
   ```bash
   python init_db.py
   ```
3. Iniciar el servidor:
   ```bash
   python app.py
   ```
4. Abrir en el navegador: `http://127.0.0.1:5000`

---

## Uso Rápido

1. **Asignación (Op. 01):** Desde un equipo `Disponible`, asigna usuario/área y ubicación.
2. **Devolución (Op. 02):** Registra el reingreso en buen estado (vuelve a `Disponible` / `Depósito Central`) o con falla (pasa a `En Mantenimiento` / `Taller IT`).
3. **Mantenimiento/Baja (Op. 03):** Gestiona garantías, reparaciones o bajas definitivas.
4. **Exportación:** Descarga el reporte consolidado en CSV desde el Dashboard.