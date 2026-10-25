# Gestionnaire de Parc Informatique & Téléphonique

Application de bureau PyQt6 + SQLite pour gérer votre parc d'équipements.

## Prérequis
- Python 3.10+
- PyQt6 : `pip install PyQt6`

## Lancement
```bash
python main.py
```

## Fonctionnalités
- ✅ Ajout / Modification / Suppression d'équipements
- ✅ Recherche multi-colonnes en temps réel
- ✅ Filtre par colonne spécifique
- ✅ Export CSV (compatible Excel)
- ✅ Base de données SQLite locale (`parc.db`)
- ✅ Interface bilingue française

## Champs gérés
| Champ          | Description                   |
|----------------|-------------------------------|
| FAN            | Identifiant FAN               |
| USER ID        | Identifiant utilisateur       |
| NOM PRÉNOM     | Nom et prénom                 |
| PC             | Modèle du PC                  |
| PC SERIAL      | Numéro de série PC            |
| NUM TÉL        | Numéro de téléphone           |
| APPAREIL TÉL   | Modèle appareil téléphonique  |
| APP TÉL SERIAL | Numéro de série téléphone     |
| CASQUE         | Modèle casque                 |
| DISQUE BACKUP  | Disque de sauvegarde          |

## Raccourcis clavier
| Raccourci | Action         |
|-----------|----------------|
| Ctrl+N    | Ajouter        |
| Ctrl+E    | Modifier       |
| Suppr     | Supprimer      |
| Ctrl+S    | Exporter CSV   |

