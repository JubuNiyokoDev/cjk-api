# Stockage des médias : disque historique + S3 centralisé

## Principe

Deux backends coexistent, arbitrés fichier par fichier par
`core.storages.MediaRouterStorage` :

| Fichier | Servi depuis | URL |
|---|---|---|
| Présent dans `MEDIA_ROOT` (déjà téléversé) | disque, via nginx | `https://api.cjkamenge.com/media/<nom>` |
| Absent du disque (téléversé après la bascule) | S3 / RustFS | `https://cdn.rundinova.com/cjk-media/<nom>` |

Le critère est un `stat()` local, sans appel réseau. **Aucun fichier existant
n'est déplacé, copié ni réécrit** : les 46 fichiers de production (≈64 Mio)
gardent exactement l'URL qu'ils ont aujourd'hui, et la migration ne peut donc
pas perdre de données ni casser un lien déjà publié.

Quand un même nom existe des deux côtés, **le disque gagne** : un lien publié ne
change jamais. `exists()` interroge en revanche les deux backends, de sorte
qu'un nouveau téléversement ne puisse jamais masquer un fichier du disque — il
sera suffixé par Django.

## Activation

Le code est **inerte tant que `AWS_STORAGE_BUCKET_NAME` est vide** : sans cette
variable il n'y a pas de backend distant et tout, lecture comme écriture, reste
sur le disque. Le déploiement du code est donc sans effet observable, et la
bascule se fait ensuite en une seule étape.

### 1. Dépendances

```bash
cd /home/cjk-api.io
./venv/bin/pip install -r requirements.txt   # django-storages + boto3
```

### 2. Variables dans `/home/cjk-api.io/.env`

```ini
AWS_STORAGE_BUCKET_NAME=cjk-media
AWS_S3_ENDPOINT_URL=https://s3.rundinova.com
AWS_S3_CUSTOM_DOMAIN=cdn.rundinova.com/cjk-media
AWS_ACCESS_KEY_ID=<RUSTFS_ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<RUSTFS_SECRET_KEY>
```

Les identifiants sont ceux de `/opt/rundinova-storage/.env`.

`AWS_S3_CUSTOM_DOMAIN` inclut le nom du bucket : RustFS est servi en path-style
derrière nginx (`s3.rundinova.com/<bucket>/<clé>`), et django-storages se
contente de concaténer `<domaine>/<clé>`.

### 3. Redémarrage

```bash
systemctl restart cjk-api
```

### 4. Vérification

```bash
./venv/bin/python manage.py media_audit
```

Attendu juste après la bascule : tous les fichiers en `disque`, zéro en `s3`,
zéro `MANQUANT`. Téléverser ensuite une image depuis le back-office et relancer
la commande : le nouveau fichier doit apparaître en `s3`, et son URL pointer sur
`cdn.rundinova.com`.

## Le bucket

`cjk-media` est créé sur RustFS avec une politique autorisant uniquement
`s3:GetObject` aux requêtes anonymes. Vérifié :

- lecture anonyme d'un objet via `https://cdn.rundinova.com/cjk-media/...` → `200` ;
- énumération du bucket (`GET /cjk-media/`, `?list-type=2`) → `403` ;
- `PUT`/`DELETE` sur le vhost `cdn.` → `403` (bloqué par nginx, avant RustFS).

Les écritures passent par `s3.rundinova.com`, authentifiées en SigV4.

## Points à surveiller

1. **Ne jamais vider `MEDIA_ROOT`.** C'est désormais la seule source des
   anciens fichiers, et leurs URLs en dépendent. À sauvegarder avant toute
   opération sur `/home/cjk-api.io`.
2. **Identifiants partagés.** L'API utilise aujourd'hui les identifiants racine
   de RustFS. À remplacer par un utilisateur dédié restreint au bucket
   `cjk-media` dès que possible.
3. **Pas de sauvegarde S3.** RustFS est mono-nœud, mono-disque, sans
   réplication : le bucket doit entrer dans une stratégie de sauvegarde.
4. **Migrer les anciens fichiers est possible mais inutile.** Copier un fichier
   du disque vers S3 ne changerait pas son URL (le disque gagne). Pour basculer
   réellement un ancien fichier, il faudrait le copier *puis* le retirer du
   disque — ce qui change son URL publique. À ne faire que de façon délibérée.
