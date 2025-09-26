#!/bin/bash
echo "🔧 Executando build no Render..."

# Instalar dependências
pip install -r requirements.txt

# Criar diretórios necessários
mkdir -p uploads
mkdir -p static/images

# Inicializar banco de dados
python -c "
from app import app, setup_database
with app.app_context():
    setup_database()
    print('✅ Banco de dados inicializado!')
"

echo "🚀 Build concluído!"