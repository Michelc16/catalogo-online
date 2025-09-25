import sqlite3
import csv
import os
from datetime import datetime

def backup_database():
    """Faz backup dos produtos para CSV antes de atualizar"""
    try:
        # Conectar ao banco
        conn = sqlite3.connect('catalogo.db')
        cursor = conn.cursor()
        
        # Criar backup com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'backups/products_backup_{timestamp}.csv'
        
        # Criar diretório de backups
        os.makedirs('backups', exist_ok=True)
        
        # Exportar produtos para CSV
        cursor.execute('''
            SELECT name, description, price, category, image_url, created_at 
            FROM product
        ''')
        
        products = cursor.fetchall()
        
        with open(backup_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'description', 'price', 'category', 'image_url', 'created_at'])
            writer.writerows(products)
        
        print(f"✅ Backup criado: {backup_file} ({len(products)} produtos)")
        conn.close()
        return backup_file
        
    except Exception as e:
        print(f"❌ Erro no backup: {e}")
        return None

def restore_backup():
    """Restaura produtos do último backup"""
    try:
        # Encontrar o backup mais recente
        backup_files = [f for f in os.listdir('backups') if f.startswith('products_backup_')]
        if not backup_files:
            print("❌ Nenhum backup encontrado")
            return
        
        latest_backup = sorted(backup_files)[-1]
        backup_path = os.path.join('backups', latest_backup)
        
        # Restaurar dados
        conn = sqlite3.connect('catalogo.db')
        cursor = conn.cursor()
        
        with open(backup_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute('''
                    INSERT OR IGNORE INTO product 
                    (name, description, price, category, image_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (row['name'], row['description'], float(row['price']), 
                      row['category'], row['image_url'], row['created_at']))
        
        conn.commit()
        conn.close()
        print(f"✅ Backup restaurado: {latest_backup}")
        
    except Exception as e:
        print(f"❌ Erro na restauração: {e}")

if __name__ == '__main__':
    backup_database()