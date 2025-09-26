import os
import requests
import csv
import json
from datetime import datetime

class BackupManager:
    def __init__(self):
        self.render_url = "https://catalogo-online-0i96.onrender.com"  # SUA URL
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def fazer_backup_render(self):
        """Faz backup dos produtos do Render"""
        try:
            print("🔗 Conectando ao Render...")
            response = requests.get(f"{self.render_url}/api/products", timeout=30)
            
            if response.status_code == 200:
                products = response.json()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # CSV
                csv_file = f'{self.backup_dir}/produtos_{timestamp}.csv'
                if products:
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=products[0].keys())
                        writer.writeheader()
                        writer.writerows(products)
                
                # JSON
                json_file = f'{self.backup_dir}/backup_{timestamp}.json'
                backup_data = {
                    'backup_date': timestamp,
                    'total_products': len(products),
                    'render_url': self.render_url,
                    'products': products
                }
                
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ BACKUP REALIZADO: {len(products)} produtos")
                print(f"📁 Arquivos: {csv_file}, {json_file}")
                
                return len(products)
            else:
                print(f"❌ Erro API: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return 0
    
    def listar_backups(self):
        """Lista backups disponíveis"""
        if not os.path.exists(self.backup_dir):
            print("❌ Nenhum backup encontrado")
            return
        
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.startswith('backup_') and file.endswith('.json'):
                backups.append(file)
        
        if not backups:
            print("📋 Nenhum backup encontrado")
            return
        
        print("📋 BACKUPS DISPONÍVEIS:")
        for backup in sorted(backups, reverse=True)[:10]:
            file_path = os.path.join(self.backup_dir, backup)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"   📁 {backup}")
                print(f"      📅 {data['backup_date']} | 🛍️  {data['total_products']} produtos")
                print(f"      🌐 {data['render_url']}")
                print()
    
    def upload_github(self):
        """Faz upload para GitHub"""
        try:
            # Verificar se há backups novos
            os.system('git add backups/')
            os.system(f'git commit -m "Backup automático: {datetime.now().strftime("%d/%m/%Y %H:%M")}"')
            os.system('git push origin main')
            print("✅ Backup enviado para GitHub")
        except Exception as e:
            print(f"❌ Erro GitHub: {e}")

# Interface simples
if __name__ == '__main__':
    backup = BackupManager()
    
    print("=== SISTEMA DE BACKUP AUTOMÁTICO ===")
    print(f"🌐 API: {backup.render_url}")
    
    print("\nOpções:")
    print("1. Fazer backup agora")
    print("2. Listar backups")
    print("3. Backup + Upload GitHub")
    print("4. Verificar status do Render")
    
    opcao = input("Escolha (1-4): ").strip()
    
    if opcao == "1":
        backup.fazer_backup_render()
    elif opcao == "2":
        backup.listar_backups()
    elif opcao == "3":
        count = backup.fazer_backup_render()
        if count > 0:
            backup.upload_github()
    elif opcao == "4":
        # Testar conexão
        try:
            response = requests.get(f"{backup.render_url}/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ Render online e funcionando")
            else:
                print("❌ Render com problemas")
        except:
            print("❌ Não foi possível conectar ao Render")
    else:
        print("❌ Opção inválida")