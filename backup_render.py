import os
import requests
import csv
import json
from datetime import datetime

def backup_from_render():
    """Faz backup dos produtos da API do Render"""
    try:
        # URL da sua API no Render
        render_url = "https://catalogo-online-0i96.onrender.com"  # SUBSTITUA pela sua URL
        
        print(f"🔗 Conectando à API: {render_url}")
        
        # Buscar produtos da API
        response = requests.get(f"{render_url}/api/products")
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produtos encontrados na API")
            
            # Criar backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs('backups', exist_ok=True)
            
            # Backup CSV
            csv_file = f'backups/produtos_render_{timestamp}.csv'
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if products:
                    columns = products[0].keys()
                    writer = csv.DictWriter(f, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(products)
            
            # Backup JSON
            json_file = f'backups/backup_render_{timestamp}.json'
            backup_data = {
                'backup_date': timestamp,
                'source': 'render_api',
                'total_products': len(products),
                'products': products
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            print("🎉 BACKUP DO RENDER CRIADO!")
            print(f"📊 Produtos: {len(products)}")
            print(f"📁 CSV: {csv_file}")
            print(f"📁 JSON: {json_file}")
            
            # Mostrar alguns produtos
            print("\n📦 AMOSTRA DE PRODUTOS:")
            for i, product in enumerate(products[:3]):
                print(f"   {i+1}. {product.get('name', 'N/A')} - R$ {product.get('price', 'N/A')}")
            
            return len(products)
            
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 0

if __name__ == '__main__':
    # SUBSTITUA pela URL do seu app no Render
    YOUR_RENDER_URL = "https://catalogo-online-0i96.onrender.com"  # 👈 ALTERE AQUI!
    
    if YOUR_RENDER_URL == "https://seu-app.onrender.com":
        print("❌ Por favor, edite o arquivo e coloque sua URL do Render")
        print("🔗 Encontre sua URL em: https://dashboard.render.com")
    else:
        backup_from_render()