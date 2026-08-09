import os
from datetime import datetime
from decimal import Decimal

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import DB_CONFIG

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cambie-esta-clave-para-produccion')


def conectar():
    return mysql.connector.connect(**DB_CONFIG)


def consultar(sql, parametros=(), uno=False):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(sql, parametros)
        return cursor.fetchone() if uno else cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


def ejecutar(sql, parametros=()):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute(sql, parametros)
        conexion.commit()
        return cursor.lastrowid
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def datos(sql):
    try:
        return consultar(sql)
    except mysql.connector.Error as error:
        flash(f'No se pudo conectar a MySQL: {error}', 'danger')
        return []


@app.template_filter('moneda')
def moneda(valor):
    return f"L. {float(valor or 0):,.2f}"


def total_carrito(nombre):
    return sum(Decimal(str(item['subtotal'])) for item in session.get(nombre, []))


@app.route('/')
def inicio():
    try:
        resumen = {
            'productos': consultar('SELECT COUNT(*) AS total FROM producto', uno=True)['total'],
            'clientes': consultar('SELECT COUNT(*) AS total FROM clientes', uno=True)['total'],
            'ventas_hoy': consultar('SELECT COUNT(*) AS total FROM facturas WHERE DATE(fecha) = CURDATE()', uno=True)['total'],
            'total_hoy': consultar('SELECT COALESCE(SUM(total), 0) AS total FROM facturas WHERE DATE(fecha) = CURDATE()', uno=True)['total'],
        }
        bajos = consultar('SELECT nombre_producto, stock_actual, stock_minimo FROM producto WHERE stock_actual <= stock_minimo ORDER BY stock_actual')
    except mysql.connector.Error as error:
        resumen, bajos = None, []
        flash(f'Importe database/schema.sql y configure MySQL. Detalle: {error}', 'warning')
    return render_template('inicio.html', resumen=resumen, bajos=bajos)


@app.route('/productos', methods=['GET', 'POST'])
def productos():
    if request.method == 'POST':
        try:
            ejecutar('''INSERT INTO producto (id_categoria, codigo_barra, nombre_producto, precio_compra, precio_venta, stock_actual, stock_minimo)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                     (int(request.form['id_categoria']), request.form['codigo_barra'].strip(), request.form['nombre_producto'].strip(),
                      float(request.form['precio_compra']), float(request.form['precio_venta']), int(request.form['stock_actual']), int(request.form['stock_minimo'])))
            flash('Producto registrado correctamente.', 'success')
        except (ValueError, mysql.connector.Error) as error:
            flash(f'No fue posible guardar el producto: {error}', 'danger')
        return redirect(url_for('productos'))
    return render_template('productos.html', productos=datos('''SELECT p.*, c.nombre_categoria FROM producto p
        JOIN categorias c ON c.id_categoria = p.id_categoria ORDER BY p.nombre_producto'''),
        categorias=datos('SELECT * FROM categorias ORDER BY nombre_categoria'))


@app.post('/categorias')
def categorias():
    try:
        nombre = request.form['nombre_categoria'].strip()
        if not nombre:
            raise ValueError('El nombre de categoría es obligatorio.')
        ejecutar('INSERT INTO categorias (nombre_categoria, descripcion) VALUES (%s, %s)',
                 (nombre, request.form.get('descripcion', '').strip()))
        flash('Categoría creada.', 'success')
    except (ValueError, mysql.connector.Error) as error:
        flash(f'No fue posible guardar la categoría: {error}', 'danger')
    return redirect(url_for('productos'))


def directorio(tabla, columnas, titulo):
    if request.method == 'POST':
        valores = [request.form.get(campo, '').strip() for campo in columnas]
        try:
            if not valores[0]:
                raise ValueError('El primer campo es obligatorio.')
            ejecutar(f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({', '.join(['%s'] * len(columnas))})", valores)
            flash(f'{titulo[:-1]} registrado correctamente.', 'success')
        except (ValueError, mysql.connector.Error) as error:
            flash(f'No fue posible guardar el registro: {error}', 'danger')
        return redirect(request.path)
    return render_template('directorio.html', titulo=titulo, tabla=tabla, columnas=columnas,
                           registros=datos(f'SELECT * FROM {tabla} ORDER BY 1 DESC'))


@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    return directorio('clientes', ['nombre_cliente', 'dni', 'telefono', 'direccion'], 'Clientes')


@app.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    return directorio('proveedores', ['nombre_empresa', 'telefono', 'rtn', 'contacto'], 'Proveedores')


@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    return directorio('usuarios', ['nombre_usuario', 'contrasena', 'rol'], 'Usuarios')


@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if request.method == 'POST':
        try:
            codigo, cantidad = request.form['codigo_barra'].strip(), int(request.form['cantidad'])
            producto = consultar('SELECT * FROM producto WHERE codigo_barra = %s', (codigo,), uno=True)
            carrito = session.get('carrito_venta', [])
            reservado = sum(x['cantidad'] for x in carrito if producto and x['id_producto'] == producto['id_producto'])
            if not producto or cantidad <= 0 or producto['stock_actual'] < reservado + cantidad:
                raise ValueError('Producto inexistente, cantidad inválida o stock insuficiente.')
            carrito.append({'id_producto': producto['id_producto'], 'codigo': producto['codigo_barra'], 'nombre': producto['nombre_producto'],
                            'cantidad': cantidad, 'precio': float(producto['precio_venta']), 'subtotal': float(producto['precio_venta']) * cantidad})
            session['carrito_venta'] = carrito
            flash('Producto agregado a la venta.', 'success')
        except (KeyError, TypeError, ValueError) as error:
            flash(str(error), 'danger')
        return redirect(url_for('ventas'))
    subtotal = total_carrito('carrito_venta')
    return render_template('ventas.html', clientes=datos('SELECT * FROM clientes ORDER BY nombre_cliente'),
        usuarios=datos('SELECT * FROM usuarios ORDER BY nombre_usuario'), carrito=session.get('carrito_venta', []), subtotal=subtotal,
        impuesto=subtotal * Decimal('0.15'), total=subtotal * Decimal('1.15'))


@app.post('/ventas/confirmar')
def confirmar_venta():
    carrito = session.get('carrito_venta', [])
    try:
        if not carrito:
            raise ValueError('Agregue al menos un producto a la venta.')
        cliente, usuario = int(request.form['id_cliente']), int(request.form['id_usuario'])
        subtotal = total_carrito('carrito_venta'); impuesto = subtotal * Decimal('0.15'); total = subtotal + impuesto
        conexion = conectar(); cursor = conexion.cursor(); numero = f"FAC-{datetime.now():%Y%m%d%H%M%S%f}"
        try:
            cursor.execute('INSERT INTO facturas (id_cliente, id_usuario, numero_factura, subtotal, impuesto, total) VALUES (%s, %s, %s, %s, %s, %s)',
                           (cliente, usuario, numero, subtotal, impuesto, total))
            factura = cursor.lastrowid
            for item in carrito:
                cursor.execute('UPDATE producto SET stock_actual = stock_actual - %s WHERE id_producto = %s AND stock_actual >= %s',
                               (item['cantidad'], item['id_producto'], item['cantidad']))
                if cursor.rowcount != 1:
                    raise ValueError(f"Stock insuficiente para {item['nombre']}.")
                cursor.execute('INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)',
                               (factura, item['id_producto'], item['cantidad'], item['precio']))
            conexion.commit()
        except Exception:
            conexion.rollback(); raise
        finally:
            cursor.close(); conexion.close()
        session.pop('carrito_venta', None)
        flash(f'Factura {numero} guardada correctamente.', 'success')
    except (ValueError, mysql.connector.Error) as error:
        flash(f'No fue posible procesar la venta: {error}', 'danger')
    return redirect(url_for('ventas'))


@app.post('/ventas/limpiar')
def limpiar_venta():
    session.pop('carrito_venta', None)
    return redirect(url_for('ventas'))


@app.route('/compras', methods=['GET', 'POST'])
def compras():
    if request.method == 'POST':
        try:
            producto = consultar('SELECT * FROM producto WHERE id_producto = %s', (int(request.form['id_producto']),), uno=True)
            cantidad, costo = int(request.form['cantidad']), float(request.form['costo'])
            if not producto or cantidad <= 0 or costo < 0:
                raise ValueError('Datos de compra inválidos.')
            carrito = session.get('carrito_compra', [])
            carrito.append({'id_producto': producto['id_producto'], 'nombre': producto['nombre_producto'],
                            'cantidad': cantidad, 'costo': costo, 'subtotal': cantidad * costo})
            session['carrito_compra'] = carrito
            flash('Producto agregado a la compra.', 'success')
        except (ValueError, TypeError) as error:
            flash(str(error), 'danger')
        return redirect(url_for('compras'))
    return render_template('compras.html', proveedores=datos('SELECT * FROM proveedores ORDER BY nombre_empresa'),
        usuarios=datos('SELECT * FROM usuarios ORDER BY nombre_usuario'), productos=datos('SELECT * FROM producto ORDER BY nombre_producto'),
        carrito=session.get('carrito_compra', []), total=total_carrito('carrito_compra'))


@app.post('/compras/confirmar')
def confirmar_compra():
    carrito = session.get('carrito_compra', [])
    try:
        if not carrito:
            raise ValueError('Agregue al menos un producto a la compra.')
        proveedor, usuario = int(request.form['id_proveedor']), int(request.form['id_usuario'])
        referencia = request.form['numero_referencia'].strip()
        if not referencia:
            raise ValueError('La referencia es obligatoria.')
        conexion = conectar(); cursor = conexion.cursor()
        try:
            cursor.execute('INSERT INTO compras (id_proveedor, id_usuario, numero_referencia, total) VALUES (%s, %s, %s, %s)',
                           (proveedor, usuario, referencia, total_carrito('carrito_compra')))
            compra = cursor.lastrowid
            for item in carrito:
                cursor.execute('INSERT INTO detalle_compras (id_compra, id_producto, cantidad, costo_unitario) VALUES (%s, %s, %s, %s)',
                               (compra, item['id_producto'], item['cantidad'], item['costo']))
                cursor.execute('UPDATE producto SET stock_actual = stock_actual + %s WHERE id_producto = %s', (item['cantidad'], item['id_producto']))
            conexion.commit()
        except Exception:
            conexion.rollback(); raise
        finally:
            cursor.close(); conexion.close()
        session.pop('carrito_compra', None)
        flash(f'Compra {referencia} guardada correctamente.', 'success')
    except (ValueError, mysql.connector.Error) as error:
        flash(f'No fue posible procesar la compra: {error}', 'danger')
    return redirect(url_for('compras'))


@app.post('/compras/limpiar')
def limpiar_compra():
    session.pop('carrito_compra', None)
    return redirect(url_for('compras'))


@app.route('/reportes')
def reportes():
    return render_template('reportes.html', inventario=datos('''SELECT codigo_barra, nombre_producto, stock_actual, stock_minimo,
        CASE WHEN stock_actual <= stock_minimo THEN 'REABASTECER' ELSE 'OK' END AS estado FROM producto ORDER BY nombre_producto'''),
        ventas=datos('''SELECT f.numero_factura, f.fecha, c.nombre_cliente, f.total FROM facturas f JOIN clientes c ON c.id_cliente = f.id_cliente
        WHERE DATE(f.fecha) = CURDATE() ORDER BY f.fecha DESC'''),
        compras=datos('''SELECT c.numero_referencia, c.fecha, p.nombre_empresa, c.total FROM compras c JOIN proveedores p ON p.id_proveedor = c.id_proveedor
        WHERE DATE(c.fecha) = CURDATE() ORDER BY c.fecha DESC'''))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
