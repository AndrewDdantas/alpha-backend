#!/bin/bash
# Script de setup para deploy no Ubuntu (AWS Lightsail)
# Execute: chmod +x setup.sh && ./setup.sh

set -e

echo "=========================================="
echo "  Alpha Backend - Setup Script"
echo "=========================================="

# Atualizar sistema
echo "[1/7] Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências
echo "[2/7] Instalando dependências..."
sudo apt install python3-pip python3-venv nginx git -y

# Ir para diretório home
cd /home/ubuntu

# Clonar repositório (se não existir)
if [ ! -d "alpha-backend" ]; then
    echo "[3/7] Clonando repositório..."
    git clone https://github.com/AndrewDdantas/alpha-backend.git
else
    echo "[3/7] Atualizando repositório..."
    cd alpha-backend
    git pull origin master
    cd ..
fi

cd alpha-backend

# Criar ambiente virtual
echo "[4/7] Configurando ambiente Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Verificar .env
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  ATENÇÃO: Arquivo .env não encontrado!"
    echo "   Copie o conteúdo do .env.example e configure:"
    echo "   nano /home/ubuntu/alpha-backend/.env"
    echo ""
fi

# Copiar serviço systemd
echo "[5/7] Configurando serviço systemd..."
sudo cp deploy/alpha-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable alpha-api

# Configurar Nginx
echo "[6/7] Configurando Nginx..."
sudo cp deploy/nginx.conf /etc/nginx/sites-available/alpha-api
sudo ln -sf /etc/nginx/sites-available/alpha-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Iniciar API
echo "[7/7] Iniciando API..."
sudo systemctl start alpha-api

echo ""
echo "=========================================="
echo "  ✅ Setup concluído!"
echo "=========================================="
echo ""
echo "Comandos úteis:"
echo "  - Ver status:     sudo systemctl status alpha-api"
echo "  - Ver logs:       sudo journalctl -u alpha-api -f"
echo "  - Reiniciar:      sudo systemctl restart alpha-api"
echo ""
echo "API disponível em: http://$(curl -s ifconfig.me)"
echo ""
