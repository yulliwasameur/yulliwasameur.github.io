---
layout: archive
title: "Logiciels"
permalink: /logiciels/
author_profile: true
description: "Logiciels et outils libres de Yulliwas Ameur : KabOCR, OCR gratuit pour le kabyle."
---

Des outils libres, utilisables par tout le monde, publiés avec leur code, leur licence et un DOI pour pouvoir les citer.

## KabOCR — OCR du kabyle

**[Essayer KabOCR en ligne](https://yulliwasameur.github.io/kabocr/)**

Déposez un PDF ou une image en kabyle (écriture latine). KabOCR reconnaît le texte. Vous pouvez ensuite le copier, le télécharger en `.txt` ou récupérer un **PDF cherchable**. **Tout se passe dans votre navigateur** : le fichier n'est envoyé nulle part.

- **Précision** : environ 0,9 % d'erreur par caractère sur des mémoires imprimés, 1,7 % sur des livres. Ces textes n'avaient jamais été vus par le modèle. C'est mieux que les modèles kabyles publics testés.
- **Limites** : imprimé en écriture latine seulement. Ni tifinagh, ni manuscrit. La lettre ţ et la notation phonétique ne sont pas encore reconnues. Relisez toujours le texte.
- **Pour les développeurs** : modèle Tesseract à télécharger, outil en ligne de commande, et boîte à outils d'évaluation `kabocr-eval`, qui mesure aussi les erreurs sur les lettres kabyles (ɛ, ɣ, ḍ…).
- **Code et modèle** : [github.com/yulliwasameur/kabocr](https://github.com/yulliwasameur/kabocr). Code sous Apache-2.0, modèle sous CC BY-SA 4.0.
- **Citer** : Ameur, Y. (2026). *KabOCR: open OCR for Kabyle (Latin script)*, version 0.1.0 [Logiciel]. Zenodo. [https://doi.org/10.5281/zenodo.24111659](https://doi.org/10.5281/zenodo.24111659)

<small>*In English* — KabOCR is free OCR for Kabyle (Latin script). It runs entirely in the browser: drop a PDF, get the text and a searchable PDF. Code: Apache-2.0; model: CC BY-SA 4.0; DOI: [10.5281/zenodo.24111659](https://doi.org/10.5281/zenodo.24111659).</small>
