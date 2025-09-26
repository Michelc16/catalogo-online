@echo off
echo === ATUALIZAÇÃO SEGURA DO SISTEMA ===
echo.

echo 1. Fazendo backup dos produtos...
python backup_automatico.py

echo.
echo 2. Verificando alterações locais...
git status

echo.
echo 3. Adicionando arquivos...
git add .

echo.
echo 4. Fazendo commit...
git commit -m "Atualização: %date% %time%"

echo.
echo 5. Enviando para GitHub...
git push origin main

echo.
echo === ATUALIZAÇÃO CONCLUÍDA ===
echo ✅ Backup realizado
echo ✅ Código atualizado
echo ✅ Render fará deploy automático
pause