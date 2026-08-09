# EasyPOS — Sistema web de punto de venta e inventario

Aplicación web para pequeños comercios. Permite administrar productos y categorías, clientes, proveedores y usuarios; registrar compras y ventas; actualizar inventario y consultar reportes diarios desde un navegador.

> La versión a entregar se ejecuta con **Flask + MySQL**. El archivo `app.py` se conserva como la primera versión de escritorio; el archivo principal de la versión web es `web_app.py`.

## Contenido de la entrega

| Archivo o carpeta | Contenido |
| --- | --- |
| `web_app.py` | Código fuente principal de la aplicación web Flask. |
| `templates/` y `static/` | Interfaz web HTML/CSS. |
| `wsgi.py` y `Procfile` | Punto de entrada para hosting compatible con WSGI. |
| `app.py` | Versión inicial de escritorio, conservada como referencia. |
| `config.py` | Parámetros de conexión a MySQL que deben ajustarse en cada equipo. |
| `requirements.txt` | Dependencia de Python. |
| `database/schema.sql` | Definición completa de la base de datos y datos iniciales de prueba. También puede usarse para restaurar una instalación limpia. |
| `ENTREGA.md` | Instructivo de instalación, pruebas y material para el video. |

## Requisitos

- Python 3.10 o superior.
- MySQL Server 8.0 o compatible y MySQL Workbench (opcional, para importar el script).
- Acceso a una cuenta de MySQL con permiso para crear bases de datos.

## Instalación rápida

1. Abra MySQL Workbench, conéctese al servidor y ejecute el archivo `database/schema.sql` completo. Este crea la base de datos `pos_db`, sus tablas, relaciones y registros de demostración.
2. Abra `config.py` y ajuste `host`, `user` y `password` con las credenciales de su instalación de MySQL. El nombre de la base debe permanecer como `pos_db`.
3. Desde una terminal ubicada en esta carpeta, instale la dependencia:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Inicie el sistema web:

   ```bash
   python web_app.py
   ```

5. Abra `http://127.0.0.1:5000` en el navegador.

Para publicar en un hosting, consulte [DESPLIEGUE_WEB.md](DESPLIEGUE_WEB.md).

## Datos iniciales para pruebas

El script crea automáticamente los siguientes registros:

- Usuario: `admin` — contraseña registrada: `admin123` — rol: Administrador.
- Cliente: Cliente General.
- Proveedor: Proveedor General.
- Productos: Camiseta Deportiva (código `75010001`) y Tachones / Tacos (código `75010002`).

La versión académica no incluye una pantalla de inicio de sesión: el usuario `admin` se selecciona en los módulos de ventas y compras para identificar quién realizó el movimiento.

## Flujo básico de prueba

1. En **Productos / Categorías**, revise los dos productos precargados o agregue uno nuevo.
2. En **Ventas**, seleccione Cliente General y admin, escriba el código `75010001`, indique una cantidad y pulse **Añadir a Factura**. Luego pulse **Procesar y Guardar Factura**. El stock disminuirá.
3. En **Compras**, seleccione el proveedor y admin, indique una referencia distinta (por ejemplo, `REF-002`), agregue un producto con cantidad y costo, y guarde. El stock aumentará.
4. En **Reportes**, consulte inventario, ventas del día y compras del día.

Para volver a un estado de prueba limpio, elimine la base `pos_db` desde MySQL y ejecute nuevamente `database/schema.sql`.

## Nota de seguridad

Las contraseñas se guardan como texto plano solo para fines académicos. Una versión de producción debe usar autenticación real, hash de contraseñas y variables de entorno para las credenciales de base de datos.
