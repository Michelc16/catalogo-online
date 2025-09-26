import sqlite3
import csv
import json
import os
from datetime import datetime

class BackupManager:
    def __init__(self):
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        """Cria backup completo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            conn = sqlite3.connect('catalogo.db')
            cursor = conn.cursor()
            
            # Backup de produtos
            cursor.execute('SELECT * FROM product')
            products = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            # CSV (para Excel)
            csv_file = os.path.join(self.backup_dir, f'produtos_{timestamp}.csv')
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                for product in products:
                    # Converter dados para string
                    row = []
                    for item in product:
                        if hasattr(item, 'isoformat'):
                            row.append(item.isoformat())
                        else:
                            row.append(str(item) if item is not None else '')
                    writer.writerow(row)
            
            # JSON (para fácil leitura)
            json_file = os.path.join(self.backup_dir, f'backup_{timestamp}.json')
            backup_data = {
                'backup_date': timestamp,
                'total_products': len(products),
                'products': []
            }
            
            for product in products:
                product_dict = {}
                for i, column in enumerate(columns):
                    value = product[i]
                    if hasattr(value, 'isoformat'):
                        product_dict[column] = value.isoformat()
                    else:
                        product_dict[column] = value
                backup_data['products'].append(product_dict)
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            conn.close()
            
            print("📦 BACKUP CRIADO COM SUCESSO!")
            print(f"📊 Produtos: {len(products)}")
            print(f"📁 CSV: {csv_file}")
            print(f"📁 JSON: {json_file}")
            print(f"💾 Tamanho: {os.path.getsize(csv_file) / 1024:.1f} KB")
            
            return csv_file, json_file
            
        except Exception as e:
            print(f"❌ Erro no backup: {e}")
            return None, None
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.startswith('backup_') and file.endswith('.json'):
                backups.append(file)
        
        print("📋 BACKUPS DISPONÍVEIS:")
        for backup in sorted(backups, reverse=True)[:5]:  # Últimos 5
            file_path = os.path.join(self.backup_dir, backup)
            size_kb = os.path.getsize(file_path) / 1024
            print(f"   📁 {backup} ({size_kb:.1f} KB)")
        
        return backups
    
    def upload_to_github(self):
        """Faz upload dos backups para GitHub"""
        try:
            # Adicionar apenas arquivos de backup
            os.system('git add backups/*.csv backups/*.json')
            os.system(f'git commit -m "Backup automático: {datetime.now().strftime("%d/%m/%Y %H:%M")}"')
            os.system('git push origin main')
            print("✅ Backup enviado para GitHub")
        except Exception as e:
            print(f"❌ Erro no upload: {e}")

# Interface simples
if __name__ == '__main__':
    backup_mgr = BackupManager()
    
    print("=== SISTEMA DE BACKUP ===")
    print("1. Criar backup")
    print("2. Listar backups")
    print("3. Backup + Upload GitHub")
    
    opcao = input("Escolha uma opção (1-3): ").strip()
    
    if opcao == "1":
        backup_mgr.create_backup()
    elif opcao == "2":
        backup_mgr.list_backups()
    elif opcao == "3":
        backup_mgr.create_backup()
        backup_mgr.upload_to_github()
    else:
        print("❌ Opção inválida")