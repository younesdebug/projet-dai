# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Étudiant :** Younes Radouani · **Classe :** 5IA G2 · **Travail individuel (en monôme)** · **Date :** 10 novembre 2026

Travail effectué selon les pages 3 à 6 de `S6_polycopie.pdf`, dans `maintai-starter-tp3`. Les tests fournis sont conservés. Sorties complètes et captures : `preuves/`.

## 1. Mise en place (dans `TP/TP3`)

Environnement local `.venv`, Python 3.13.14, dépendances de `requirements.txt` installées. Le CSV contient 5 000 relevés et le modèle est entraîné. Faute de `../TP2/.env`, `.env` a été créé depuis le modèle avec une clé locale aléatoire.

Dernière ligne réelle avant modification, avec `python -m pytest --tb=short` :

```text
=================== 5 failed, 18 passed, 1 warning in 6.52s ===================
```

Les trois tests de `tests/test_client.py` lèvent `NotImplementedError: TP3 sprint 2 : MaintaiClient.predict`. Les deux tests de `tests/test_ui.py` lèvent `IndexError: list index out of range` : les indicateurs n'existent pas encore. [Sortie initiale complète](preuves/tests-initial.txt).

Les tests utilisent le Python de `.venv` hors du bac à sable, car celui-ci bloque l'accès aux dossiers temporaires Windows.

## 2. Lancer Streamlit

Les commandes ont été exécutées successivement depuis la racine, avec `.venv/Scripts` dans le PATH. Les options supplémentaires fixent l'adresse à 127.0.0.1, le mode headless et le port dédié 8511 pour isoler les essais du serveur déjà ouvert.

Avec `streamlit run ui/app.py`, le serveur démarre, mais le navigateur affiche :

```text
ModuleNotFoundError: No module named 'maintai'
File "ui/app.py", line 9, in <module>
    from maintai.client import APIError, MaintaiClient
```

[Capture du lancement direct](preuves/initial-cli.png) · [Journal réel](preuves/initial-cli.log).

Avec `python -m streamlit run ui/app.py`, l'application s'affiche. L'onglet Données contient encore :

```text
Sprint 1 : les indicateurs et les graphiques viendront ici.
```

[Capture initiale](preuves/initial-module.png). `python -m` inclut le dossier courant dans le chemin de recherche des modules : le paquet local `maintai` devient importable. Le lancement direct par l'exécutable ne fournit pas ce même chemin dans cet environnement.

## 3. Sprint 1 : l'onglet « Données »

Code de l'onglet après chargement de `df` :

```python
c1, c2, c3 = st.columns(3)
c1.metric("Relevés", str(len(df)))
c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

variable = st.selectbox("Variable à explorer", FEATURES)
tranches = pd.cut(df[variable], bins=10)
taux = df.groupby(tranches, observed=True).failure.mean()
taux.index = pd.Index([round(i.mid, 2) for i in taux.index], name=variable)
st.subheader("Taux de panne par tranche")
st.bar_chart(taux.rename("Taux de panne"), sort=False)

st.subheader("Température et vibration")
nuage = df.assign(panne=df.failure.map({0: "non", 1: "oui"}))
st.scatter_chart(nuage, x="temperature_c", y="vibration_mm_s", color="panne")
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.6% |
| Température moyenne | 59.8 °C |

Avec `vibration_mm_s`, le taux augmente fortement : environ 2,0 %, 9,8 %, 32,3 %, 66,4 %, 83,6 %, puis 100 % dans les dernières tranches observées. Les tranches extrêmes ont peu de relevés, jusqu'à un seul ; les tranches vides sont omises par `observed=True`.

La vibration paraît davantage liée à la panne que la température dans ces données synthétiques. Les coefficients du modèle après standardisation concordent : 2,164 pour la vibration contre 1,370 pour la température. Cette observation ne démontre pas une causalité générale. [Statistiques détaillées](preuves/statistiques.json).

[Capture du sprint 1](preuves/sprint1-donnees-vibration.png) · [Vue finale des données](preuves/final-donnees-vibration.png). Les abscisses des barres gardent des milieux de tranches numériques ; le nuage distingue les pannes par « oui/non ».

Tests après le sprint 1 :

```text
=================== 4 failed, 19 passed, 1 warning in 9.11s ===================
```

Expérience avec `print("relance")` en haut du script, retiré ensuite :

```text
Au chargement : 1 occurrence
Après modification de la liste déroulante : 2 occurrences
Après déplacement du curseur dans le formulaire : 2 occurrences
Après clic sur Prédire : 3 occurrences
```

Une interaction peut réexécuter le script entier. Les curseurs sont ici dans `st.form` : leurs changements sont regroupés jusqu'à la soumission. Le déplacement seul ne relance donc pas immédiatement le script. [Compteurs réels](preuves/relances.json) · [Journal avec le print temporaire](preuves/relance-streamlit.log).

`@st.cache_data` mémorise le résultat de `charger(path)` et évite de relire le CSV à chaque relance pour les mêmes arguments. Le cache dépend des arguments et du code de la fonction ; remplacer le CSV au même chemin ne suffit pas à l'invalider automatiquement. Il faut alors vider le cache ou prévoir son invalidation.

## 4. Sprint 2 : l'onglet « Prédiction »

Méthode `predict` :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
    headers = {"X-API-Key": self.api_key} if self.api_key else {}
    r = self.http.post("/v1/predict", json=reading, headers=headers)
    if r.status_code != 200:
        raise APIError(r.status_code, r.json().get("detail"))
    return r.json()
```

L'interface utilise `try / except APIError / except httpx.HTTPError / else`. Le client HTTP est fermé après la requête. La probabilité est arrondie en pourcentage ; l'état utilise `st.error` pour l'alerte et `st.success` pour le cas normal.

Étape intermédiaire, client implémenté mais affichage pas encore terminé :

```text
=================== 1 failed, 22 passed, 1 warning in 5.26s ===================
```

Dernière ligne des tests finaux :

```text
======================== 23 passed, 1 warning in 7.55s ========================
```

[Sortie finale complète](preuves/tests-final.txt). L'avertissement restant est une dépréciation de `starlette.testclient` avec `httpx`, provenant des dépendances fournies.

Essais dans Edge avec une vraie API uvicorn et `.env` chargé, sans mock. Les ports dédiés sont 8511 pour Streamlit et 8011 pour l'API ; `http://127.0.0.1:8011` est saisi dans la barre latérale.

| Essai | Ce qu'affiche Streamlit |
|---|---|
| Valeurs par défaut : 72 °C, 6 mm/s, 85 %, 15000 h ; bonne clé | **95 %** et **ALERTE : risque de panne élevé.** |
| Valeurs par défaut ; fausse clé | **Erreur 401 : Clé API absente ou invalide** |
| API de test réellement arrêtée | **API injoignable : vérifiez son adresse et que le serveur est démarré.** |
| Essai normal supplémentaire : -40 °C, autres valeurs par défaut, bonne clé | **0 %** et **NORMAL : risque de panne faible.** |

Captures : [bonne clé](preuves/final-bonne-cle.png), [mauvaise clé](preuves/final-mauvaise-cle.png), [état normal](preuves/final-normal.png), [API arrêtée](preuves/final-api-arretee.png). Le dernier essai conserve les valeurs de l'essai normal. La clé réelle reste masquée. Les serveurs créés pour les essais sont ensuite arrêtés ; la session initiale de l'utilisateur est conservée.

Pourquoi pas de CORS ? La requête est envoyée par le serveur Python Streamlit avec `httpx`, pas par le navigateur. CORS est une restriction appliquée par les navigateurs aux requêtes interorigines. Le port Streamlit n'a donc pas besoin d'être autorisé pour cet appel serveur à serveur. La clé API reste nécessaire.

## 5. Questions de compréhension

1. En TP2, le JavaScript du navigateur envoie la requête avec `fetch`. Dans Streamlit, le navigateur transmet les interactions au serveur Streamlit ; ce serveur appelle l'API avec `httpx`.
2. `test_client.py` injecte le `TestClient` FastAPI par `http=client`. Les requêtes atteignent l'application en mémoire, sans uvicorn ni port réseau. `test_ui.py` utilise `AppTest` et remplace la prédiction par une réponse connue.
3. Pour une démonstration rapide, je choisirais Streamlit : formulaires, graphiques et modèle se relient avec peu de code. Pour une application durable de technicien, HTML/JavaScript permettrait davantage de personnalisation mobile et d'interactions fines, au prix de plus de développement. Streamlit reste adapté à un outil interne simple ou à un prototype.

## 6. Le rendu Git

- Pull request : **non créée**, car ce dossier n'a pas de `.git` et Git est absent du PATH et des emplacements habituels vérifiés.
- Tag `tp3` sur GitHub : **non vérifiable** sans le dépôt du groupe. Aucun tag créé ; il doit être posé après la fusion.
- `git status` avant commit : **non exécutable** ; aucun résultat inventé.
- `.gitignore` exclut `.env`, `.venv/`, `data/*.csv`, `models/`, les caches pytest et Python. Aucun secret ou artefact généré n'a été ajouté à un dépôt.
- Restant : obtenir Git et le dépôt du groupe, intégrer les fichiers dans `TP/TP3` sur `tp3`, contrôler `git status` et les exclusions dans ce dépôt, préparer les commits, pousser et ouvrir la PR. Après relecture et fusion seulement, poser et pousser le tag `tp3`.

## 7. Ce qui reste flou

Les vérifications fonctionnelles demandées ont été effectuées et les captures sont disponibles. Le code et le compte rendu sont écrits dans les fichiers du projet ; aucune manipulation de l'interface de VS Code n'a été effectuée.

Restent le groupe et les membres à renseigner, ainsi que le rendu Git faute de dépôt et de Git. Les résultats ci-dessus sont les sorties réellement obtenues.
