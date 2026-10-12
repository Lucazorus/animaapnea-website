# Réécriture native — consignes communes

Objectif : chaque langue doit se lire comme si elle avait été écrite directement par un rédacteur natif, spécialiste de l'apnée, pour ce marché. Pas de traduction littérale, pas de calque de syntaxe, pas de tournure qui « sent » la traduction.

## Ce qu'on réécrit
1. Les 14 articles de la langue : `blog/<lang>/<fichier>` (liste dans `blog/_data/slugs.json`).
2. Les textes de la landing pour cette langue : écrire un fichier `blog/_data/landing/<lang>.json` (objet JSON, mêmes clés que l'entrée `en` de `i18n.js` à la racine du site, plus une clé `title` = titre de la page pour le navigateur). Garder `{t}` dans `dialResult`, les balises `<strong>…</strong>` dans `tbFact1-3`, `days` = 7 abréviations séparées par des virgules en commençant par lundi, `week` peut contenir `{n}` pour placer le numéro.

## Méthode
- Partir du SENS (version française = référence ; anglais en appui), jamais des phrases. Réécrire titres, chapô, paragraphes, intertitres, encadrés, légendes, textes des schémas SVG, `data-labels`, FAQ (visible ET JSON-LD identiques), méta (title ≤ 65 caractères terminé par ` | Anima Apnea`, description 140–160 caractères, ou longueur naturelle en ja/zh), fil d'Ariane, signature, encadré auteur, CTA, cartes « à lire ensuite ».
- Vocabulaire d'apnée réellement employé par les apnéistes de ce pays (clubs, fédérations, forums), registre et forme d'adresse naturels pour un contenu sportif/santé grand public dans cette langue.
- Phrases au rythme naturel de la langue ; supprimer les répétitions et lourdeurs ; titres courts et idiomatiques.

## Ce qui ne change pas
- Faits, chiffres, protocoles, sources (titres des sources en anglais), numéros de références, avertissements de sécurité (aucun ne doit être affaibli), affirmations sur l'app (ne rien ajouter).
- Structure HTML, classes, ids, scripts, `<!--ALTERNATES-->` ou bloc hreflang existant, canonical, attributs de données numériques, géométrie des SVG (raccourcir un libellé plutôt que de déborder), liens internes (noms de fichiers de `slugs.json`).

## Vérification
- `python3 blog/_data/check.py <fichiers>` doit renvoyer OK pour chaque article.
- Le JSON de la landing doit être valide (`python3 -m json.tool blog/_data/landing/<lang>.json`).
- Ne modifier aucun autre fichier, pas de git.
