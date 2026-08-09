# Instructivo de entrega — EasyPOS

## Qué debe comprimirse

Comprima la carpeta completa del proyecto, conservando esta estructura:

```text
EasyPOS/
├── web_app.py
├── templates/
├── static/
├── wsgi.py
├── Procfile
├── config.py
├── requirements.txt
├── README.md
├── ENTREGA.md
└── database/
    └── schema.sql
```

No es necesario incluir la carpeta `__pycache__`, ya que se genera automáticamente al ejecutar Python.

## Base de datos y restauración

El archivo `database/schema.sql` es la definición reproducible y respaldo inicial de la base de datos. Contiene:

- Creación de la base `pos_db`.
- Tablas, llaves primarias, relaciones y restricciones.
- Datos semilla necesarios para probar el sistema.

Para restaurarlo en MySQL Workbench: abra el archivo, selecciónelo completo y presione el botón de ejecución (ícono de rayo). También puede utilizar una terminal de MySQL:

```bash
mysql -u root -p < database/schema.sql
```

Si se desea generar un respaldo con los registros creados durante una demostración, después de instalar MySQL ejecute:

```bash
mysqldump -u root -p pos_db > pos_db_respaldo.sql
```

## Configuración necesaria

Edite `config.py` antes de ejecutar el programa si MySQL no usa la configuración predeterminada:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'pos_db'
}
```

El usuario de demostración es `admin` y la contraseña almacenada en la base es `admin123`; no se solicita en pantalla porque la aplicación no implementa inicio de sesión. Para hosting, configure las credenciales de MySQL como variables de entorno; consulte `DESPLIEGUE_WEB.md`.

## Guion sugerido para el video de YouTube

1. Presentar a los integrantes y el objetivo: sistema de punto de venta e inventario para pequeños comercios.
2. Mostrar la carpeta entregada: código fuente, `requirements.txt` y `database/schema.sql`.
3. Importar `database/schema.sql` y mostrar las tablas creadas en MySQL.
4. Configurar MySQL, instalar las dependencias y ejecutar `python web_app.py`.
5. Mostrar Productos/Categorías, Clientes, Proveedores y Usuarios.
6. Registrar una venta usando el código `75010001` y comprobar que baja el inventario.
7. Registrar una compra con una referencia nueva y comprobar que sube el inventario.
8. Abrir Reportes y mostrar inventario, ventas y compras del día.
9. Abrir la URL pública del hosting, repetir una prueba breve y confirmar que corresponde al código entregado.

Antes de publicar, reemplacen esta línea por el enlace del video:

```text
Video de demostración: PENDIENTE DE PUBLICAR EN YOUTUBE
```
