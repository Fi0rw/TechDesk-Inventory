# Documento de Decisiones de Diseño 

- **Proyecto:** TechDesk Inventory — Sistema de Control e Inventario de Activos IT
- **Autor:** Tobías Gabriel Fioroni
- **Fecha:** 20 de Octubre de 2026

## 1. Enfoque General y Alcance del Dominio (ITAM y HAM Operativo)

Para el desarrollo del presente MVP (Producto Mínimo Viable), se analizó la práctica formal de **ITAM (IT Asset Management)**, la cual gobierna los activos tecnológicos de una organización durante la totalidad de su ciclo de vida. 

Se definió delimitar el alcance hacia la especialización de **HAM (Hardware Asset Management)**, priorizando el control físico del activo, su ubicación, su asignación, el seguimiento de sus **fechas críticas (como el vencimiento de garantías)** y su historial de auditoría. 

* **Lo que cubre el MVP:** Control de inventario de bienes de uso, gestión de estados de stock, asignación a custodios, reingresos, envío a mantenimiento/garantía con asignación automática de responsables, control de garantías por fecha, alertas de stock crítico y historial de movimientos.

## 2. Modelo del Ciclo de Vida del Activo y Estados Definidos

El stock debe administrarse de forma activa, no únicamente lo que ya está instalado y en uso. Los estados posibles habituales de un activo son: disponible, en preparación, reservado, en reparación, pendiente de baja, retirado, en tránsito, prestado y en cuarentena. Cada uno de estos estados condiciona qué acciones son válidas sobre el activo en ese momento

En este caso, se decidió utilizar **5 estados operativos** que replican el ciclo de vida real de un activo para simplificar el MVP:
1. **`Disponible` (En Pañol/Depósito):** Físicamente en stock, configurado y listo para ser asignado. Sin custodio asignado (`N/A`), ubicado obligatoriamente en Depósito Central.
2. **`Asignado` (En Uso Operativo):** Entregado a un usuario final o área. Exige obligatoriamente un **Custodio / Usuario** y una ubicación de destino.
3. **`En Mantenimiento`:** Falla técnica o reparación interna. Se remueve del stock operativo y el sistema asigna automáticamente como custodio a **'Soporte Técnico Especializado'** en el Taller de IT.
4. **`En Garantía`:** Remitido al proveedor o servicio técnico oficial bajo cobertura contractual. El sistema asigna automáticamente como custodio al **'Service Oficial'**.
5. **`Dado de Baja`:** Estado terminal del activo por obsolescencia o daño irreparable. Conserva su historial de movimientos intacto para auditorías.

## 3. Reglas de Negocio Operativas e Integridad de Procesos

Para garantizar la coherencia del pañol y evitar inconsistencias de datos:

1. **Trazabilidad de Devolución Obligatoria:** Un activo en estado `Asignado` **no puede ser enviado de forma directa a `En Mantenimiento` o `Dado de Baja`**. Se requiere obligatoriamente registrar primero la **Operación 02 (Devolución / Reingreso)**:
    - Si se devuelve en **Buen Estado**, pasa a `Disponible` y retorna automáticamente al *Depósito Central* con custodio `N/A`.
    - Si se devuelve **Con Falla**, pasa a `En Mantenimiento` con derivación automática al *Taller de IT*.
2. **Automatización de Custodios y Ubicaciones:**
    - **Asignación (Op. 01):** Campo de custodio y ubicación obligatorios.
    - **Mantenimiento:** Custodio fijo asignado: *Soporte Técnico Especializado*.
    - **Garantía:** Custodio fijo asignado: *Service Oficial*.
    - **Baja / Disponible:** Custodio asignado: `N/A`.
3. **Control de Fechas y Vencimiento de Garantías:** Cada activo registra de forma estructurada su **fecha de expiración de garantía**, lo que permite al personal de soporte identificar rápidamente si un componente averiado cuenta con cobertura del fabricante antes de derivarlo a costos internos.
4. **Historial de Movimientos:** Cada cambio de estado, asignación, devolución o reporte genera un registro inmutable con estado anterior, nuevo, custodio, ubicación, notas y marca de tiempo.
5. **Identificación Única y QR:** Cada equipo cuenta con un etiqueta de activo (Asset Tag) unívoco (ej: `IT-2026-001`) y una etiqueta QR integrada para escaneo rápido y control de inventario.

## 4. Modelo de Datos y Normalización (SQLite)

El sistema utiliza un esquema relacional normalizado en SQLite compuesto por tres tablas principales diseñadas para garantizar la integridad referencial y el seguimiento histórico de activos. En resumen:
1. **`assets`**: Tabla central que almacena el inventario de equipos, estados, custodios, ubicaciones y la **fecha de vencimiento de garantía (`warranty_expiration`)**.
2. **`asset_history`**: Bitácora relacional que historiza cada transacción vinculada por clave foránea al activo.
3. **`category_settings`**: Tabla de parámetros que almacena los umbrales de stock mínimo configurable por categoría para disparar las alertas visuales.

### 1. Tabla: `assets` (Inventario de Activos de Hardware)
Almacena la información principal de cada activo tecnológico.

| Campo | Tipo de Dato | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único del registro |
| `asset_tag` | TEXT | UNIQUE, NOT NULL | Código/Etiqueta unívoca de inventario (ej: IT-2026-001) |
| `name` | TEXT | NOT NULL | Nombre, marca o modelo del equipo |
| `category` | TEXT | NOT NULL | Categoría funcional (Laptops, Monitores, Redes, etc.) |
| `status` | TEXT | NOT NULL, CHECK | Estado operativo (`Disponible`, `Asignado`, `En Mantenimiento`, `En Garantía`, `Dado de Baja`) |
| `location` | TEXT | NOT NULL | Ubicación física actual (Depósito Central, Taller IT, etc.) |
| `custodian` | TEXT | DEFAULT 'N/A' | Empleado, área o entidad responsable del equipo |
| `warranty_expiration` | DATE | NULLABLE | Fecha de vencimiento de la cobertura/garantía oficial |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Fecha y hora de la última modificación realizada |

### 2. Tabla: `asset_history` (Historial de movimientos para Auditoría y Trazabilidad)
Registra de forma inmutable cada movimiento o cambio de estado realizado sobre un activo.

| Campo | Tipo de Dato | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único del movimiento |
| `asset_id` | INTEGER | FOREIGN KEY (`assets.id`), NOT NULL | Vínculo al activo auditado |
| `action` | TEXT | NOT NULL | Nombre de la operación realizada (ej: Asignación, Devolución) |
| `previous_status` | TEXT | NULLABLE | Estado en el que se encontraba el activo antes del cambio |
| `new_status` | TEXT | NOT NULL | Nuevo estado asignado tras la operación |
| `custodian` | TEXT | NULLABLE | Custodio registrado en el momento del movimiento |
| `location` | TEXT | NULLABLE | Ubicación asignada en el momento del movimiento |
| `notes` | TEXT | NULLABLE | Observaciones, justificaciones o detalles de fallas |
| `timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Marca de tiempo exacta del registro |

### 3. Tabla: `category_settings` (Parámetros de Stock Mínimo)
Almacena los umbrales de alerta configurables para cada categoría de hardware.

| Campo | Tipo de Dato | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `category` | TEXT | PRIMARY KEY | Nombre único de la categoría configurada |
| `min_available` | INTEGER | DEFAULT 2 | Unidades mínimas requeridas antes de disparar alerta de stock |

---

### Relaciones entre Entidades (Cardinalidad)
- **`assets` (1) ─── (0..N) `asset_history`**: Un activo puede tener cero o múltiples registros históricos en la bitácora de auditoría. Cada registro histórico pertenece estrictamente a un único activo (`FOREIGN KEY (asset_id)`).