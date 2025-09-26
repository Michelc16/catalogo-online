import sqlite3
from werkzeug.security import generate_password_hash

def add_admin_user():
    """Adiciona um usuário admin diretamente no banco"""
    
    # Para SQLite local (desenvolvimento)
    conn = sqlite3.connect('catalogo.db')
    cursor = conn.cursor()
    
    username = input("Username do novo admin: ")
    email = input("Email do novo admin: ")
    password = input("Password do novo admin: ")
    
    # Hash da password
    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute('''
            INSERT INTO user (username, email, password_hash, is_admin, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, True, True))
        
        conn.commit()
        print(f"✅ Admin {username} adicionado com sucesso!")
        
    except sqlite3.IntegrityError:
        print("❌ Usuário ou email já existe!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_admin_user()