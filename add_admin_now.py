import requests
import json

def add_admin_complete():
    """Solução completa para adicionar admin"""
    
    BASE_URL = "https://catalogo-online-0i96.onrender.com"
    
    print("=== ADICIONAR NOVO ADMINISTRADOR ===")
    print()
    
    # Dados do novo usuário admin
    new_user = {
        "username": input("Username do novo admin: ").strip(),
        "email": input("Email do novo admin: ").strip(),
        "password": input("Password do novo admin: ").strip()
    }
    
    # Dados do admin atual (SEUS dados)
    admin_user = {
        "username": input("Seu username admin: ").strip(),
        "password": input("Sua password admin: ").strip()
    }
    
    try:
        print()
        print("1. Registrando novo usuário...")
        
        # Registrar novo usuário
        register_response = requests.post(
            f"{BASE_URL}/api/register",
            json=new_user,
            timeout=10
        )
        
        if register_response.status_code == 201:
            print("✅ Novo usuário registrado!")
        elif register_response.status_code == 400:
            error_msg = register_response.json().get('error', 'Erro desconhecido')
            if "já existe" in error_msg:
                print("ℹ️  Usuário já existe, continuando...")
            else:
                print(f"❌ Erro no registro: {error_msg}")
                return
        else:
            print(f"❌ Erro no registro: {register_response.status_code}")
            return
        
        print()
        print("2. Fazendo login como admin...")
        
        # Login como admin
        login_response = requests.post(
            f"{BASE_URL}/api/login",
            json=admin_user,
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login admin: {login_response.json().get('error', 'Erro desconhecido')}")
            return
        
        print("✅ Login admin realizado!")
        
        print()
        print("3. Buscando usuários...")
        
        # Buscar usuários
        users_response = requests.get(
            f"{BASE_URL}/api/admin/users",
            cookies=login_response.cookies,
            timeout=10
        )
        
        if users_response.status_code != 200:
            print("❌ Acesso negado ou rota não implementada")
            print("📝 Implementando sistema de promoção...")
            implement_promotion_system()
            return
        
        users = users_response.json()
        print(f"✅ {len(users)} usuários encontrados")
        
        # Encontrar o novo usuário
        target_user = None
        for user in users:
            if user['username'] == new_user['username']:
                target_user = user
                break
        
        if not target_user:
            print("❌ Novo usuário não encontrado na lista")
            print("📋 Usuários disponíveis:")
            for user in users:
                print(f"   - {user['username']} ({user['email']}) - Admin: {user['is_admin']}")
            return
        
        print()
        print("4. Promovendo usuário a admin...")
        
        # Promover usuário (se a rota existir)
        promote_response = requests.put(
            f"{BASE_URL}/api/admin/users/{target_user['id']}/promote",
            cookies=login_response.cookies,
            timeout=10
        )
        
        if promote_response.status_code == 200:
            print("🎉 Usuário promovido a administrador com sucesso!")
            print()
            print("📋 RESUMO:")
            print(f"   👤 Usuário: {new_user['username']}")
            print(f"   📧 Email: {new_user['email']}")
            print(f"   🔑 Password: {new_user['password']}")
            print(f"   🌐 URL: {BASE_URL}/admin")
            print()
            print("⚠️  Compartilhe estas credenciais com segurança!")
            
        elif promote_response.status_code == 404:
            print("❌ Rota de promoção não implementada ainda")
            implement_promotion_system()
        else:
            print(f"❌ Erro na promoção: {promote_response.json()}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def implement_promotion_system():
    """Guia para implementar o sistema de promoção"""
    print()
    print("📋 PARA IMPLEMENTAR O SISTEMA DE PROMOÇÃO:")
    print("1. Adicione as rotas de promote/demote no app.py")
    print("2. Atualize o admin.js com os novos botões")
    print("3. Faça deploy no Render")
    print("4. Execute este script novamente")
    print()
    print("🔗 Documentação das rotas:")
    print("   PUT /api/admin/users/<id>/promote")
    print("   PUT /api/admin/users/<id>/demote")

if __name__ == '__main__':
    add_admin_complete()