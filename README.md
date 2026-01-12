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
