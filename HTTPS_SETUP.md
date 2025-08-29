# Configuration HTTPS pour facturx.app

Ce guide explique comment configurer HTTPS pour le domaine `facturx.app` avec Let's Encrypt.

## Prérequis

- Serveur avec Docker et Docker Compose installés (IP: 89.168.44.67)
- Domaine `facturx.app` pointant vers votre serveur
- Ports 80 et 443 ouverts sur le serveur

## Configuration DNS

### 1. Configuration des enregistrements DNS

Configurez les enregistrements DNS suivants chez votre registraire de domaine :

```
# Enregistrement A principal
facturx.app.        A    89.168.44.67

# Enregistrement CNAME pour www (optionnel)
www.facturx.app.    CNAME    facturx.app.

# Enregistrements pour les sous-domaines (si nécessaire)
api.facturx.app.    A    89.168.44.67
staging.facturx.app. A   89.168.44.67
```

### 2. Vérification de la propagation DNS

Après avoir configuré les enregistrements DNS, vérifiez la propagation :

```bash
# Vérifier la résolution DNS
nslookup facturx.app
dig facturx.app

# Vérifier que l'IP correspond
ping facturx.app

# Vérifier depuis différents serveurs DNS
dig @8.8.8.8 facturx.app
dig @1.1.1.1 facturx.app
```

**Résultat attendu :**
```
facturx.app.    300    IN    A    89.168.44.67
```

### 3. Timeline de propagation

- **Propagation locale** : 5-15 minutes
- **Propagation globale** : 24-48 heures maximum
- **Vérification recommandée** : Attendre au moins 30 minutes avant l'installation SSL

### 4. Validation avant SSL

Avant d'installer le certificat SSL, validez que le domaine est accessible :

```bash
# Test HTTP (doit fonctionner)
curl -I http://facturx.app
curl -I http://89.168.44.67

# Vérifier que Nginx répond
telnet facturx.app 80
```

## 🚀 Configuration automatique

### Étape 1 : Validation préalable

Avant de commencer, validez que votre serveur est accessible :

```bash
# Se connecter au serveur
ssh user@89.168.44.67

# Vérifier que Docker fonctionne
docker --version
docker-compose --version

# Vérifier que les ports sont ouverts
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### Étape 2 : Exécuter le script de configuration

```bash
# Rendre le script exécutable
chmod +x scripts/setup-ssl.sh

# Exécuter la configuration SSL
./scripts/setup-ssl.sh
```

### Étape 3 : Déployer avec HTTPS

```bash
# Arrêter les services actuels
docker-compose down

# Redémarrer avec la nouvelle configuration
docker-compose up -d

# Vérifier les logs
docker-compose logs nginx
```

Le script va :
- Installer certbot si nécessaire
- Obtenir un certificat SSL pour facturx.app
- Configurer le renouvellement automatique
- Redémarrer les services Docker

## 🔧 Configuration manuelle (alternative)

Si vous préférez configurer manuellement :

### 1. Installer certbot

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Arrêter nginx temporairement

```bash
sudo docker compose -f infra/docker/docker-compose.yml stop nginx
```

### 3. Obtenir le certificat

```bash
sudo certbot certonly \
    --standalone \
    --email votre-email@example.com \
    --agree-tos \
    --no-eff-email \
    --domains facturx.app
```

### 4. Redémarrer les services

```bash
sudo docker compose -f infra/docker/docker-compose.yml up -d
```

### 5. Configurer le renouvellement automatique

```bash
# Ajouter une tâche cron pour le renouvellement
echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'docker compose -f $(pwd)/infra/docker/docker-compose.yml restart nginx'" | sudo crontab -
```

## 🧪 Test de la configuration

### Vérifier le certificat SSL

```bash
# Test de base
curl -I https://facturx.app/health

# Test détaillé du certificat
openssl s_client -connect facturx.app:443 -servername facturx.app
```

### Vérifier la redirection HTTP → HTTPS

```bash
# Doit rediriger vers HTTPS
curl -I http://facturx.app
```

## ✅ Validation

Après la configuration, testez l'accès HTTPS :

### Tests de connectivité

```bash
# Test HTTPS principal
curl -I https://facturx.app

# Test direct par IP (doit échouer avec certificat)
curl -I https://89.168.44.67

# Vérifier le certificat SSL
openssl s_client -connect facturx.app:443 -servername facturx.app

# Test de redirection HTTP vers HTTPS
curl -I http://facturx.app

# Vérifier les en-têtes de sécurité
curl -I https://facturx.app | grep -E '(Strict-Transport|X-Frame|X-Content)'
```

### Tests depuis différents emplacements

```bash
# Test depuis différents serveurs DNS
dig @8.8.8.8 facturx.app
dig @1.1.1.1 facturx.app

# Test de latence
ping -c 4 facturx.app
traceroute facturx.app
```

## 🌐 URLs d'accès

Après configuration réussie, votre application sera accessible via :

- **Production** : https://facturx.app
- **API** : https://facturx.app/api/
- **Health Check** : https://facturx.app/health
- **Documentation** : https://facturx.app/docs (si configurée)

### Informations serveur

- **IP du serveur** : 89.168.44.67
- **Ports exposés** : 80 (HTTP), 443 (HTTPS)
- **Certificat** : Let's Encrypt (renouvellement automatique)

## 📊 Monitoring et maintenance

### Vérification quotidienne

```bash
# Statut des services
docker-compose ps

# Utilisation des ressources
docker stats --no-stream

# Espace disque
df -h

# Logs récents
docker-compose logs --tail=50 nginx
```

### Surveillance SSL

```bash
# Vérifier l'expiration du certificat
echo | openssl s_client -connect facturx.app:443 2>/dev/null | openssl x509 -noout -dates

# Test de renouvellement
sudo certbot renew --dry-run
```

## 📁 Fichiers modifiés

### `infra/nginx/conf.d/facturx.conf`
- ✅ Ajout du bloc server HTTPS (port 443)
- ✅ Configuration SSL/TLS sécurisée
- ✅ Redirection HTTP → HTTPS pour facturx.app
- ✅ Headers de sécurité HTTPS
- ✅ Conservation de la config localhost pour le développement

### `infra/docker/docker-compose.yml`
- ✅ Volumes pour les certificats Let's Encrypt
- ✅ Variable d'environnement DOMAIN_NAME
- ✅ Port 443 exposé

## 🔍 Dépannage

### Problème : "Certificate not found"

```bash
# Vérifier que les certificats existent
sudo ls -la /etc/letsencrypt/live/facturx.app/

# Si absent, relancer l'obtention du certificat
sudo certbot certonly --standalone -d facturx.app
```

### Problème : "Connection refused"

```bash
# Vérifier que nginx fonctionne
sudo docker compose -f infra/docker/docker-compose.yml ps

# Vérifier les logs nginx
sudo docker compose -f infra/docker/docker-compose.yml logs nginx
```

### Problème : "DNS resolution failed"

```bash
# Vérifier la configuration DNS
nslookup facturx.app

# Attendre la propagation DNS (peut prendre jusqu'à 48h)
```

### Problème : DNS ne résout pas

```bash
# Vérifier la propagation DNS
nslookup facturx.app 8.8.8.8
dig facturx.app @1.1.1.1

# Vider le cache DNS local
sudo systemctl flush-dns  # Ubuntu
sudo dscacheutil -flushcache  # macOS
```

## 🔄 Renouvellement automatique

Le certificat Let's Encrypt est valide 90 jours. Le renouvellement automatique est configuré pour :
- **Fréquence** : Tous les jours à 12h00
- **Action** : Redémarrage automatique de nginx si le certificat est renouvelé
- **Logs** : Consultables dans `/var/log/letsencrypt/`

## 🎉 Résultat final

Après configuration, votre site sera accessible via :
- ✅ `https://facturx.app` (HTTPS sécurisé)
- ✅ `http://facturx.app` (redirige vers HTTPS)
- ✅ `http://localhost` (développement local)

## 📞 Support

En cas de problème :
1. Vérifiez les logs : `sudo docker compose logs nginx`
2. Testez la configuration : `sudo nginx -t`
3. Vérifiez les certificats : `sudo certbot certificates`