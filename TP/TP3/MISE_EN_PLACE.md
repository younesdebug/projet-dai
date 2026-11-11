# Mise en place TP3 — 10 novembre 2026

Ce document décrit l'état initial. Les sprints sont maintenant terminés :
**23 passed, 1 warning in 7.55s**. Voir `COMPTE_RENDU.md` et `preuves/` pour
les résultats et captures de chaque étape.

Le projet est installé dans son dossier actuel, avec un environnement `.venv`
créé sous Python 3.13.14 et les dépendances de `requirements.txt` installées.
L'environnement du TP1 et le fichier `../TP2/.env` n'ont pas été trouvés.
Le fichier `.env` a été créé depuis `.env.example` avec une clé locale aléatoire.
Il est exclu par `.gitignore`.

## Vérifications

- `python -m maintai.dataset` : 5 000 relevés, taux de panne 13,6 %.
- `python -m maintai.train` : modèle enregistré dans `models/model.joblib`.
- `python -m pytest --tb=short` : **5 failed, 18 passed**, un avertissement.
- Les cinq échecs correspondent aux exercices non implémentés : trois tests
  du client et deux tests de l'interface. Le code des exercices est conservé.
- L'API `/health` répond avec `status=ok` et `model_loaded=true`.
- Streamlit répond sur http://127.0.0.1:8501 ; l'onglet Données conserve
  le message d'attente du sprint 1, sans indicateurs ni graphiques.

## Relancer depuis la racine du projet

Terminal 1 :

```powershell
.\.venv\Scripts\python.exe -m uvicorn maintai.api.main:app --env-file .env --host 127.0.0.1 --port 8000
```

Terminal 2 :

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/app.py --server.address=127.0.0.1
```

Tests :

```powershell
.\.venv\Scripts\python.exe -m pytest
```

`streamlit run` utilise l'exécutable trouvé dans le PATH. `python -m streamlit`
utilise le module installé dans le Python choisi et place le dossier courant
dans le chemin des imports Python. La seconde forme est préférable ici pour
retrouver le paquet local `maintai`. Les deux exécutables de `.venv` annoncent
Streamlit 1.66.1.

Les journaux des serveurs sont dans `.venv/api.*.log` et
`.venv/streamlit.*.log`. Les serveurs ont été lancés en arrière-plan.

## Étape Git restante

Ce dossier ne contient pas de dépôt `.git`. Git n'est pas disponible dans le
PATH ni aux emplacements habituels vérifiés. La création de la branche `tp3`,
le commit et le push restent à effectuer avec le dépôt du groupe.
