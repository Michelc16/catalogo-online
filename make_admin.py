import requests
import json

def make_user_admin():
    """Torna um usuário existente em admin via API"""
    
    # URL do seu Render
    BASE_URL = "https://catalogo-online-0i96.onrender.com"
    
    # Dados do SEU login admin atual (o primeiro usuário que criou)
    ADMIN_CREDENTIALS = {
        "username": "Michel",  # 👈 SUBSTITUA pelo SEU username
        "password": "sua_senha"  # 👈 SUBSTITUA pela SUA senha
    }
    
    # Dados do usuário que será tornado admin
    USER_TO_PROMOTE = {
        "username": "Mateus",  # 👈 Usuário que você registrou
        "email": "mateuscomercialatual@gmail.com"
    }
    
    try:
        print("🔐 Fazendo login como admin...")
        
        # Login como admin
        login_response = requests.post(
            f"{BASE_URL}/api/login",
            json=ADMIN_CREDENTIALS,
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.json()}")
            return
        
        # Obter cookies de sessão
        cookies = login_response.cookies
        print("✅ Login realizado!")
        
        # Buscar todos os usuários
        print("📋 Buscando usuários...")
        users_response = requests.get(
            f"{BASE_URL}/api/admin/users",
            cookies=cookies,
            timeout=10
        )
        
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"✅ {len(users)} usuários encontrados")
            
            # Encontrar o usuário para promover
            user_to_promote = None
            for user in users:
                if (user['username'] == USER_TO_PROMOTE['username'] or 
                    user['email'] == USER_TO_PROMOTE['email']):
                    user_to_promote = user
                    break
            
            if user_to_promote:
                print(f"🎯 Usuário encontrado: {user_to_promote['username']}")
                
                # Aqui você precisaria de uma rota específica para promover usuários
                # Como não temos, vamos usar um método alternativo:
                
                print("⚠️  Método de promoção não implementado ainda.")
                print("📝 Vamos implementar a rota de promoção primeiro...")
                
            else:
                print("❌ Usuário não encontrado. Verifique username/email.")
                print("📋 Usuários disponíveis:")
                for user in users:
                    print(f"   - {user['username']} ({user['email']}) - Admin: {user['is_admin']}")
                
        else:
            print(f"❌ Erro ao buscar usuários: {users_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    make_user_admin()