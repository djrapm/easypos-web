import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import DB_CONFIG

def obtener_conexion():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a MySQL:\n{err}")
        return None

class SistemaPOSOficial:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema POS e Inventario - Control Total")
        self.root.geometry("1100x700")

        self.carrito_venta = []
        self.carrito_compra = []

        # Notebook (Pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Modulos
        self.tab_ventas = ttk.Frame(self.notebook)
        self.tab_productos = ttk.Frame(self.notebook)
        self.tab_compras = ttk.Frame(self.notebook)
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_proveedores = ttk.Frame(self.notebook)
        self.tab_usuarios = ttk.Frame(self.notebook)
        self.tab_reportes = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_ventas, text=" 🛒 Ventas ")
        self.notebook.add(self.tab_productos, text=" 📦 Productos / Categorías ")
        self.notebook.add(self.tab_compras, text=" 🚚 Compras ")
        self.notebook.add(self.tab_clientes, text=" 👥 Clientes ")
        self.notebook.add(self.tab_proveedores, text=" 🏢 Proveedores ")
        self.notebook.add(self.tab_usuarios, text=" 👤 Usuarios ")
        self.notebook.add(self.tab_reportes, text=" 📊 Reportes ")

        self.crear_modulo_ventas()
        self.crear_modulo_productos()
        self.crear_modulo_compras()
        self.crear_modulo_clientes()
        self.crear_modulo_proveedores()
        self.crear_modulo_usuarios()
        self.crear_modulo_reportes()

    # ==========================================
    # 1. VENTAS / FACTURAS / DETALLE FACTURA
    # ==========================================
    def crear_modulo_ventas(self):
        lbl = tk.Label(self.tab_ventas, text="MODULO DE VENTAS (FACTURACIÓN)", font=("Arial", 14, "bold"), bg="#2c3e50", fg="white", pady=6)
        lbl.pack(fill=tk.X)

        datos = tk.LabelFrame(self.tab_ventas, text="Datos de la factura", padx=10, pady=5)
        datos.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(datos, text="Cliente:").grid(row=0, column=0)
        self.cmb_v_cliente = ttk.Combobox(datos, state="readonly", width=32)
        self.cmb_v_cliente.grid(row=0, column=1, padx=5)
        tk.Label(datos, text="Usuario:").grid(row=0, column=2)
        self.cmb_v_usuario = ttk.Combobox(datos, state="readonly", width=25)
        self.cmb_v_usuario.grid(row=0, column=3, padx=5)
        self.actualizar_combos_venta()

        frame = tk.LabelFrame(self.tab_ventas, text="Agregar Producto a Venta", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(frame, text="Código Barra:").grid(row=0, column=0)
        self.ent_v_cod = tk.Entry(frame, width=15)
        self.ent_v_cod.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Cantidad:").grid(row=0, column=2)
        self.ent_v_cant = tk.Entry(frame, width=8)
        self.ent_v_cant.insert(0, "1")
        self.ent_v_cant.grid(row=0, column=3, padx=5)

        btn_add = tk.Button(frame, text="Añadir a Factura", bg="#27ae60", fg="white", font=("Arial", 9, "bold"), command=self.add_venta_item)
        btn_add.grid(row=0, column=4, padx=10)

        cols = ("id", "codigo", "nombre", "precio_unitario", "cantidad", "subtotal")
        self.tabla_v = ttk.Treeview(self.tab_ventas, columns=cols, show="headings", height=8)
        for c, t in zip(cols, ["ID Prod", "Código", "Nombre del Producto", "Precio Unitario", "Cantidad", "Subtotal"]):
            self.tabla_v.heading(c, text=t)
            self.tabla_v.column(c, anchor="center")
        self.tabla_v.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        frame_tot = tk.Frame(self.tab_ventas)
        frame_tot.pack(fill=tk.X, padx=15, pady=10)

        self.lbl_v_resumen = tk.Label(frame_tot, text="Subtotal: L.0.00 | Impuesto (15%): L.0.00 | Total: L.0.00", font=("Arial", 12, "bold"), fg="#c0392b")
        self.lbl_v_resumen.pack(side=tk.LEFT)

        btn_facturar = tk.Button(frame_tot, text="PROCESAR Y GUARDAR FACTURA", bg="#2980b9", fg="white", font=("Arial", 11, "bold"), command=self.procesar_factura)
        btn_facturar.pack(side=tk.RIGHT)

    def add_venta_item(self):
        cod, cant_s = self.ent_v_cod.get().strip(), self.ent_v_cant.get().strip()
        if not cod or not cant_s.isdigit(): 
            messagebox.showwarning("Atención", "Ingrese código y cantidad válida.")
            return

        cant = int(cant_s)
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM producto WHERE codigo_barra = %s", (cod,))
        prod = cursor.fetchone()
        conn.close()

        if not prod:
            messagebox.showerror("Error", "Producto no encontrado.")
            return

        cantidad_en_carrito = sum(item['cant'] for item in self.carrito_venta if item['id'] == prod['id_producto'])
        if prod['stock_actual'] < cantidad_en_carrito + cant:
            messagebox.showwarning("Stock Insuficiente", f"Solo quedan {prod['stock_actual']} unidades en stock.")
            return

        precio_u = float(prod['precio_venta'])
        sub = precio_u * cant
        self.carrito_venta.append({'id': prod['id_producto'], 'codigo': cod, 'nombre': prod['nombre_producto'], 'precio_u': precio_u, 'cant': cant, 'sub': sub})
        
        self.tabla_v.insert("", tk.END, values=(prod['id_producto'], cod, prod['nombre_producto'], f"L.{precio_u:.2f}", cant, f"L.{sub:.2f}"))
        self.actualizar_totales_venta()
        self.ent_v_cod.delete(0, tk.END)

    def actualizar_totales_venta(self):
        subtotal = sum(x['sub'] for x in self.carrito_venta)
        impuesto = subtotal * 0.15
        total = subtotal + impuesto
        self.lbl_v_resumen.config(text=f"Subtotal: L.{subtotal:.2f} | Impuesto: L.{impuesto:.2f} | Total: L.{total:.2f}")

    def procesar_factura(self):
        if not self.carrito_venta:
            messagebox.showwarning("Atención", "Agregue al menos un producto a la factura.")
            return
        if not self.cmb_v_cliente.get() or not self.cmb_v_usuario.get():
            messagebox.showwarning("Atención", "Seleccione un cliente y un usuario.")
            return
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()

        subtotal = sum(x['sub'] for x in self.carrito_venta)
        impuesto = subtotal * 0.15
        total = subtotal + impuesto
        id_cliente = int(self.cmb_v_cliente.get().split(' - ')[0])
        id_usuario = int(self.cmb_v_usuario.get().split(' - ')[0])

        try:
            cursor.execute("INSERT INTO facturas (id_cliente, id_usuario, numero_factura, subtotal, impuesto, total) VALUES (%s, %s, %s, %s, %s, %s)",
                           (id_cliente, id_usuario, f"FAC-{__import__('datetime').datetime.now():%Y%m%d%H%M%S%f}", subtotal, impuesto, total))
            id_f = cursor.lastrowid

            for item in self.carrito_venta:
                cursor.execute("INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)", 
                               (id_f, item['id'], item['cant'], item['precio_u']))
                cursor.execute("UPDATE producto SET stock_actual = stock_actual - %s WHERE id_producto = %s", (item['cant'], item['id']))
            
            conn.commit()
            messagebox.showinfo("Éxito", f"Factura #{id_f} procesada exitosamente.")
            self.carrito_venta.clear()
            for r in self.tabla_v.get_children(): self.tabla_v.delete(r)
            self.actualizar_totales_venta()
            self.cargar_productos_tabla()
            self.actualizar_combos_compras()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error en Venta", str(e))
        finally:
            conn.close()

    def actualizar_combos_venta(self):
        conn = obtener_conexion()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_cliente, nombre_cliente FROM clientes ORDER BY nombre_cliente")
        clientes = cursor.fetchall()
        self.cmb_v_cliente['values'] = [f"{x['id_cliente']} - {x['nombre_cliente']}" for x in clientes]
        if clientes:
            self.cmb_v_cliente.current(0)
        cursor.execute("SELECT id_usuario, nombre_usuario FROM usuarios ORDER BY nombre_usuario")
        usuarios = cursor.fetchall()
        self.cmb_v_usuario['values'] = [f"{x['id_usuario']} - {x['nombre_usuario']}" for x in usuarios]
        if usuarios:
            self.cmb_v_usuario.current(0)
        conn.close()

    # ==========================================
    # 2. PRODUCTOS Y CATEGORÍAS
    # ==========================================
    def crear_modulo_productos(self):
        lbl = tk.Label(self.tab_productos, text="CATÁLOGO DE PRODUCTOS Y CATEGORÍAS", font=("Arial", 14, "bold"), bg="#34495e", fg="white", pady=6)
        lbl.pack(fill=tk.X)

        frame_cat = tk.LabelFrame(self.tab_productos, text="Registrar Categoría", padx=10, pady=5)
        frame_cat.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(frame_cat, text="Nombre Categoría:").grid(row=0, column=0)
        self.ent_cat_nom = tk.Entry(frame_cat)
        self.ent_cat_nom.grid(row=0, column=1, padx=5)

        tk.Label(frame_cat, text="Descripción:").grid(row=0, column=2)
        self.ent_cat_des = tk.Entry(frame_cat)
        self.ent_cat_des.grid(row=0, column=3, padx=5)

        btn_cat = tk.Button(frame_cat, text="Guardar Categoría", bg="#16a085", fg="white", command=self.guardar_categoria)
        btn_cat.grid(row=0, column=4, padx=5)

        frame_prod = tk.LabelFrame(self.tab_productos, text="Registrar Producto", padx=10, pady=5)
        frame_prod.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(frame_prod, text="Código Barra:").grid(row=0, column=0)
        self.ent_p_cod = tk.Entry(frame_prod)
        self.ent_p_cod.grid(row=0, column=1)

        tk.Label(frame_prod, text="Nombre Producto:").grid(row=0, column=2)
        self.ent_p_nom = tk.Entry(frame_prod)
        self.ent_p_nom.grid(row=0, column=3)

        tk.Label(frame_prod, text="Categoría:").grid(row=0, column=4)
        self.cmb_p_categoria = ttk.Combobox(frame_prod, state="readonly", width=20)
        self.cmb_p_categoria.grid(row=0, column=5, padx=5)

        tk.Label(frame_prod, text="Precio Compra:").grid(row=1, column=0)
        self.ent_p_pc = tk.Entry(frame_prod)
        self.ent_p_pc.grid(row=1, column=1)

        tk.Label(frame_prod, text="Precio Venta:").grid(row=1, column=2)
        self.ent_p_pv = tk.Entry(frame_prod)
        self.ent_p_pv.grid(row=1, column=3)

        tk.Label(frame_prod, text="Stock Inicial:").grid(row=2, column=0)
        self.ent_p_stok = tk.Entry(frame_prod)
        self.ent_p_stok.grid(row=2, column=1)

        btn_p = tk.Button(frame_prod, text="Guardar Producto", bg="#27ae60", fg="white", font=("Arial", 9, "bold"), command=self.guardar_producto)
        btn_p.grid(row=2, column=3, pady=5)

        cols = ("id", "codigo", "nombre", "p_compra", "p_venta", "stock_actual")
        self.tabla_p = ttk.Treeview(self.tab_productos, columns=cols, show="headings", height=8)
        for c, t in zip(cols, ["ID", "Código Barra", "Nombre del Producto", "Precio Compra", "Precio Venta", "Stock Actual"]):
            self.tabla_p.heading(c, text=t)
            self.tabla_p.column(c, anchor="center")
        self.tabla_p.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.cargar_productos_tabla()
        self.actualizar_combos_categorias()

    def guardar_categoria(self):
        cat = self.ent_cat_nom.get().strip()
        des = self.ent_cat_des.get().strip()
        if not cat: return
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorias (nombre_categoria, descripcion) VALUES (%s, %s)", (cat, des))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Categoría registrada correctamente.")
        self.ent_cat_nom.delete(0, tk.END)
        self.ent_cat_des.delete(0, tk.END)
        self.actualizar_combos_categorias()

    def actualizar_combos_categorias(self):
        conn = obtener_conexion()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria")
        categorias = cursor.fetchall()
        self.cmb_p_categoria['values'] = [f"{c['id_categoria']} - {c['nombre_categoria']}" for c in categorias]
        if categorias:
            self.cmb_p_categoria.current(0)
        conn.close()

    def guardar_producto(self):
        cod, nom = self.ent_p_cod.get().strip(), self.ent_p_nom.get().strip()
        pc, pv, st = self.ent_p_pc.get().strip(), self.ent_p_pv.get().strip(), self.ent_p_stok.get().strip()
        categoria = self.cmb_p_categoria.get()
        if not (cod and nom and pc and pv and st and categoria):
            messagebox.showwarning("Atención", "Complete todos los campos del producto.")
            return

        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        try:
            id_categoria = int(categoria.split(' - ')[0])
            cursor.execute("INSERT INTO producto (id_categoria, codigo_barra, nombre_producto, precio_compra, precio_venta, stock_actual, stock_minimo) VALUES (%s, %s, %s, %s, %s, %s, 5)",
                           (id_categoria, cod, nom, float(pc), float(pv), int(st)))
            conn.commit()
            messagebox.showinfo("Éxito", "Producto guardado con éxito.")
            self.cargar_productos_tabla()
            self.actualizar_combos_compras()
            self.ent_p_cod.delete(0, tk.END)
            self.ent_p_nom.delete(0, tk.END)
            self.ent_p_pc.delete(0, tk.END)
            self.ent_p_pv.delete(0, tk.END)
            self.ent_p_stok.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def cargar_productos_tabla(self):
        for r in self.tabla_p.get_children(): self.tabla_p.delete(r)
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT id_producto, codigo_barra, nombre_producto, precio_compra, precio_venta, stock_actual FROM producto")
        for r in cursor.fetchall():
            self.tabla_p.insert("", tk.END, values=r)
        conn.close()

    # ==========================================
    # 3. COMPRAS / DETALE COMPRAS
    # ==========================================
    def crear_modulo_compras(self):
        lbl = tk.Label(self.tab_compras, text="REGISTRO DE COMPRAS A PROVEEDORES", font=("Arial", 14, "bold"), bg="#e67e22", fg="white", pady=6)
        lbl.pack(fill=tk.X)

        frame_prov = tk.LabelFrame(self.tab_compras, text="1. Datos de la Compra", padx=10, pady=5)
        frame_prov.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(frame_prov, text="Seleccionar Proveedor:").grid(row=0, column=0, padx=5)
        self.cmb_c_proveedor = ttk.Combobox(frame_prov, state="readonly", width=35)
        self.cmb_c_proveedor.grid(row=0, column=1, padx=5)

        tk.Label(frame_prov, text="Usuario:").grid(row=0, column=2, padx=5)
        self.cmb_c_usuario = ttk.Combobox(frame_prov, state="readonly", width=22)
        self.cmb_c_usuario.grid(row=0, column=3, padx=5)

        tk.Label(frame_prov, text="N° Referencia / Factura:").grid(row=1, column=0, padx=5)
        self.ent_c_ref = tk.Entry(frame_prov, width=15)
        self.ent_c_ref.insert(0, "REF-001")
        self.ent_c_ref.grid(row=1, column=1, padx=5)

        frame_item = tk.LabelFrame(self.tab_compras, text="2. Agregar Producto a la Compra", padx=10, pady=5)
        frame_item.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(frame_item, text="Producto:").grid(row=0, column=0, padx=5)
        self.cmb_c_producto = ttk.Combobox(frame_item, state="readonly", width=35)
        self.cmb_c_producto.grid(row=0, column=1, padx=5)

        tk.Label(frame_item, text="Cantidad Aumentar:").grid(row=0, column=2, padx=5)
        self.ent_c_cant = tk.Entry(frame_item, width=8)
        self.ent_c_cant.insert(0, "1")
        self.ent_c_cant.grid(row=0, column=3, padx=5)

        tk.Label(frame_item, text="Costo Unitario (L.):").grid(row=0, column=4, padx=5)
        self.ent_c_costo = tk.Entry(frame_item, width=10)
        self.ent_c_costo.grid(row=0, column=5, padx=5)

        btn_add = tk.Button(frame_item, text="➕ Añadir a la Lista", bg="#27ae60", fg="white", font=("Arial", 9, "bold"), command=self.add_compra_item)
        btn_add.grid(row=0, column=6, padx=10)

        cols = ("id_p", "producto", "cantidad", "costo_unitario", "subtotal")
        self.tabla_c = ttk.Treeview(self.tab_compras, columns=cols, show="headings", height=7)
        for c, t in zip(cols, ["ID Prod", "Nombre Producto", "Cantidad Ingresada", "Costo Unitario", "Subtotal"]):
            self.tabla_c.heading(c, text=t)
            self.tabla_c.column(c, anchor="center")
        self.tabla_c.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        frame_bot = tk.Frame(self.tab_compras)
        frame_bot.pack(fill=tk.X, padx=15, pady=10)

        self.lbl_c_total = tk.Label(frame_bot, text="Total Compra: L.0.00", font=("Arial", 12, "bold"), fg="#d35400")
        self.lbl_c_total.pack(side=tk.LEFT)

        btn_proc = tk.Button(frame_bot, text="💾 GUARDAR COMPRA Y SUMAR AL STOCK", bg="#d35400", fg="white", font=("Arial", 11, "bold"), command=self.procesar_compra)
        btn_proc.pack(side=tk.RIGHT)

        self.actualizar_combos_compras()

    def actualizar_combos_compras(self):
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_proveedor, nombre_empresa FROM proveedores")
        provs = cursor.fetchall()
        self.cmb_c_proveedor['values'] = [f"{p['id_proveedor']} - {p['nombre_empresa']}" for p in provs]
        if provs: self.cmb_c_proveedor.current(0)

        cursor.execute("SELECT id_usuario, nombre_usuario FROM usuarios ORDER BY nombre_usuario")
        usuarios = cursor.fetchall()
        self.cmb_c_usuario['values'] = [f"{u['id_usuario']} - {u['nombre_usuario']}" for u in usuarios]
        if usuarios: self.cmb_c_usuario.current(0)

        cursor.execute("SELECT id_producto, nombre_producto, stock_actual FROM producto")
        prods = cursor.fetchall()
        self.cmb_c_producto['values'] = [f"{p['id_producto']} - {p['nombre_producto']} (Stock actual: {p['stock_actual']})" for p in prods]
        if prods: self.cmb_c_producto.current(0)

        conn.close()

    def add_compra_item(self):
        prod_sel = self.cmb_c_producto.get()
        cant_s = self.ent_c_cant.get().strip()
        costo_s = self.ent_c_costo.get().strip()

        if not prod_sel or not cant_s.isdigit() or not costo_s:
            messagebox.showwarning("Atención", "Seleccione un producto e ingrese cantidad y costo válidos.")
            return

        id_p = int(prod_sel.split(' - ')[0])
        nombre_p = prod_sel.split(' - ')[1].split(' (Stock')[0]
        cant = int(cant_s)
        try:
            costo = float(costo_s)
        except ValueError:
            messagebox.showwarning("Atención", "El costo unitario debe ser numérico.")
            return
        if cant <= 0 or costo < 0:
            messagebox.showwarning("Atención", "La cantidad debe ser mayor que cero y el costo no puede ser negativo.")
            return
        sub = cant * costo

        self.carrito_compra.append({'id_p': id_p, 'nombre': nombre_p, 'cant': cant, 'costo': costo, 'sub': sub})
        self.tabla_c.insert("", tk.END, values=(id_p, nombre_p, cant, f"L.{costo:.2f}", f"L.{sub:.2f}"))

        tot = sum(x['sub'] for x in self.carrito_compra)
        self.lbl_c_total.config(text=f"Total Compra: L.{tot:.2f}")

    def procesar_compra(self):
        prov_sel = self.cmb_c_proveedor.get()
        if not self.carrito_compra:
            messagebox.showwarning("Atención", "No hay productos añadidos a la lista de compra.")
            return
        if not prov_sel:
            messagebox.showwarning("Atención", "Seleccione un proveedor.")
            return
        if not self.cmb_c_usuario.get() or not self.ent_c_ref.get().strip():
            messagebox.showwarning("Atención", "Seleccione un usuario e ingrese la referencia.")
            return

        id_prov = int(prov_sel.split(' - ')[0])
        id_usuario = int(self.cmb_c_usuario.get().split(' - ')[0])
        ref = self.ent_c_ref.get().strip()

        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        tot = sum(x['sub'] for x in self.carrito_compra)

        try:
            cursor.execute("INSERT INTO compras (id_proveedor, id_usuario, numero_referencia, total) VALUES (%s, %s, %s, %s)",
                           (id_prov, id_usuario, ref, tot))
            id_c = cursor.lastrowid

            for x in self.carrito_compra:
                cursor.execute("INSERT INTO detalle_compras (id_compra, id_producto, cantidad, costo_unitario) VALUES (%s, %s, %s, %s)", 
                               (id_c, x['id_p'], x['cant'], x['costo']))
                cursor.execute("UPDATE producto SET stock_actual = stock_actual + %s WHERE id_producto = %s", (x['cant'], x['id_p']))
            
            conn.commit()
            messagebox.showinfo("¡Éxito!", f"Compra #{id_c} guardada exitosamente.\n\n¡El stock de los productos ha sido actualizado!")

            self.carrito_compra.clear()
            for r in self.tabla_c.get_children(): self.tabla_c.delete(r)
            self.lbl_c_total.config(text="Total Compra: L.0.00")
            
            self.actualizar_combos_compras()
            self.cargar_productos_tabla()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error en Compra", str(e))
        finally:
            conn.close()

    # ==========================================
    # 4. CLIENTES
    # ==========================================
    def crear_modulo_clientes(self):
        lbl = tk.Label(self.tab_clientes, text="DIRECTORIO DE CLIENTES", font=("Arial", 14, "bold"), bg="#2980b9", fg="white", pady=6)
        lbl.pack(fill=tk.X)

        frame = tk.LabelFrame(self.tab_clientes, text="Registrar Cliente", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(frame, text="Nombre:").grid(row=0, column=0)
        self.ent_cli_nom = tk.Entry(frame)
        self.ent_cli_nom.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="DNI:").grid(row=0, column=2)
        self.ent_cli_dni = tk.Entry(frame)
        self.ent_cli_dni.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame, text="Teléfono:").grid(row=1, column=0)
        self.ent_cli_tel = tk.Entry(frame)
        self.ent_cli_tel.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Dirección:").grid(row=1, column=2)
        self.ent_cli_dir = tk.Entry(frame)
        self.ent_cli_dir.grid(row=1, column=3, padx=5, pady=5)

        btn_cli = tk.Button(frame, text="Guardar Cliente", bg="#2980b9", fg="white", font=("Arial", 9, "bold"), command=self.guardar_cliente)
        btn_cli.grid(row=2, column=3, pady=5)

        cols = ("id", "nombre", "dni", "telefono", "direccion")
        self.tabla_cli = ttk.Treeview(self.tab_clientes, columns=cols, show="headings", height=8)
        for c, t in zip(cols, ["ID", "Nombre Cliente", "DNI", "Teléfono", "Dirección"]):
            self.tabla_cli.heading(c, text=t)
            self.tabla_cli.column(c, anchor="center")
        self.tabla_cli.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.cargar_clientes_tabla()

    def guardar_cliente(self):
        nom, dni = self.ent_cli_nom.get().strip(), self.ent_cli_dni.get().strip()
        tel, dir_c = self.ent_cli_tel.get().strip(), self.ent_cli_dir.get().strip()
        if not nom: return

        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nombre_cliente, dni, telefono, direccion) VALUES (%s, %s, %s, %s)", (nom, dni, tel, dir_c))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Cliente registrado con éxito.")
        self.cargar_clientes_tabla()
        self.actualizar_combos_venta()

    def cargar_clientes_tabla(self):
        for r in self.tabla_cli.get_children(): self.tabla_cli.delete(r)
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT id_cliente, nombre_cliente, dni, telefono, direccion FROM clientes")
        for r in cursor.fetchall():
            self.tabla_cli.insert("", tk.END, values=r)
        conn.close()

    # ==========================================
    # 5. PROVEEDORES
    # ==========================================
    def crear_modulo_proveedores(self):
        lbl = tk.Label(self.tab_proveedores, text="DIRECTORIO DE PROVEEDORES", font=("Arial", 14, "bold"), bg="#8e44ad", fg="white", pady=6)
        lbl.pack(fill=tk.X)

        frame = tk.LabelFrame(self.tab_proveedores, text="Registrar Proveedor", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(frame, text="Nombre Empresa:").grid(row=0, column=0)
        self.ent_prov_emp = tk.Entry(frame)
        self.ent_prov_emp.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Teléfono:").grid(row=0, column=2)
        self.ent_prov_tel = tk.Entry(frame)
        self.ent_prov_tel.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame, text="RTN:").grid(row=1, column=0)
        self.ent_prov_rtn = tk.Entry(frame)
        self.ent_prov_rtn.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Contacto:").grid(row=1, column=2)
        self.ent_prov_con = tk.Entry(frame)
        self.ent_prov_con.grid(row=1, column=3, padx=5, pady=5)

        btn_pr = tk.Button(frame, text="Guardar Proveedor", bg="#8e44ad", fg="white", font=("Arial", 9, "bold"), command=self.guardar_proveedor)
        btn_pr.grid(row=2, column=3, pady=5)

        cols = ("id", "empresa", "telefono", "rtn", "contacto")
        self.tabla_pr = ttk.Treeview(self.tab_proveedores, columns=cols, show="headings", height=8)
        for c, t in zip(cols, ["ID", "Nombre Empresa", "Teléfono", "RTN", "Contacto"]):
            self.tabla_pr.heading(c, text=t)
            self.tabla_pr.column(c, anchor="center")
        self.tabla_pr.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.cargar_proveedores_tabla()

    def guardar_proveedor(self):
        emp, tel = self.ent_prov_emp.get().strip(), self.ent_prov_tel.get().strip()
        rtn, con = self.ent_prov_rtn.get().strip(), self.ent_prov_con.get().strip()
        if not emp: return

        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO proveedores (nombre_empresa, telefono, rtn, contacto) VALUES (%s, %s, %s, %s)", (emp, tel, rtn, con))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Proveedor registrado con éxito.")
        self.cargar_proveedores_tabla()
        self.actualizar_combos_compras()

    def cargar_proveedores_tabla(self):
        for r in self.tabla_pr.get_children(): self.tabla_pr.delete(r)
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT id_proveedor, nombre_empresa, telefono, rtn, contacto FROM proveedores")
        for r in cursor.fetchall():
            self.tabla_pr.insert("", tk.END, values=r)
        conn.close()

    # ==========================================
    # 6. USUARIOS
    # ==========================================
    def crear_modulo_usuarios(self):
        lbl = tk.Label(self.tab_usuarios, text="GESTIÓN DE USUARIOS DEL SISTEMA", font=("Arial", 14, "bold"), bg="#16a085", fg="white", pady=6)
        lbl.pack(fill=tk.X)

        frame = tk.LabelFrame(self.tab_usuarios, text="Registrar Usuario", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(frame, text="Nombre Usuario:").grid(row=0, column=0)
        self.ent_usr_nom = tk.Entry(frame)
        self.ent_usr_nom.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Contraseña:").grid(row=0, column=2)
        self.ent_usr_pas = tk.Entry(frame, show="*")
        self.ent_usr_pas.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame, text="Rol:").grid(row=1, column=0)
        self.ent_usr_rol = tk.Entry(frame)
        self.ent_usr_rol.grid(row=1, column=1, padx=5, pady=5)

        btn_u = tk.Button(frame, text="Guardar Usuario", bg="#16a085", fg="white", font=("Arial", 9, "bold"), command=self.guardar_usuario)
        btn_u.grid(row=1, column=3, pady=5)

        cols = ("id", "nombre", "rol")
        self.tabla_usr = ttk.Treeview(self.tab_usuarios, columns=cols, show="headings", height=8)
        for c, t in zip(cols, ["ID Usuario", "Nombre Usuario", "Rol"]):
            self.tabla_usr.heading(c, text=t)
            self.tabla_usr.column(c, anchor="center")
        self.tabla_usr.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.cargar_usuarios_tabla()

    def guardar_usuario(self):
        u, p, r = self.ent_usr_nom.get().strip(), self.ent_usr_pas.get().strip(), self.ent_usr_rol.get().strip()
        if not (u and p and r): return

        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre_usuario, contrasena, rol) VALUES (%s, %s, %s)", (u, p, r))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Usuario creado exitosamente.")
        self.cargar_usuarios_tabla()
        self.actualizar_combos_venta()
        self.actualizar_combos_compras()

    def cargar_usuarios_tabla(self):
        for r in self.tabla_usr.get_children(): self.tabla_usr.delete(r)
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre_usuario, rol FROM usuarios")
        for r in cursor.fetchall():
            self.tabla_usr.insert("", tk.END, values=r)
        conn.close()

    # ==========================================
    # 7. REPORTES
    # ==========================================
    def crear_modulo_reportes(self):
        tk.Label(self.tab_reportes, text="REPORTES DEL SISTEMA", font=("Arial", 14, "bold"), bg="#34495e", fg="white", pady=6).pack(fill=tk.X)
        botones = tk.Frame(self.tab_reportes)
        botones.pack(fill=tk.X, padx=15, pady=10)
        tk.Button(botones, text="Inventario y stock mínimo", command=self.reporte_inventario).pack(side=tk.LEFT, padx=5)
        tk.Button(botones, text="Ventas del día", command=self.reporte_ventas).pack(side=tk.LEFT, padx=5)
        tk.Button(botones, text="Compras del día", command=self.reporte_compras).pack(side=tk.LEFT, padx=5)
        self.txt_reporte = tk.Text(self.tab_reportes, height=24, font=("Consolas", 10))
        self.txt_reporte.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    def mostrar_reporte(self, titulo, columnas, filas):
        self.txt_reporte.delete("1.0", tk.END)
        self.txt_reporte.insert(tk.END, titulo + "\n" + "=" * 80 + "\n")
        self.txt_reporte.insert(tk.END, " | ".join(columnas) + "\n" + "-" * 80 + "\n")
        for fila in filas:
            self.txt_reporte.insert(tk.END, " | ".join(str(valor) for valor in fila) + "\n")
        self.txt_reporte.insert(tk.END, f"\nRegistros: {len(filas)}")

    def reporte_inventario(self):
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_barra, nombre_producto, stock_actual, stock_minimo, CASE WHEN stock_actual <= stock_minimo THEN 'REABASTECER' ELSE 'OK' END FROM producto ORDER BY nombre_producto")
        self.mostrar_reporte("INVENTARIO", ["Código", "Producto", "Actual", "Mínimo", "Estado"], cursor.fetchall())
        conn.close()

    def reporte_ventas(self):
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT numero_factura, fecha, nombre_cliente, total FROM facturas JOIN clientes USING(id_cliente) WHERE DATE(fecha) = CURDATE() ORDER BY fecha DESC")
        self.mostrar_reporte("VENTAS DEL DÍA", ["Factura", "Fecha", "Cliente", "Total"], cursor.fetchall())
        conn.close()

    def reporte_compras(self):
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT numero_referencia, fecha, nombre_empresa, total FROM compras JOIN proveedores USING(id_proveedor) WHERE DATE(fecha) = CURDATE() ORDER BY fecha DESC")
        self.mostrar_reporte("COMPRAS DEL DÍA", ["Referencia", "Fecha", "Proveedor", "Total"], cursor.fetchall())
        conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaPOSOficial(root)
    root.mainloop()
