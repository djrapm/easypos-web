# Despliegue de EasyPOS Web

## Ejecución local

1. Importe `database/schema.sql` en MySQL.
2. Ajuste las credenciales locales en `config.py` o defina estas variables de entorno: `DB_HOST`, `DB_USER`, `DB_PASSWORD` y `DB_NAME`.
3. Instale dependencias: `python -m pip install -r requirements.txt`.
4. Ejecute: `python web_app.py`.
5. Abra `http://127.0.0.1:5000`.

## Requisitos para un hosting

El hosting debe poder ejecutar aplicaciones Python WSGI y conectarse a una base MySQL remota. No suba `config.py` con una contraseña real; configure las credenciales como variables de entorno del hosting:

```text
DB_HOST=servidor-mysql
DB_PORT=3306
DB_USER=usuario-pos
DB_PASSWORD=contraseña-segura
DB_NAME=pos_db
SECRET_KEY=valor-largo-aleatorio
```

El comando de inicio es:

```text
gunicorn wsgi:app
```

El archivo `Procfile` ya contiene este comando para plataformas que lo detectan automáticamente.

## Antes de entregar

- Importe `database/schema.sql` en la base de datos remota.
- Cree las variables de entorno anteriores en el panel del hosting.
- Verifique la URL pública: inicio, registro de productos, una venta, una compra y reportes.
- Incluya la URL pública y el enlace del video de YouTube en `ENTREGA.md`.

> Para que Codex publique el sitio por usted todavía se necesita acceso a una cuenta de hosting y a una base MySQL remota. No comparta contraseñas en el código ni por el chat.
