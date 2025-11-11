# 🎬 CineNantes

Bienvenue sur **CineNantes**, l’application web qui rassemble en un clin d’oeil tous les horaires des séances de cinéma à Nantes et ses alentours !  
Retrouvez facilement les films à l’affiche, filtrez par cinéma, recherchez vos coups de cœur, et découvrez les séances accessibles ou en version originale.

---

## 🚀 Fonctionnalités

- **Affichage des séances** : Visualisez tous les films programmés dans les cinémas nantais, jour par jour.
- **Filtres par cinéma** : Sélectionnez un ou plusieurs cinémas pour n’afficher que leurs séances.
- **Recherche instantanée** : Trouvez rapidement un film grâce à la barre de recherche.
- **Affichage des versions** : Repérez facilement les séances en VO ou VF.
- **Accessibilité** : Les séances accessibles aux personnes à mobilité réduite sont signalées.
- **Épingler vos films** : Marquez vos films favoris pour les retrouver plus vite.
- **Responsive** : L’application s’adapte à tous les écrans, du mobile à l’ordinateur.

---

## 🛠️ Installation

### Prérequis

- Python 3.8+
- Un compte [Supabase](https://supabase.com/) (pour la base de données)
- Un compte [Vercel](https://vercel.com/) (pour le déploiement)

### 1. Cloner le projet

git clone https://github.com/Bcharier/CineNantes.git
cd CineNantes

### 2. Installer les Dépendances

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

### Configurer l'environnement

Renseignez vos clés Supabase et le titre du site dans le fichier .env : 
SUPABASE_URL=...
PUBLIC_SUPABASE_ANON_KEY=...
WEBSITE_TITLE=...

Modifier le fichier .env.sample pour renseigner les cinémas dont vous souhaitez récupérer les informations. 

L'id de chaque cinéma est disponible dans l'url : 
Par exemple pour le Katorza à Nantes dont l'id est P0052 : https://www.allocine.fr/seance/salle_gen_csalle=P0052.html 

### Initialiser la base de données 

Créez les tables dans Supabase en utilisant le schéma fourni dans modules/Models.py.
Lancez le script de population pour importer les séances :
python scripts/populate_db.py

### Lancer l'application en local 

python app.py


🗂️ Structure du projet

├── app.py                # Application Flask principale
├── api/                  # Api pour les tâches automatisées
├── modules/              # Scraping, gestion Supabase, modèles
├── scripts/              # Scripts d’import et de traitement des données
├── static/               # Fichiers statiques (CSS, JS, images)
├── templates/            # Templates HTML Jinja2
├── data/                 # Données brutes des séances (JSON)
├── .env.sample           # Données des cinémas
├── requirements.txt      # Dépendances Python
└── vercel.json           # Configuration Vercel


🙏 Remerciements

Merci à Solène Derniaux pour l’idée originale.
Merci à tous les cinémas nantais pour leur programmation riche et variée.


📝 Licence

Ce projet est open-source, n’hésitez pas à le adapter ou à contribuer !

Bon film ! 🍿