import sqlite3
import os

def check_database():
    print("=== VERIFICANDO BANCO DE DADOS ===")
    
    # Possíveis locais do banco
    possible_dbs = [
        'catalogo.db',
        'instance/catalogo.db',
        '../catalogo.db',
        'database/catalogo.db'
    ]
    
    for db_file in possible_dbs:
        if os.path.exists(db_file):
            print(f"✅ Banco encontrado: {db_file}")
            
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Verificar tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                print(f"📊 Tabelas encontradas: {[table[0] for table in tables]}")
                
                # Verificar produtos
                if 'product' in [table[0] for table in tables]:
                    cursor.execute("SELECT COUNT(*) FROM product")
                    count = cursor.fetchone()[0]
                    print(f"🛍️  Total de produtos: {count}")
                    
                    # Mostrar alguns produtos
                    cursor.execute("SELECT id, name, price FROM product LIMIT 5")
                    products = cursor.fetchall()
                    print("📦 Primeiros produtos:")
                    for product in products:
                        print(f"   - ID {product[0]}: {product[1]} - R$ {product[2]}")
                else:
                    print("❌ Tabela 'product' não encontrada!")
                
                conn.close()
                
            except Exception as e:
                print(f"❌ Erro ao acessar {db_file}: {e}")
        else:
            print(f"❌ {db_file} não encontrado")

if __name__ == '__main__':
    check_database()