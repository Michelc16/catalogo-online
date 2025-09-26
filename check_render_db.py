import os

print("=== VERIFICANDO CONFIGURAÇÃO DO RENDER ===")
print("DATABASE_URL:", os.environ.get('DATABASE_URL', 'Não configurado'))
