# Préparation de la remise TP4

Younes Radouani — 5IA G2 — travail individuel.

Le dossier `TP/TP4` préparé dans le starter est une copie propre à intégrer dans le futur dépôt. Les expériences ont été exécutées à la racine du starter, avec son `.venv`. Les chemins absolus des journaux désignent cet emplacement de travail.

Quand le lien du dépôt sera fourni :

1. Cloner le dépôt ou utiliser sa copie locale, puis partir de `main` à jour et créer la branche `tp4`.
2. Copier uniquement le contenu du dossier préparé `maintai-starter-tp4/TP/TP4` dans `TP/TP4` du dépôt. Ne pas copier le starter entier ni toucher à `TP/TP3`.
3. Exécuter `git status --short`, puis `git add TP/TP4` et `git diff --cached --stat`. Vérifier que seuls les fichiers de TP4 sont présents.
4. Vérifier les exclusions avec `git check-ignore --no-index TP/TP4/.env TP/TP4/.venv/test TP/TP4/data/sensors.csv TP/TP4/models/model.joblib TP/TP4/dist/test.whl TP/TP4/build/test TP/TP4/maintai.egg-info/test TP/TP4/__pycache__/test.pyc`.
5. Créer le commit, pousser la branche `tp4` et ouvrir la pull request vers `main`. Après relecture et fusion, revenir sur `main`, faire `git pull`, puis `git tag tp4` et `git push origin tp4`.
6. Ajouter le lien réel de la PR et le statut du tag dans `COMPTE_RENDU.md`.

Le wheel se reconstruit avec `python -m build` et ne se committe pas. Les données se régénèrent avec `python -m maintai.dataset`, puis les modèles avec `python -m maintai.train`, après création du venv et installation de `requirements.txt`. Dans ce nouveau venv, installer ensuite le package avec `python -m pip install -e .` avant de vérifier les 27 tests.

Le wheel testé localement reste dans `maintai-starter-tp4/dist/maintai-0.2.0-py3-none-any.whl`. Les modèles restent dans `maintai-starter-tp4/models/`. Ils ne figurent pas dans la copie de rendu.
