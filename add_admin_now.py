import requests
import json
import sys

def add_admin_now():
    print("=== ADICIONAR NOVO ADMINISTRADOR ===\n")
    
    # Configurações
    BASE_URL = "http://localhost:5000"  # Altere para sua URL do Render se necessário
    
    # Coletar dados
    new_username = input("Username do novo admin: ").strip()
    new_email = input("Email do novo admin: ").strip()
    new_password = input("Password do novo admin: ").strip()
    admin_username = input("Seu username admin: ").strip()
    admin_password = input("Sua password admin: ").strip()
    
    print("\n1. Registrando novo usuário...")
    
    # Registrar novo usuário
    try:
        register_data = {
            "username": new_username,
            "email": new_email,
            "password": new_password
        }
        
        response = requests.post(f"{BASE_URL}/api/register", json=register_data)
        
        if response.status_code == 201:
            print("✅ Novo usuário registrado!")
        else:
            error_msg = response.json().get('error', 'Erro desconhecido')
            print(f"❌ Erro no registro: {error_msg}")
            return
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    print("\n2. Fazendo login como admin...")
    
    # Login como admin
    session = requests.Session()
    try:
        login_data = {
            "username": admin_username,
            "password": admin_password
        }
        
        response = session.post(f"{BASE_URL}/api/login", json=login_data)
        
        if response.status_code == 200:
            print("✅ Login admin realizado!")
        else:
            error_msg = response.json().get('error', 'Erro desconhecido')
            print(f"❌ Erro no login: {error_msg}")
            return
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    print("\n3. Buscando usuários...")
    
    # Buscar lista de usuários
    try:
        response = session.get(f"{BASE_URL}/api/admin/users")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ {len(users)} usuários encontrados")
            
            # Encontrar o novo usuário
            new_user = None
            for user in users:
                if user['username'] == new_username:
                    new_user = user
                    break
            
            if new_user:
                print(f"✅ Novo usuário encontrado (ID: {new_user['id']})")
                
                # Promover a admin
                print("\n4. Promovendo usuário a administrador...")
                
                promote_response = session.put(f"{BASE_URL}/api/admin/users/{new_user['id']}/promote")
                
                if promote_response.status_code == 200:
                    print("✅ Usuário promovido a administrador com sucesso!")
                    print(f"\n🎉 CONCLUÍDO! {new_username} agora é administrador!")
                else:
                    error_msg = promote_response.json().get('error', 'Erro desconhecido')
                    print(f"❌ Erro na promoção: {error_msg}")
            else:
                print("❌ Novo usuário não encontrado na lista")
                
        else:
            print("❌ Acesso negado ou rota não implementada")
            print("\n📝 Implementando sistema de promoção...")
            implement_promotion_system()
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        implement_promotion_system()

def implement_promotion_system():
    print("""
📋 PARA IMPLEMENTAR O SISTEMA DE PROMOÇÃO:

1. Adicione as seguintes rotas no arquivo app.py:

@app.route('/api/admin/users/<int:user_id>/promote', methods=['PUT'])
@admin_required
def promote_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        if user.id == session['user_id']:
            return jsonify({"error": "Não é possível modificar sua própria conta"}), 400
        
        user.is_admin = True
        db.session.commit()
        
        return jsonify({"message": "Usuário promovido a administrador com sucesso", "user": user.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao promover usuário: {str(e)}"}), 400

@app.route('/api/admin/users/<int:user_id>/demote', methods=['PUT'])
@admin_required
def demote_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        if user.id == session['user_id']:
            return jsonify({"error": "Não é possível modificar sua própria conta"}), 400
        
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1 and user.is_admin:
            return jsonify({"error": "Não é possível remover o último administrador"}), 400
        
        user.is_admin = False
        db.session.commit()
        
        return jsonify({"message": "Administrador rebaixado a usuário comum com sucesso", "user": user.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao rebaixar usuário: {str(e)}"}), 400

2. Atualize o admin.js com as funções promoteUser() e demoteUser()

3. Faça deploy no Render
4. Execute este script novamente

🔗 Rotas implementadas:
   PUT /api/admin/users/<id>/promote
   PUT /api/admin/users/<id>/demote
""")

if __name__ == "__main__":
    add_admin_now()