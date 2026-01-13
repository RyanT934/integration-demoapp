# integration-demoapp

## Présentation

**integration-demoapp** est un projet de démonstration d’intégration applicative visant à déployer un **batch Python automatisé via cron**, sécurisé, et persistant ses données dans une base **PostgreSQL**.

Ce projet met en avant des bonnes pratiques d’administration système, de sécurité, et d’exploitation applicative sur un serveur Linux.

---

## Objectifs du projet

- Déployer un batch applicatif Python sur un serveur Linux
- Automatiser son exécution via `cron`
- Persister les résultats dans une base PostgreSQL
- Sécuriser l’accès serveur et applicatif
- Externaliser les secrets de configuration
- Garantir la traçabilité via des logs persistants

---

## Stack technique

- **OS** : Ubuntu Server
- **Accès distant** : OpenSSH (authentification par clé uniquement)
- **Sécurité** : Fail2ban
- **Base de données** : PostgreSQL
- **Langage** : Python 3

---

## Fonctionnement global

- Exécution quotidienne automatisée via `cron`
- Connexion à la base PostgreSQL via variables d’environnement
- Gestion des erreurs applicatives
- Écriture des logs en base de données
- Séparation claire des comptes système et applicatifs

---

## Sécurité mise en œuvre

- Comptes utilisateurs nominatifs
- Compte applicatif dédié sans shell
- Accès SSH par clé uniquement
- Interdiction de connexion root
- Secrets externalisés dans un fichier `.env`
- Protection contre les attaques par force brute (Fail2ban)

---

## Mise à jour du système
Cette étape permet de s’assurer que le serveur dispose des derniers correctifs de sécurité et des mises à jour de paquets avant toute configuration applicative. C’est un prérequis essentiel pour limiter les vulnérabilités connues sur un serveur exposé.
```
sudo apt upgrade -y
```
---
## Configuration SSH
L’accès SSH constitue le point d’entrée principal du serveur. Il est donc configuré de manière sécurisée afin de limiter les risques d’intrusion, en imposant une authentification par clé et en désactivant les accès sensibles.
### Installation et activation
Installation du service OpenSSH et activation du démon afin de permettre l’administration distante du serveur.
```bash
sudo apt install -y openssh-server
```
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Génération de clé SSH (poste client)
Une paire de clés asymétriques est générée côté client afin de mettre en place une authentification forte, plus sécurisée qu’un mot de passe.
```bash
ssh-keygen -t ed25519 -C "appadmin@integration-demo"
```
### Déploiement de la clé sur le serveur
La clé publique est déployée dans l’espace utilisateur du serveur avec des permissions strictes, conformément aux bonnes pratiques de sécurité SSH.
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

```bash
nano ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```
### Durcissement de la configuration SSH
La configuration SSH est renforcée afin de :
- désactiver l’authentification par mot de passe,
- interdire la connexion directe de l’utilisateur root,
- forcer l’usage des clés publiques.
```bash
sudo nano /etc/ssh/sshd_config
```
Paramètres à modifier :
```
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
```
### Validation et rechargement
La configuration est vérifiée syntaxiquement avant rechargement du service, afin d’éviter toute coupure d’accès due à une erreur de configuration.
```bash
sudo sshd -t
sudo systemctl reload ssh
```
### Protection contre les attaques – Fail2ban
Fail2ban est utilisé pour protéger le serveur contre les attaques par force brute en surveillant les journaux système et en bannissant automatiquement les adresses IP suspectes.
```bash
sudo apt install -y fail2ban
```
### Configuration
La configuration est effectuée via un fichier jail.local afin de préserver les paramètres par défaut et garantir la maintenabilité lors des mises à jour du service.
```bash
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

#### Configuration SSH recommandée :
```ini
[sshd]
enabled = true
maxretry = 5
findtime = 10m
bantime = 1h
```

### Redémarrage et vérification
```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd
```
### Structuration du serveur applicatif
Une séparation claire entre les composants système et applicatifs est mise en place afin d’améliorer la sécurité, la lisibilité et l’exploitabilité du serveur.

#### Création de l’arborescence
Les répertoires applicatifs et de logs sont centralisés dans des emplacements dédiés, facilitant la maintenance et le monitoring.

```bash
sudo mkdir -p /opt/app/demoapp
sudo mkdir -p /logs/app
sudo chown -R appadmin:appadmin /opt/app /logs/app
```

#### Création du compte applicatif dédié
Un compte système spécifique à l’application est créé, sans accès interactif, afin de respecter le principe du moindre privilège.

```bash
sudo useradd -r -m -d /opt/app/demoapp -s /usr/sbin/nologin demoapp
sudo chown -R demoapp:demoapp /opt/app/demoapp
```

## PostgreSQL
PostgreSQL est utilisé comme système de gestion de base de données relationnelle pour stocker les traces d’exécution du batch applicatif.
### Installation
```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl status postgresql
```
### Création de l’utilisateur et de la base
Un utilisateur et une base dédiés à l’application sont créés afin d’isoler les accès et limiter les droits au strict nécessaire.

```bash
sudo -i -u postgres
```
```
createuser demoapp_user
```
```
createdb demoapp_db -O demoapp_user
```
```psql
ALTER USER demoapp_user WITH PASSWORD '********';
\q
exit
```

### Création du schéma
Une table de logs est définie pour stocker les informations d’exécution du batch, assurant la traçabilité et facilitant le diagnostic en cas d’erreur.

#### Connexion :
```
bash
psql -h localhost -U demoapp_user -d demoapp_db
```
```sql

CREATE TABLE app_logs (
    id SERIAL PRIMARY KEY,
    run_date TIMESTAMP NOT NULL,
    message TEXT NOT NULL
);
```

## Déploiement du batch Python
Le batch Python constitue le cœur applicatif du projet. Il est conçu pour s’exécuter de manière autonome et interagir avec la base PostgreSQL.

### Fonctionnement du batch Python
Le batch Python est responsable de l’exécution applicative automatisée.
À chaque lancement, il se connecte à la base PostgreSQL en utilisant des variables d’environnement, enregistre une trace d’exécution et remonte une erreur explicite en cas d’échec.

### Installation du driver PostgreSQL
```bash
sudo apt install -y python3-psycopg2
```

### Droits d’exécution

```bash
chmod +x /opt/app/demoapp/app.py
```

### Test manuel
Une exécution manuelle est réalisée afin de valider le bon fonctionnement du script avant son automatisation.

```bash
/opt/app/demoapp/app.py

```

## Externalisation des secrets
Les informations sensibles (identifiants de base de données) sont externalisées dans un fichier .env afin d’éviter leur exposition dans le code source.

### Création du fichier .env

```bash
nano /opt/app/demoapp/.env
```

#### Variables attendues :

```env
DB_HOST=localhost
DB_NAME=demoapp_db
DB_USER=demoapp_user
DB_PASSWORD=********
```

### Sécurisation
Les permissions du fichier .env sont volontairement restrictives pour empêcher tout accès non autorisé aux secrets applicatifs.

```bash
chmod 600 /opt/app/demoapp/.env
chown demoapp:demoapp /opt/app/demoapp/.env
```

## Automatisation via cron
L’exécution du batch est automatisée à l’aide de cron, permettant un fonctionnement régulier et sans intervention humaine.

### Édition de la crontab du compte applicatif

```bash
sudo crontab -u demoapp -e
```

### Tâche planifiée
Les variables d’environnement sont chargées dynamiquement au moment de l’exécution afin de garantir la portabilité et la séparation configuration / code.

```bash
0 1 * * * export $(grep -v '^#' /opt/app/demoapp/.env | xargs) && /opt/app/demoapp/app.py
```
Cette commande charge dynamiquement les variables d’environnement depuis le fichier .env avant l’exécution du batch.

### Rappel – Syntaxe cron
```text
.---------------- minute (0 - 59)
|  .------------- hour (0 - 23)
|  |  .---------- day of month (1 - 31)
|  |  |  .------- month (1 - 12)
|  |  |  |  .---- day of week (0 - 6)
|  |  |  |  |
*  *  *  *  *  command
```
