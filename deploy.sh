#!/bin/bash

# Script de déploiement pour CloudSense API sur VPS
# Usage: ./deploy.sh [staging|production]

ENV=${1:-production}
SSH_KEY="/Users/mac/Desktop/deploy/dev-ssh-key.pem"
SERVER_USER="ubuntu"
SERVER_HOST="ec2-13-39-19-215.eu-west-3.compute.amazonaws.com"
PROJECT_PATH="/var/www/html/apps/cloudsense"

echo "🚀 Déploiement de CloudSense API - Environnement: $ENV"
echo "🌐 Serveur: $SERVER_HOST"

# Vérifier que la clé SSH existe
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ Erreur: Clé SSH non trouvée à $SSH_KEY"
    exit 1
fi

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

# Synchronisation locale
echo "🔄 Synchronisation locale et push vers le repository..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo "ℹ️ Aucune modification à commiter"
git push origin "$CURRENT_BRANCH"

# Connexion au serveur et déploiement via Docker Compose
echo "🔗 Connexion au serveur et déploiement via Docker Compose..."
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_HOST" << EOF
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
