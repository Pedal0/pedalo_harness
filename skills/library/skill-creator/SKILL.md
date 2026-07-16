---
name: skill-creator
description: Créer un nouveau skill ou améliorer un skill existant de ce harness. Utilise ce skill dès que l'utilisateur veut créer un skill, ajouter une capacité réutilisable, transformer un workflow de la conversation en skill, ou modifier/optimiser un skill existant même s'il ne prononce pas le mot "skill".
---

# Skill Creator

Un skill pour créer des skills. Suis ce processus dans l'ordre.

## RÈGLE ABSOLUE À LIRE EN PREMIER

Ta première réponse après avoir lu ce skill doit contenir UNIQUEMENT les
questions de l'étape 1 posées à l'utilisateur. Aucun tool call, aucune
création de fichier. Tu n'appelles write_file qu'APRÈS que l'utilisateur
a répondu aux questions dans un message ultérieur.

## Étape 1 : Comprendre l'intention

Avant d'écrire quoi que ce soit, obtiens les réponses à ces questions
(depuis la conversation si elles y sont déjà, sinon pose-les à l'utilisateur) :

1. Que doit permettre ce skill ?
2. Quand doit-il se déclencher ? (quelles phrases/contextes utilisateur)
3. Quel est le format de sortie attendu ?
4. Y a-t-il des étapes fixes, des pièges connus, des exemples de référence ?

Ne passe à l'étape 2 qu'avec ces réponses confirmées par l'utilisateur.

## Étape 2 : Anatomie d'un skill

Un skill est un DOSSIER dans skills/library/ :

    skills/library/nom-du-skill/
    ├── SKILL.md          (obligatoire)
    └── references/       (optionnel : docs détaillées chargées au besoin)

Le SKILL.md commence par un frontmatter YAML entre deux lignes "---" :

    ---
    name: nom-du-skill
    description: Ce que fait le skill ET quand l'utiliser.
    ---

Règles strictes du frontmatter :
- name : minuscules et tirets, identique au nom du dossier.
- description : UNE seule ligne (pas de retour à la ligne dans la valeur).
- Tout le "quand l'utiliser" va dans la description, jamais dans le corps.

## Étape 3 : Écrire la description (le plus important)

La description est le SEUL texte que le modèle voit en permanence :
c'est elle qui déclenche ou non la lecture du skill.

- Inclus ce que fait le skill ET les contextes précis d'utilisation.
- Les modèles sous-déclenchent : rends la description légèrement insistante.
  Exemple : au lieu de "Aide à créer des dashboards", écris "Créer des
  dashboards de données. À utiliser dès que l'utilisateur mentionne un
  dashboard, une visualisation, des métriques ou l'affichage de données,
  même sans le mot dashboard."
- Ajoute "uniquement quand..." si le skill risque de sur-déclencher.

## Étape 4 : Écrire le corps

- Étapes numérotées, impératives, ordonnées. Pas de paragraphes vagues.
- Reste sous ~150 lignes. Au-delà, déplace les détails dans
  references/nom.md et écris dans le corps : "Pour X, lis d'abord
  references/nom.md dans ce dossier de skill."
- Inclus les commandes exactes, formats exacts, exemples concrets.
- N'invente aucune capacité : ce harness a les tools read_file,
  write_file et bash (PowerShell, avec confirmation utilisateur).

## Étape 5 : Créer les fichiers

1. Vérifie avec read_file qu'aucun skill du même nom n'existe déjà
   dans skills/library/.
2. Crée le fichier avec write_file :
   skills/library/nom-du-skill/SKILL.md
   (write_file crée le dossier automatiquement).
3. Relis le fichier créé avec read_file pour vérifier que le frontmatter
   est intact (commence bien par "---", name et description présents).

## Étape 6 : Tester avec l'utilisateur

Le loader ne charge les skills qu'au démarrage : demande à l'utilisateur
de relancer le harness, puis propose-lui 2 ou 3 phrases de test :
- une qui DOIT déclencher le skill,
- une proche mais qui ne doit PAS le déclencher.
Si le déclenchement échoue, améliore la description (étape 3) et refais tester.

## Si l'utilisateur veut modifier un skill existant

- Lis d'abord le SKILL.md existant en entier.
- Conserve le name d'origine.
- Réécris le fichier complet avec write_file (pas de modification partielle).