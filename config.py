import os

# En local se usan estos valores. En hosting defina DB_HOST, DB_USER,
# DB_PASSWORD y DB_NAME sin guardar credenciales en el código.
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'pos_db'),
}
