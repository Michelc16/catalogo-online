# optimize.py
import os
import sys
from app import app, db, Product, User

def optimize_database():
    with app.app_context():
        print("🔄 Otimizando banco de dados...")
        
        # Limpar cache
        from app import cache
        cache.clear()
        print("✅ Cache limpo")
        
        # Estatísticas do banco
        product_count = Product.query.count()
        user_count = User.query.count()
        
        print(f"📊 Estatísticas:")
        print(f"   Produtos: {product_count}")
        print(f"   Usuários: {user_count}")
        
        print("🎯 Otimização concluída!")

if __name__ == "__main__":
    optimize_database()