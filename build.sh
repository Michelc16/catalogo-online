#!/bin/bash
# build.sh
echo "Instalando dependências..."
pip install -r requirements.txt

echo "Executando setup do banco..."
python -c "
from app import app, setup_database
with app.app_context():
    setup_database()
    print('✅ Banco configurado!')
"