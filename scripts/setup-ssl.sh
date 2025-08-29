#!/bin/bash

# Script pour configurer SSL avec Let's Encrypt pour facturx.app
# Ce script doit être exécuté sur le serveur de production

set -e

DOMAIN="facturx.app"
EMAIL="papidiagne370@gmail.com"  # Remplacez par votre email

echo "🔐 Configuration SSL pour $DOMAIN"

# Vérifier si certbot est installé
if ! command -v certbot &> /dev/null; then
    echo "📦 Installation de certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Arrêter nginx temporairement pour obtenir le certificat
echo "⏹️  Arrêt temporaire de nginx..."
sudo docker compose -f infra/docker/docker-compose.yml stop nginx

# Obtenir le certificat SSL
echo "📜 Obtention du certificat SSL..."
sudo certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN

# Vérifier que les certificats ont été créés
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "❌ Erreur: Les certificats n'ont pas été créés"
    exit 1
fi

echo "✅ Certificats SSL créés avec succès!"

# Redémarrer les services
echo "🚀 Redémarrage des services..."
sudo docker compose -f infra/docker/docker-compose.yml up -d

# Configurer le renouvellement automatique
echo "🔄 Configuration du renouvellement automatique..."
sudo crontab -l 2>/dev/null | grep -v "certbot renew" | sudo crontab -
echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'docker compose -f $(pwd)/infra/docker/docker-compose.yml restart nginx'" | sudo crontab -

echo "🎉 Configuration SSL terminée!"
echo "📋 Votre site est maintenant accessible sur: https://$DOMAIN"
echo "📋 Le certificat sera renouvelé automatiquement tous les jours à 12h00"

# Test de la configuration
echo "🧪 Test de la configuration..."
if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health | grep -q "200"; then
    echo "✅ Test réussi! Le site répond correctement en HTTPS"
else
    echo "⚠️  Attention: Le site ne répond pas correctement. Vérifiez la configuration."
fi