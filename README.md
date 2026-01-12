# integration-demoapp
Déployer un batch applicatif Python exécuté via cron et persistant ses données dans PostgreSQL.
## Stack
- Ubuntu Server
- OpenSSH (clé uniquement)
- Fail2ban
- PostgreSQL
- Python 3

## Fonctionnement
- Exécution quotidienne via cron
- Connexion DB via variables d’environnement
- Gestion d’erreurs et rollback
- Logs persistants

## Sécurité
- Comptes nominatifs
- Comptes applicatifs dédiés
- SSH par clé
- Secrets externalisés

### Mise à jour du système
sudo apt upgrade -y

### Installation et activation de SSH
sudo apt install -y openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh

#### Génération d’une clé SSH (poste client)
ssh-keygen -t ed25519 -C "appadmin@integration-demo"

#### Déploiement manuel de la clé sur le serveur
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

#### Durcissement SSH
sudo nano /etc/ssh/sshd_config

##### A modifier :
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes

#### Validation et rechargement :
sudo sshd -t
sudo systemctl reload ssh

### Protection contre les attaques (fail2ban)

#### Installation
sudo apt install -y fail2ban

#### Configuration
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

A modifier:
[sshd]
enabled = true
maxretry = 5
findtime = 10m
bantime = 1h

#### Redémarrage et vérif
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd


### Structuration du serveur applicatif
#### Création arborescence
sudo mkdir -p /opt/app/demoapp
sudo mkdir -p /logs/app
sudo chown -R appadmin:appadmin /opt/app /logs/app

#### Création d'un compte dédié
sudo useradd -r -m -d /opt/app/demoapp -s /usr/sbin/nologin demoapp
sudo chown -R demoapp:demoapp /opt/app/demoapp

### PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl status postgresql
#### Création de l’utilisateur et de la base
sudo -i -u postgres
createuser demoapp_user
createdb demoapp_db -O demoapp_user
psql
ALTER USER demoapp_user WITH PASSWORD '********';
\q
exit

#### Création du schéma
Connexion : psql -h localhost -U demoapp_user -d demoapp_db

CREATE TABLE app_logs (
    id SERIAL PRIMARY KEY,
    run_date TIMESTAMP NOT NULL,
    message TEXT NOT NULL
);


### Déploiement du batch applicatif Python
Driver PostgreSQL
sudo apt install -y python3-psycopg2

#### Mettre les droits pour rendre executable le script :
chmod +x /opt/app/demoapp/app.py
#### Test
/opt/app/demoapp/app.py

### Externalisation des secrets
Création .env :
nano /opt/app/demoapp/.env

Variable à modifier dans le .env :

DB_HOST=localhost
DB_NAME=demoapp_db
DB_USER=demoapp_user
DB_PASSWORD=********

Sécurisation pour le rendre utilisable que pour demoapp :
chmod 600 /opt/app/demoapp/.env
chown demoapp:demoapp /opt/app/demoapp/.env

### Automatisation via cron

sudo crontab -u demoapp -e

Dans le fichier :
0 1 * * * export $(grep -v '^#' /opt/app/demoapp/.env | xargs) && /opt/app/demoapp/app.py

exemple : 
### Cron job syntax

The cron daemon uses the following syntax:

.---------------- minute (0 - 59)
| .------------- hour (0 - 23)
| | .---------- day of month (1 - 31)
| | | .------- month (1 - 12) OR jan,feb,mar,apr...
| | | | .---- day of week (0 - 6) (Sunday=0 or 7)
| | | | |

command to be executed

(grep -v '^#' /opt/app/demoapp/.env | xargs)
Cette commande permet de charger les variables d’environnement depuis un fichier .env, en excluant les lignes de commentaires, afin de les rendre disponibles pour l’exécution du batch.




































































