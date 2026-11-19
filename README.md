## Données

Le projet utilise le jeu de logs **HDFS_v1** de la collection [Loghub](https://github.com/logpai/loghub). Les données **ne sont pas versionnées dans Git** : chaque membre de l'équipe les télécharge de son côté.

### Où les télécharger

1. Ouvrir le dépôt Loghub, section **HDFS**.
2. Dans la colonne *Download* de **HDFS_v1**, suivre le lien (hébergement Zenodo).
3. Télécharger `HDFS_v1.zip` (environ 1,5 Go une fois décompressé).

### Où les placer

```powershell
# depuis la racine du projet
tar -xf data\raw\HDFS_v1.zip -C data\raw
```

Arborescence attendue :

```
data/
└── raw/
    ├── HDFS_v1.zip
    ├── HDFS.log                        # logs bruts
    └── preprocessed/
        └── anomaly_label.csv           # étiquettes par bloc (BlockId, Label)
```

Si l'archive se décompresse dans un sous-dossier, adapter la constante `RAW` dans `scripts/check_data.py`.

### Échantillon pour les tests

Un échantillon de 2 000 lignes (`HDFS_2k`) est versionné dans `tests/data/`. Il sert au développement rapide et aux tests unitaires. Il n'est pas nécessaire de le télécharger.

### Vérifier l'intégrité

```powershell
python scripts/check_data.py
```

Valeurs attendues :

| Contrôle | Valeur attendue |
|---|---|
| Nombre de lignes de `HDFS.log` | 11 175 629 |
| Nombre de blocs dans `anomaly_label.csv` | environ 575 000 |
| Part d'anomalies | environ 2,9 % |
| SHA256 de `HDFS.log` | 0783096174d7832c618337f9609e06e04abd86ddd7089b3c12b407e63bfebc52 |

Si le SHA256 ou le nombre de lignes diffère, le fichier est incomplet ou corrompu : le retélécharger avant de continuer.

### Espace disque

Prévoir au moins 5 Go libres (archive, log décompressé, fichiers produits par le parsing).