# add_admin_render.py
import requests
import os
import sys

def add_admin_render():
    print("=== ADICIONAR ADMIN NO RENDER ===\n")
    
    # URL do seu app no Render
    BASE_URL = input("URL do seu app no Render (ex: https://seu-app.onrender.com): ").strip()
    
    if not BASE_URL:
        print("❌ URL é obrigatória!")
        return
    
    # Coletar dados
    new_username = input("Username do novo admin: ").strip()
    new_email = input("Email do novo admin: ").strip()
    new_password = input("Password do novo admin: ").strip()
    
    print(f"\n🌐 Conectando com: {BASE_URL}")
    
    # 1. Registrar novo usuário
    print("1. Registrando novo usuário...")
    try:
        register_data = {
            "username": new_username,
            "email": new_email,
            "password": new_password
        }
        
        response = requests.post(f"{BASE_URL}/api/register", json=register_data, timeout=30)
        
        if response.status_code == 201:
            print("✅ Novo usuário registrado!")
        else:
            error_msg = response.json().get('error', 'Erro desconhecido')
            print(f"❌ Erro no registro: {error_msg}")
            
            # Tentar login direto se o usuário já existe
            if "já existe" in error_msg.lower():
                print("🔄 Usuário já existe, tentando promover...")
                promote_existing_user(BASE_URL, new_username, new_password)
            return
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # 2. Login com o novo usuário (que será admin se for o primeiro)
    print("\n2. Verificando status do usuário...")
    try:
        login_data = {
            "username": new_username,
            "password": new_password
        }
        
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/login", json=login_data, timeout=30)
        
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('user', {}).get('is_admin'):
                print("🎉 Usuário é administrador (primeiro registro)!")
            else:
                print("⚠️  Usuário é comum, precisa ser promovido por um admin existente")
        else:
            print("❌ Erro no login")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def promote_existing_user(base_url, username, password):
    """Promover usuário existente para admin"""
    try:
        # Primeiro fazer login
        session = requests.Session()
        login_data = {"username": username, "password": password}
        response = session.post(f"{base_url}/api/login", json=login_data, timeout=30)
        
        if response.status_code != 200:
            print("❌ Não foi possível fazer login")
            return
        
        # Verificar se já é admin
        user_data = response.json()
        if user_data.get('user', {}).get('is_admin'):
            print("✅ Usuário já é administrador!")
            return
        
        print("📋 Para promover este usuário a admin, você precisa:")
        print("1. Fazer login com uma conta admin existente")
        print("2. Ir para a seção 'Usuários' no painel admin")
        print("3. Clicar no botão 'Promover' ao lado do usuário")
        print(f"4. Ou acessar: {base_url}/admin")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    add_admin_render()