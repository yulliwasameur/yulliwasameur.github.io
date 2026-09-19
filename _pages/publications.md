---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
description: "Publications scientifiques, thèse, prépublication, logiciels et jeux de données de Yulliwas Ameur en cybersécurité, cryptographie et apprentissage automatique préservant la vie privée."
---

Cette page distingue les publications évaluées par les pairs des autres productions de recherche. Les notices HAL et les DOI éditeurs sont fournis lorsqu'ils sont disponibles. Mon [CV HAL](https://cv.hal.science/yulliwas-ameur) reste la source institutionnelle de référence.

[Download the bibliography (BibTeX)](/files/publications.bib) · [Subscribe to publications (Atom)](/feed/publications.xml) · [Research code and artifacts](/code/) · [Research highlights in English](/research-highlights/)

## Publications évaluées par les pairs

{% assign sorted_publications = site.publications | sort: "date" | reverse %}
{% for post in sorted_publications %}
  {% if post.output_type == "peer-reviewed" %}
    {% include archive-single.html %}
  {% endif %}
{% endfor %}

## Contributions récentes et actes à paraître

Le statut et les versions disponibles sont précisés dans chaque fiche.

{% for post in sorted_publications %}
  {% if post.output_type == "conference-record" %}
    {% include archive-single.html %}
  {% endif %}
{% endfor %}

## Prépublication

{% for post in sorted_publications %}
  {% if post.output_type == "preprint" %}
    {% include archive-single.html %}
  {% endif %}
{% endfor %}

## Thèse

{% for post in sorted_publications %}
  {% if post.output_type == "thesis" %}
    {% include archive-single.html %}
  {% endif %}
{% endfor %}

## Logiciels et jeux de données

{% for post in sorted_publications %}
  {% if post.output_type == "software" or post.output_type == "dataset" %}
    {% include archive-single.html %}
  {% endif %}
{% endfor %}

## Évaluation scientifique ouverte

{% for post in sorted_publications %}
  {% if post.output_type == "open-review" %}
    {% include archive-single.html %}
  {% endif %}
{% endfor %}

[Research highlights in English: contributions, evidence and citation links](/research-highlights/)
