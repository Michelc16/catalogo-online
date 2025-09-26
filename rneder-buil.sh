#!/bin/bash
# Script executado antes de cada deploy no Render

echo "=== INICIANDO BACKUP AUTOMÁTICO ==="

# Fazer backup se existir banco SQLite
if [ -f catalogo.db ]; then
    python backup.py
    echo "✅ Backup realizado antes do deploy"
else
    echo "ℹ️  Banco PostgreSQL detectado - backup não necessário"
fi

# Instalar dependências
pip install -r requirements.txt

echo "=== DEPLOY INICIADO ==="