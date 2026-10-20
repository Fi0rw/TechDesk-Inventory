# TechDesk Inventory (HAM)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-green?style=flat-square&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?style=flat-square&logo=sqlite)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?style=flat-square&logo=tailwind-css)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=flat-square)

**TechDesk Inventory** es una aplicación web MVP (Producto Mínimo Viable) desarrollada para la gestión eficiente de activos tecnológicos (Hardware Asset Management - HAM). Permite llevar el control centralizado del ciclo de vida de los equipos informáticos, garantizando la trazabilidad, asignación de custodios, alertas de stock mínimo y gestión de garantías.

---

## 📌 Tabla de Contenidos

1. [Descripción del Proyecto](#-descripción-del-proyecto)
2. [Características Principales](#-características-principales)
3. [Arquitectura y Tecnologías](#-arquitectura-y-tecnologías)
5. [Estructura del Proyecto](#-estructura-del-proyecto)
6. [Requisitos Previos](#-requisitos-previos)
7. [Instalación y Configuración](#-instalación-y-configuración)
8. [Ejecución](#-ejecución)
   - [Inicio Rápido (Usuarios no técnicos - PowerShell)](#-inicio-rápido-script-powershell)
   - [Inicio Manual (Desarrolladores)](#-inicio-manual-desarrolladores)
9. [Guía de Uso](#-guía-de-uso)
10. [Contribución](#-contribución)
11. [Licencia](#-licencia)

---


## ✨ Características Principales

- 📦 **Gestión Completa de Activos**: Monitoreo de laptops, monitores, periféricos, servidores y dispositivos de red.
- 🔄 **Ciclo de Vida Integrado**: Registro de 3 operaciones fundamentales HAM (Asignación, Devolución y Mantenimiento/Baja).
- 👤 **Asignación Automática de Custodios**: Reglas automáticas para determinar el responsable del activo según su estado.
- 📍 **Control de Ubicaciones**: Sincronización estricta entre estados y ubicaciones físicas (Depósito Central, Taller de IT, Sucursales, etc.).
- ⚠️ **Alertas de Stock Mínimo**: Indicadores visuales en el Dashboard cuando una categoría cae por debajo del umbral mínimo configurado.
- 🏷️ **Etiquetas con Código QR**: Generación dinámica de etiquetas imprimibles para fácil escaneo y auditoría de equipos.
- 📊 **Exportación de Datos**: Descarga de reportes consolidados en formato CSV (compatible con Excel).
- 📜 **Historial de Auditoría**: Registro automático de cada cambio de estado, custodio, ubicación o notas asociadas a un activo.

---

## 🛠️ Arquitectura y Tecnologías

La aplicación sigue una arquitectura ligera y autosostenible:

- **Lenguaje Principal**: Python 3.8+
- **Backend Framework**: [Flask](https://flask.palletsprojects.com/) (Ruteo, renderizado de plantillas y lógica de negocio).
- **Base de Datos**: [SQLite](https://www.sqlite.org/) (Motor relacional liviano sin necesidad de servidor externo).
- **Frontend & UI**: HTML5 con [Tailwind CSS](https://tailwindcss.com/) vía CDN (Diseño responsivo y moderno).
- **Automatización**: PowerShell para despliegue y verificación en Windows.

---

## 📁 Estructura del Proyecto

```text
techdesk_inventory/
│
├── app.py                  # Servidor Flask, rutas y lógica principal
├── schema.sql              # Esquema relacional de la base de datos (SQLite)
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

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de contar con:

- **Python 3.8** o superior instalado.
- **Pip** (Administrador de paquetes de Python).
- Un navegador web moderno (Google Chrome, Edge, Firefox, Brave).
- *(Opcional para Windows)* **PowerShell 5.1+**.

---

## 🚀 Instalación y Configuración

1. **Clonar el repositorio** o descargar los archivos del proyecto:
   ```bash
   git clone https://github.com/tu-usuario/techdesk-inventory.git
   cd techdesk-inventory
   ```

2. *(Opcional)* **Crear y activar un entorno virtual**:
   - **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicializar la Base de Datos**:
   ```bash
   python init_db.py
   ```

---

## 💻 Ejecución

### ⚡ Inicio Rápido (Script PowerShell)

Para usuarios no técnicos o ejecuciones rápidas en Windows:

1. Haz clic derecho sobre el archivo **`iniciar_techdesk.ps1`** y selecciona **Ejecutar con PowerShell** (o ejecuta desde la consola `./iniciar_techdesk.ps1`).
2. El script realizará automáticamente:
   - Verificación de la instalación de Python.
   - Comprobación e instalación desatendida de la librería `Flask`.
   - Inicialización automática de la base de datos si no existe.
   - Apertura del navegador en `http://127.0.0.1:5000` tras un tiempo de espera de 3 segundos para garantizar la carga del servidor.

### 🛠️ Inicio Manual (Desarrolladores)

1. Iniciar la aplicación Flask:
   ```bash
   python app.py
   ```
2. Abre tu navegador web y accede a:
   ```text
   http://127.0.0.1:5000
   ```

---

## 🖥️ Ejemplos de Uso

1. **Registrar Asignación**:
   - Selecciona un equipo en estado `Disponible`.
   - Haz clic en **Ver Ficha / Operaciones**.
   - Completa el nombre del usuario o área y la ubicación de destino.

2. **Registrar Devolución**:
   - En la ficha de un equipo `Asignado`, selecciona si regresa en **Buen Estado** o **Con Falla/Avería**.
   - Si regresa en buen estado, cambiará automáticamente a `Disponible` en el `Depósito Central`.

3. **Exportar Reportes**:
   - En el Dashboard principal, haz clic en el botón **Exportar a CSV** para descargar el inventario actualizado.

