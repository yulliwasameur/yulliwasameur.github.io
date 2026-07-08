# Mise à jour du site yulliwasameur.github.io — mode d'emploi

Deux façons d'appliquer la mise à jour (au choix), depuis votre dépôt local `yulliwasameur.github.io` :

## Option 1 — patch git (recommandé, gère aussi les suppressions)

```bash
git checkout master   # ou main selon votre dépôt
git am site-update.patch
git push origin master
```

Si `git am` échoue (historique différent) : `git apply site-update.patch && git add -A && git commit -m "Update site" && git push`.

## Option 2 — zip

1. Dézippez `site-update.zip` à la racine du dépôt (écrase les fichiers modifiés, ajoute les nouveaux).
2. Supprimez les 8 fichiers d'exemple du template :

```bash
git rm _publications/2009-10-01-paper-title-number-1.md _publications/2010-10-01-paper-title-number-2.md \
  _talks/2021-12-07-ML4PSP-Talk.md _talks/2022-07-20-Cospar-Talk.md _talks/2022-11-24-APEX-Talk.md _talks/2022-12-15-AGU-Poster.md \
  _teaching/2019-private-tutoring.md _teaching/2022-research-software-engineering-with-python.md
git add -A && git commit -m "Update site" && git push
```

GitHub Pages reconstruira le site automatiquement (1 à 2 minutes).

## Contenu de la mise à jour

- `_config.yml` : description et bio « Teacher-Researcher in Cybersecurity — Efrei Research Lab », employeur, e-mail efrei.fr, lien vers le CV HAL ;
- `_pages/about.md` : biographie entièrement réécrite (poste actuel, thèse, parcours, thématiques, certifications, associations, lien HAL) ;
- `_pages/cv.md` : le lien CV pointe désormais vers `files/CV_Yulliwas_AMEUR.pdf` (inclus, version corrigée du jour) au lieu de l'ancien Google Drive ;
- `_publications/` : 10 fiches créées (chapitres Springer 2023 et 2026, chapitre blockchain 2025, article JCSM 2024, ANT 2023/2024/2026, PSD 2022, thèse, jeu de données GovSecLLM++) ;
- `_talks/` : 4 exposés (ILCE Neuchâtel 2023, Campus Cyber/Systematic 2023, USTHB Alger 2022, séminaire CEDRIC 2021) ;
- `_teaching/` : 5 fiches (Efrei depuis 2024, ATER Assas, vacations 2023-2024, ULB/Bamenda, Cnam) ;
- suppression des exemples du template (publications, talks, teaching factices qui polluaient le site).

Après le push, vérifiez : https://yulliwasameur.github.io/ (bio), /publications/, /talks/, /teaching/, /cv/.
