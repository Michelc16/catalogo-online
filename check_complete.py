# Crie check_complete.py
import os
import sqlite3
from flask import Flask
from models import db, Product

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Configuração IDÊNTICA ao seu app.py
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://')
    print("🌐 Usando PostgreSQL (Render)")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "catalogo.db")}'
    print("💻 Usando SQLite local")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Contar produtos via SQLAlchemy
    product_count = Product.query.count()
    print(f"🛍️  Produtos no banco (SQLAlchemy): {product_count}")
    
    # Verificar via SQL direto
    try:
        conn = sqlite3.connect('catalogo.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM product")
        sqlite_count = cursor.fetchone()[0]
        print(f"🛍️  Produtos no SQLite direto: {sqlite_count}")
        conn.close()
    except Exception as e:
        print(f"❌ Erro SQLite: {e}")

print("🔍 DATABASE_URL:", os.environ.get('DATABASE_URL', 'Não definido'))