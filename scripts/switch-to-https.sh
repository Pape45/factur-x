#!/bin/bash

# Script pour basculer de HTTP vers HTTPS avec certificats SSL
# Ce script doit être exécuté après avoir configuré Cloudflare correctement

set -e

DOMAIN="facturx.app"
EMAIL="admin@facturx.app"  # Remplacez par votre email
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKER_COMPOSE_DIR="$PROJECT_ROOT/infra/docker"
NGINX_CONF_DIR="$PROJECT_ROOT/infra/nginx/conf.d"

echo "🔄 Basculement vers HTTPS pour $DOMAIN..."

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "$DOCKER_COMPOSE_DIR/docker-compose.yml" ]; then
    echo "❌ Erreur: docker-compose.yml non trouvé dans $DOCKER_COMPOSE_DIR"
    exit 1
fi

# Vérifier que Cloudflare est configuré en mode "DNS only"
echo "⚠️  IMPORTANT: Assurez-vous que Cloudflare est configuré en mode 'DNS only' (nuage gris) avant de continuer."
read -p "Cloudflare est-il configuré en mode 'DNS only' ? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Veuillez configurer Cloudflare en mode 'DNS only' et relancer ce script."
    exit 1
fi

# Tester la connectivité directe au serveur
echo "🔍 Test de connectivité directe au serveur..."
if ! curl -s --connect-timeout 10 "http://$DOMAIN" > /dev/null; then
    echo "❌ Erreur: Impossible de se connecter à http://$DOMAIN"
    echo "Vérifiez que:"
    echo "  - Le serveur est accessible sur le port 80"
    echo "  - Les enregistrements DNS pointent vers la bonne IP"
    echo "  - Cloudflare est bien en mode 'DNS only'"
    exit 1
fi
echo "✅ Connectivité OK"

# Arrêter les services Docker
echo "🛑 Arrêt des services Docker..."
cd "$DOCKER_COMPOSE_DIR"
docker-compose -f docker-compose-temp.yml down

# Obtenir les certificats SSL avec Certbot
echo "🔐 Obtention des certificats SSL avec Certbot..."
docker run --rm \
    -v "$PROJECT_ROOT/letsencrypt:/etc/letsencrypt" \
    -v "$PROJECT_ROOT/letsencrypt-lib:/var/lib/letsencrypt" \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --domains "$DOMAIN"

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'obtention des certificats SSL"
    echo "Vérifiez que:"
    echo "  - Cloudflare est en mode 'DNS only'"
    echo "  - Le port 80 est accessible depuis Internet"
    echo "  - Les enregistrements DNS sont corrects"
    exit 1
fi

echo "✅ Certificats SSL obtenus avec succès"

# Basculer vers la configuration HTTPS
echo "🔄 Basculement vers la configuration HTTPS..."
cp "$NGINX_CONF_DIR/facturx.conf" "$NGINX_CONF_DIR/facturx.conf.backup"
cp "$DOCKER_COMPOSE_DIR/docker-compose.yml" "$DOCKER_COMPOSE_DIR/docker-compose.yml.backup"

# Créer les répertoires pour les certificats si nécessaire
mkdir -p "$PROJECT_ROOT/letsencrypt"
mkdir -p "$PROJECT_ROOT/letsencrypt-lib"

# Redémarrer avec la configuration HTTPS
echo "🚀 Redémarrage avec la configuration HTTPS..."
docker-compose up -d

# Attendre que Nginx démarre
echo "⏳ Attente du démarrage de Nginx..."
sleep 10

# Tester HTTPS
echo "🔍 Test de la configuration HTTPS..."
if curl -s --connect-timeout 10 "https://$DOMAIN" > /dev/null; then
    echo "✅ HTTPS fonctionne correctement !"
else
    echo "⚠️  HTTPS ne répond pas encore, vérifiez les logs Nginx"
fi

# Instructions finales
echo ""
echo "🎉 Basculement vers HTTPS terminé !"
echo ""
echo "📋 Prochaines étapes:"
echo "  1. Testez votre site: https://$DOMAIN"
echo "  2. Réactivez le proxy Cloudflare (nuage orange)"
echo "  3. Configurez Cloudflare en mode SSL 'Full (strict)'"
echo "  4. Testez à nouveau: https://$DOMAIN"
echo ""
echo "📁 Fichiers de sauvegarde créés:"
echo "  - $NGINX_CONF_DIR/facturx.conf.backup"
echo "  - $DOCKER_COMPOSE_DIR/docker-compose.yml.backup"
echo ""
echo "🔄 Pour revenir en arrière si nécessaire:"
echo "  docker-compose down"
echo "  cp $NGINX_CONF_DIR/facturx.conf.backup $NGINX_CONF_DIR/facturx.conf"
echo "  cp $DOCKER_COMPOSE_DIR/docker-compose.yml.backup $DOCKER_COMPOSE_DIR/docker-compose.yml"
echo "  docker-compose -f docker-compose-temp.yml up -d"