import csv
import requests
import json
from datetime import datetime

def restaurar_backup():
    """Restaura produtos de um backup"""
    print("=== RESTAURAR BACKUP ===")
    
    # Listar backups
    import os
    backups = []
    for file in os.listdir('backups'):
        if file.startswith('backup_') and file.endswith('.json'):
            backups.append(file)
    
    if not backups:
        print("❌ Nenhum backup encontrado")
        return
    
    print("📋 Backups disponíveis:")
    for i, backup in enumerate(sorted(backups, reverse=True)[:5]):
        print(f"   {i+1}. {backup}")
    
    try:
        escolha = int(input("Escolha o backup (1-5): ")) - 1
        backup_file = sorted(backups, reverse=True)[escolha]
        
        with open(f'backups/{backup_file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📦 {len(data['products'])} produtos encontrados no backup")
        
        # Restaurar para o Render
        render_url = "https://catalogo-online-0i96.onrender.com"
        
        confirm = input("Restaurar para o Render? (s/n): ").lower()
        if confirm == 's':
            for product in data['products']:
                response = requests.post(
                    f"{render_url}/api/products",
                    json=product,
                    timeout=10
                )
                if response.status_code != 201:
                    print(f"❌ Erro ao restaurar {product['name']}")
            
            print("✅ Restauração concluída!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    restaurar_backup()