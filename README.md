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

```
sudo apt upgrade -y
```
---
## Configuration SSH

### Installation et activation
```bash
sudo apt install -y openssh-server
```
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Génération de clé SSH (poste client)
```bash
ssh-keygen -t ed25519 -C "appadmin@integration-demo"
```
### Déploiement de la clé sur le serveur
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

```bash
nano ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```
Durcissement de la configuration SSH
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
```bash
sudo sshd -t
sudo systemctl reload ssh
```
### Protection contre les attaques – Fail2ban
```bash
sudo apt install -y fail2ban
```
### Configuration
```bash
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```
#### Configuration SSH recommandée :
```ini
Copier le code
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
#### Création de l’arborescence
```bash
sudo mkdir -p /opt/app/demoapp
sudo mkdir -p /logs/app
sudo chown -R appadmin:appadmin /opt/app /logs/app
```
#### Création du compte applicatif dédié
```bash
sudo useradd -r -m -d /opt/app/demoapp -s /usr/sbin/nologin demoapp
sudo chown -R demoapp:demoapp /opt/app/demoapp
```
## PostgreSQL
### Installation
```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl status postgresql
```
### Création de l’utilisateur et de la base
```bash
sudo -i -u postgres
createuser demoapp_user
createdb demoapp_db -O demoapp_user
psql
ALTER USER demoapp_user WITH PASSWORD '********';
\q
exit
```
### Création du schéma
Connexion :
```
bash
psql -h localhost -U demoapp_user -d demoapp_db
```
Table de logs :

sql
Copier le code
CREATE TABLE app_logs (
    id SERIAL PRIMARY KEY,
    run_date TIMESTAMP NOT NULL,
    message TEXT NOT NULL
);
Déploiement du batch Python
Installation du driver PostgreSQL
bash
Copier le code
sudo apt install -y python3-psycopg2
Droits d’exécution
bash
Copier le code
chmod +x /opt/app/demoapp/app.py
Test manuel
bash
Copier le code
/opt/app/demoapp/app.py
Externalisation des secrets
Création du fichier .env
bash
Copier le code
nano /opt/app/demoapp/.env
Variables attendues :

env
Copier le code
DB_HOST=localhost
DB_NAME=demoapp_db
DB_USER=demoapp_user
DB_PASSWORD=********
Sécurisation
bash
Copier le code
chmod 600 /opt/app/demoapp/.env
chown demoapp:demoapp /opt/app/demoapp/.env
Automatisation via cron
Édition de la crontab du compte applicatif
bash
Copier le code
sudo crontab -u demoapp -e
Tâche planifiée
bash
Copier le code
0 1 * * * export $(grep -v '^#' /opt/app/demoapp/.env | xargs) && /opt/app/demoapp/app.py
Cette commande charge dynamiquement les variables d’environnement depuis le fichier .env avant l’exécution du batch.

Rappel – Syntaxe cron
text
Copier le code
.---------------- minute (0 - 59)
|  .------------- hour (0 - 23)
|  |  .---------- day of month (1 - 31)
|  |  |  .------- month (1 - 12)
|  |  |  |  .---- day of week (0 - 6)
|  |  |  |  |
*  *  *  *  *  command
