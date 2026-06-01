#!/bin/bash

# Script de déploiement pour CloudSense API sur VPS (root@72.60.213.116)
# Usage: ./deploy.sh [staging|production]

ENV=${1:-production}
SERVER_USER="root"
SERVER_HOST="72.60.213.116"
PROJECT_PATH="/var/www/html/apps/cloudsense"

echo "🚀 Déploiement de CloudSense API - Environnement: $ENV"
echo "🌐 Serveur: $SERVER_USER@$SERVER_HOST"

# Branche actuelle
CURRENT_BRANCH=$(git branch --show-current)
echo "🌿 Branche actuelle: $CURRENT_BRANCH"

# Pour ce projet, on déploie depuis 'main'
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️ Attention: Vous n'êtes pas sur la branche 'main'"
    read -p "Continuer le déploiement depuis '$CURRENT_BRANCH'? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Charger les variables secrètes locales pour le déploiement
if [ -f .env ]; then
    # Helper pour lire .env en bash
    get_env_var() {
        local var_name=$1
        local value=$(grep -E "^${var_name}=" .env | cut -d'=' -f2- | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
        echo "$value"
    }
    VPS_PASSWORD=$(get_env_var "VPS_PASSWORD")
fi

if [ -z "$VPS_PASSWORD" ]; then
    echo "❌ Erreur: VPS_PASSWORD n'est pas défini dans le fichier .env local."
    exit 1
fi

# Synchronisation locale
echo "🔄 Synchronisation locale et push vers le repository..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "ℹ️ Aucune modification à commiter"
git push origin "$CURRENT_BRANCH"

# S'assurer que le répertoire de destination existe et copier le fichier .env local
echo "📤 Copie du fichier .env local vers le serveur..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "mkdir -p $PROJECT_PATH"
sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no .env "$SERVER_USER@$SERVER_HOST:$PROJECT_PATH/.env"

# Connexion au serveur et déploiement via Docker Compose
echo "🔗 Connexion au serveur via sshpass et déploiement via Docker Compose..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << EOF
    set -e
    
    echo "=== 🏗️ Mise à jour sur le serveur ==="
    
    # Créer le répertoire si inexistant
    mkdir -p "$PROJECT_PATH"
    cd "$PROJECT_PATH"
    
    # Initialiser git si nécessaire ou simplement pull
    if [ ! -d ".git" ]; then
        echo "📥 Initialisation du projet sur le serveur..."
        git clone https://github.com/gaye-lamine/cloudsense.git .
    else
        echo "📥 Récupération des dernières modifications..."
        git stash || true
        git pull origin "$CURRENT_BRANCH"
    fi
    
    # Vérifier l'existence du fichier .env
    if [ ! -f ".env" ]; then
        echo "⚠️ Fichier .env manquant sur le serveur!"
        echo "💡 Copie du fichier .env.example..."
        cp .env.example .env
        echo "👉 Assurez-vous de configurer les variables secrètes dans .env sur le serveur."
    fi
    
    # Déploiement via Docker Compose
    echo "🚀 Démarrage des conteneurs avec Docker Compose..."
    docker compose down --remove-orphans || true
    docker compose up -d --build
    
    echo "=== ✅ Déploiement terminé avec succès! ==="
EOF

echo "🏁 Déploiement terminé!"
