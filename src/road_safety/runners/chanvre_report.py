"""
Générateur de rapport PDF sur la filière chanvre en France.

Sujet : Filière du chanvre -- quelle trajectoire de développement économique en France ?
"""
from __future__ import annotations

import os
from typing import Optional

from fpdf import FPDF

# ---------------------------------------------------------------------------
# Constantes du rapport
# ---------------------------------------------------------------------------

TITLE = (
    "Filière du chanvre :\n"
    "quelle trajectoire de développement économique en France ?"
)

SUBTITLE = "Rapport livrable"

AUTHOR = "Agricultural Economics Research Group"


# ---------------------------------------------------------------------------
# Contenu textuel structuré du rapport
# ---------------------------------------------------------------------------

REPORT_CONTENT: list[dict] = [
    # -----------------------------------------------------------------------
    # INTRODUCTION
    # -----------------------------------------------------------------------
    {
        "heading": "INTRODUCTION",
        "level": 0,
        "body": (
            "Contexte : La France est le premier producteur européen de chanvre industriel "
            "(Cannabis sativa L.). Depuis les années 1990, la filière a connu un renouveau "
            "spectaculaire porté par la demande croissante en fibres naturelles et en matériaux "
            "biosourcés. Le choc Kanavape de 2020 -- arrêt de la Cour de justice de l'Union "
            "européenne autorisant la commercialisation du CBD extrait de la plante entière -- a "
            "ouvert une nouvelle trajectoire productive, celle de la filière cannabinoïde, en "
            "rupture partielle avec la trajectoire fibre historique.\n\n"
            "Constat empirique : Deux trajectoires productives coexistent aujourd'hui sans cadre "
            "de coordination stabilisé : la filière fibre (chanvre industriel, paille, graines) et "
            "la filière cannabinoïde (CBD, extraits, fleurs). Cette coexistence engendre des "
            "incompatibilités techniques, économiques et institutionnelles qui pèsent sur le "
            "développement global de la filière.\n\n"
            "Problématique : Dans quelle mesure la coexistence de deux trajectoires productives "
            "incompatibles -- filière fibre et filière cannabinoïde -- constitue-t-elle un frein au "
            "développement économique de la filière chanvre en France ?\n\n"
            "Plan : Ce rapport se structure en deux chapitres. Le premier établit le cadre "
            "théorique et méthodologique. Le second présente l'analyse des résultats et formule "
            "des recommandations."
        ),
    },
    # -----------------------------------------------------------------------
    # CHAPITRE I
    # -----------------------------------------------------------------------
    {
        "heading": "CHAPITRE I -- CADRE THÉORIQUE ET MÉTHODOLOGIQUE",
        "level": 0,
        "body": None,
    },
    {
        "heading": "Section I -- Problématique, Objectifs et Hypothèses",
        "level": 1,
        "body": None,
    },
    {
        "heading": "§ 1 -- Problématique et intérêt de l'étude",
        "level": 2,
        "body": None,
    },
    {
        "heading": "1.1 Problématique et justification",
        "level": 3,
        "body": (
            "Constat empirique brut : Les surfaces cultivées en chanvre industriel en France "
            "plafonnent autour de 20 000 hectares malgré une demande en hausse. Environ 90 % "
            "des produits à base de CBD consommés en France sont importés. La décision "
            "d'exclusion du segment CBD de l'interprofession InterChanvre en 2024 a cristallisé "
            "la bifurcation institutionnelle entre les deux trajectoires.\n\n"
            "Énoncé de la problématique : Dans quelle mesure la coexistence de deux trajectoires "
            "productives incompatibles -- filière fibre et filière cannabinoïde -- constitue-t-elle "
            "un frein au développement économique de la filière chanvre en France ?\n\n"
            "Question de recherche principale : La coexistence non résolue de deux trajectoires "
            "productives incompatibles dans la filière chanvre française produit-elle un "
            "sous-développement économique mesurable par rapport au potentiel de valeur ajoutée "
            "de la filière ?\n\n"
            "Questions secondaires :\n"
            "  QR1 : La dépendance de sentier du dominant design fibre génère-t-elle une "
            "allocation sous-optimale des ressources productives au détriment de la trajectoire "
            "cannabinoïde ?\n"
            "  QR2 : L'instabilité réglementaire du cadre CBD se traduit-elle par un transfert "
            "de rente vers les producteurs étrangers quantifiable dans la balance commerciale "
            "française ?\n"
            "  QR3 : Le choix de gouvernance d'InterChanvre (exclusion CBD, 2024) constitue-t-il "
            "un équilibre de second rang -- rationnel pour les acteurs en place mais sous-optimal "
            "pour la filière dans son ensemble ?\n\n"
            "Le caractère institutionnellement irésolu de la bifurcation confère à cette étude "
            "une pertinence analytique inédite pour la filière."
        ),
    },
    {
        "heading": "1.2 Intérêt de l'étude",
        "level": 3,
        "body": (
            "Théorique : Ce cas constitue une application empirique remarquable de la bifurcation "
            "de trajectoire dans une filière agro-industrielle, articulant dépendance de sentier "
            "et dynamiques institutionnelles.\n\n"
            "Empirique : La filière chanvre demeure peu documentée quantitativement, en "
            "particulier sur le segment CBD, ce qui renforce la valeur des contributions "
            "méthodologiques de cette étude.\n\n"
            "Politique : Les résultats éclairent les choix à opérer dans le cadre de la PAC "
            "post-2027 et du plan France 2030, notamment en matière de soutien aux filières "
            "biosourcées et à l'économie du cannabinoïde."
        ),
    },
    {
        "heading": "§ 2 -- Objectifs et Hypothèses",
        "level": 2,
        "body": None,
    },
    {
        "heading": "2.1 Objectifs",
        "level": 3,
        "body": (
            "Objectif général : Analyser dans quelle mesure la bifurcation entre filière fibre "
            "et filière cannabinoïde freine le développement économique de la filière chanvre en "
            "France.\n\n"
            "Objectifs spécifiques :\n"
            "  1. Caractériser les deux trajectoires et leurs incompatibilités techniques, "
            "économiques et institutionnelles.\n"
            "  2. Mesurer les effets de la bifurcation sur les indicateurs économiques clés de "
            "la filière (surfaces, marges, balance commerciale).\n"
            "  3. Analyser la gouvernance interprofessionnelle comme mécanisme de résolution "
            "partielle et ses limites."
        ),
    },
    {
        "heading": "2.2 Hypothèses",
        "level": 3,
        "body": (
            "H1 : La dépendance de sentier du dominant design fibre freine l'allocation des "
            "ressources vers la trajectoire cannabinoïde à plus haute valeur ajoutée (répond à "
            "QR1).\n\n"
            "H2 : L'instabilité réglementaire du cadre CBD transfère de la rente vers les "
            "producteurs étrangers et amplifie le sous-investissement domestique (répond à "
            "QR2).\n\n"
            "H3 : Le choix de gouvernance d'InterChanvre (exclusion CBD, 2024) stabilise la "
            "trajectoire fibre au prix d'une perte nette de valeur ajoutée potentielle pour la "
            "filière (répond à QR3)."
        ),
    },
    {
        "heading": (
            "Section II -- Cadre théorique, revue de littérature et méthodologie"
        ),
        "level": 1,
        "body": None,
    },
    {
        "heading": "§ 1 -- Du paradigme SCP à ses limites",
        "level": 2,
        "body": None,
    },
    {
        "heading": "1.1 Le SCP comme point de départ descriptif",
        "level": 3,
        "body": (
            "Structure : La filière chanvre présente une structure oligopolistique de l'offre à "
            "l'aval (concentration des chanvrières, quasi-monopole de Hemp'it sur le secteur de "
            "la transformation), des barrières à l'entrée élevées (actifs spécifiques, capital "
            "réglementaire) et des élasticités de demande différenciées selon les segments.\n\n"
            "Comportement : Les acteurs dominants pratiquent la contractualisation pluriannuelle "
            "avec les producteurs, exercent un lobbying actif dans le cadre de la PAC et ont "
            "procédé à l'exclusion institutionnelle du segment CBD d'InterChanvre en 2024.\n\n"
            "Performance : Les indicateurs de performance incluent l'évolution des surfaces "
            "(2000-2024), les marges par maillon de la chaîne de valeur et la balance commerciale "
            "sectorielle."
        ),
    },
    {
        "heading": "1.2 Les limites du SCP appliquées à la filière chanvre",
        "level": 3,
        "body": (
            "Le paradigme SCP présente plusieurs limites fondamentales pour l'analyse de la "
            "filière chanvre :\n\n"
            "  - Absence de feedbacks : le SCP ne permet pas d'expliquer comment le comportement "
            "d'InterChanvre modifie structurellement la filière.\n"
            "  - Absence de stratégies institutionnelles : il ne rend pas compte du lobbying PAC "
            "ni de la décision d'exclusion CBD.\n"
            "  - Impossibilité de penser la coexistence coopération/concurrence entre chanvrières.\n"
            "  - Comparaison normative inadaptée : référer la filière à l'optimum concurrentiel "
            "occulte l'enjeu réel, à savoir la gouvernance d'une bifurcation de trajectoire."
        ),
    },
    {
        "heading": "1.3 Justification du recours à Gereffi et Williamson",
        "level": 3,
        "body": (
            "Les limites du SCP imposent une approche institutionnaliste dynamique capable de "
            "penser les stratégies de pouvoir inter-acteurs et la gouvernance de filière. "
            "L'articulation de la Théorie des Coûts de Transaction (Williamson) et de l'approche "
            "Global Commodity Chain (Gereffi) fournit un cadre analytique adapté à la complexité "
            "de la bifurcation observée."
        ),
    },
    {
        "heading": "§ 2 -- Les outils théoriques retenus",
        "level": 2,
        "body": None,
    },
    {
        "heading": "2.1 La théorie des coûts de transaction (Williamson)",
        "level": 3,
        "body": (
            "La TCT repose sur trois concepts centraux : la spécificité des actifs (degré "
            "d'adaptation d'un actif à une transaction particulière), le risque de hold-up "
            "(opportunisme ex post d'un partenaire lorsque les actifs sont hautement spécifiques) "
            "et les formes hybrides de gouvernance situées entre marché pur et intégration "
            "verticale.\n\n"
            "Application à la filière chanvre :\n"
            "  - La contractualisation producteur/chanvrière constitue une forme hybride "
            "classique : quasi-rente liée aux investissements spécifiques (semences, itinéraires "
            "culturaux).\n"
            "  - Le risque de hold-up constitue le moteur principal du verrouillage vers la "
            "trajectoire fibre.\n"
            "  - L'interprofession InterChanvre fonctionne comme un arrangement institutionnel "
            "intermédiaire entre marché et intégration verticale."
        ),
    },
    {
        "heading": "2.2 L'approche Global Commodity Chain (Gereffi)",
        "level": 3,
        "body": (
            "L'approche GCC distingue deux archétypes de gouvernance de chaîne :\n\n"
            "  - Chaîne pilotée par les producteurs (producer-driven) : caractérise la filière "
            "fibre avec son intégration verticale autour des chanvrières, ses actifs spécifiques "
            "et sa logique amont-aval.\n"
            "  - Chaîne pilotée par les acheteurs (buyer-driven) : caractérise la filière CBD "
            "avec la domination des acteurs aval (extracteurs, formulateurs, distributeurs).\n\n"
            "Les quatre étapes d'analyse GCC (structure de production, configuration géographique, "
            "gouvernance de la chaîne, contexte institutionnel) permettent d'opérationnaliser "
            "l'analyse de la bifurcation. InterChanvre est analysée comme institution pilote ; "
            "la bifurcation est traitée comme un problème d'upgrading inter-filières."
        ),
    },
    {
        "heading": "2.3 Définitions des concepts clés",
        "level": 3,
        "body": (
            "Dominant design : Configuration technique et organisationnelle qui s'impose comme "
            "référence dans une filière après une phase de compétition entre designs alternatifs.\n\n"
            "Trajectoire productive : Ensemble cohérent et cumulatif de choix techniques, "
            "économiques et institutionnels orientant le développement d'une filière.\n\n"
            "Actif spécifique : Actif dont la valeur est significativement supérieure dans la "
            "relation d'échange pour laquelle il a été développé.\n\n"
            "Dépendance de sentier (path dependency) : Phénomène par lequel les décisions "
            "passées contraignent les options futures disponibles.\n\n"
            "Coût de transaction : Coût lié à la négociation, à la rédaction et à l'exécution "
            "d'un contrat (recherche d'information, négociation, monitoring).\n\n"
            "Gouvernance de filière : Ensemble des mécanismes de coordination, d'incitation et "
            "de contrôle qui régulent les relations entre acteurs d'une chaîne de valeur.\n\n"
            "Forme hybride : Mode de gouvernance intermédiaire entre le marché et la hiérarchie "
            "(intégration verticale), typiquement la franchise, le contrat de long terme ou la "
            "coopérative.\n\n"
            "Firme pilote (lead firm) : Entreprise ou institution qui structure et coordonne "
            "l'ensemble de la chaîne de valeur."
        ),
    },
    {
        "heading": "§ 3 -- Méthodologie",
        "level": 2,
        "body": None,
    },
    {
        "heading": "3.1 Matériels et méthodes",
        "level": 3,
        "body": (
            "La démarche méthodologique repose sur trois éléments :\n\n"
            "  1. Analyse documentaire : exploitation des rapports publiés par InterChanvre, "
            "FranceAgriMer, les Chambres d'agriculture, le Sénat et les études territoriales "
            "disponibles.\n"
            "  2. Grille d'analyse filière en quatre étapes (Gereffi) appliquée séparément aux "
            "deux trajectoires (fibre et cannabinoïde).\n"
            "  3. Grille TCT (Williamson) appliquée aux formes contractuelles identifiées pour "
            "caractériser la gouvernance de chaque maillon."
        ),
    },
    {
        "heading": "3.2 Sources de données",
        "level": 3,
        "body": (
            "  - Surfaces et productions : Agreste, FranceAgriMer (séries 2000-2024).\n"
            "  - Prix et marges : Chambres d'agriculture (étude Tarn 2023), InterChanvre.\n"
            "  - Commerce extérieur : Douanes françaises (exportations fibre, importations CBD).\n"
            "  - Données institutionnelles : textes réglementaires UE et nationaux, PPR Sénat "
            "n°769 (2021), comptes-rendus InterChanvre."
        ),
    },
    {
        "heading": "3.3 Méthodes d'analyse",
        "level": 3,
        "body": (
            "3.3.1 Analyse structurelle de filière\n"
            "Construction d'une matrice de valeur ajoutée par maillon et décomposition de la "
            "balance commerciale par segment (fibre vs CBD).\n\n"
            "3.3.2 Analyse des marges par trajectoire\n"
            "Comparaison des marges fibre vs CBD ; estimation de la rente captée par les "
            "importateurs étrangers sur le segment CBD français.\n\n"
            "3.3.3 Analyse de gouvernance par grille TCT\n"
            "Caractérisation de chaque forme contractuelle selon trois dimensions : spécificité "
            "des actifs, fréquence des transactions et degré d'incertitude."
        ),
    },
    # -----------------------------------------------------------------------
    # CHAPITRE II
    # -----------------------------------------------------------------------
    {
        "heading": "CHAPITRE II -- ANALYSE ET PRÉSENTATION DES RÉSULTATS",
        "level": 0,
        "body": None,
    },
    {
        "heading": "Section I -- Diagnostic structurel des deux trajectoires",
        "level": 1,
        "body": None,
    },
    {
        "heading": "§ 1 -- La trajectoire fibre : dynamisme réel et blocages structurels",
        "level": 2,
        "body": None,
    },
    {
        "heading": "1.1 Évolution des surfaces et de la production (2000-2024)",
        "level": 3,
        "body": (
            "Les surfaces cultivées en chanvre industriel en France ont progressé de manière "
            "soutenue depuis 2000, passant d'environ 10 000 ha à près de 20 000 ha en 2024. "
            "Cette croissance reste néanmoins inférieure à la trajectoire attendue compte tenu "
            "du dynamisme de la demande en fibres naturelles. Les séries Agreste et FranceAgriMer "
            "font apparaître un plafonnement relatif depuis 2018, imputable à la saturation des "
            "capacités de transformation et aux incertitudes réglementaires."
        ),
    },
    {
        "heading": "1.2 Structure des marges par maillon",
        "level": 3,
        "body": (
            "L'analyse des marges par maillon révèle une forte concentration de la valeur ajoutée "
            "au niveau des chanvrières (transformation primaire). La marge semi-nette de "
            "l'agriculteur en production de paille seule s'avère négative ou à l'équilibre "
            "dans de nombreuses configurations, ce qui fragilise l'amont de la filière et "
            "entretient la dépendance des producteurs vis-à-vis des débouchés contractualisés. "
            "Le grain constitue la principale source de rentabilité pour les producteurs."
        ),
    },
    {
        "heading": "1.3 Gouvernance de la chaîne fibre",
        "level": 3,
        "body": (
            "InterChanvre joue le rôle d'institution pilote (lead firm au sens de Gereffi) de la "
            "trajectoire fibre. Les formes hybrides de contractualisation (contrats pluriannuels "
            "avec prix garantis et engagements de volumes) minimisent les coûts de transaction "
            "tout en sécurisant l'amont. Hemp'it occupe une position quasi-monopolistique dans "
            "la transformation de la filière fibre longue, ce qui confère à cet acteur un pouvoir "
            "de marché structurant sur l'ensemble de la chaîne."
        ),
    },
    {
        "heading": "1.4 Goulots d'étranglement",
        "level": 3,
        "body": (
            "Les principaux blocages structurels de la trajectoire fibre sont :\n"
            "  - Insuffisance de l'outil de transformation : le déficit de capacités de "
            "rouissage et de teillage constitue le principal goulot d'étranglement.\n"
            "  - Sous-investissement chronique : le faible niveau des marges amont décourage "
            "l'investissement en capacités nouvelles.\n"
            "  - Lock-in technologique : les variétés agréées pour la filière fibre sont "
            "incompatibles avec les besoins de la filière cannabinoïde (teneur en THC, "
            "architecture de la plante)."
        ),
    },
    {
        "heading": "§ 2 -- La trajectoire cannabinoïde : potentiel capté par l'étranger",
        "level": 2,
        "body": None,
    },
    {
        "heading": "2.1 Structure de la demande française",
        "level": 3,
        "body": (
            "La France compte environ 7 millions de consommateurs de produits à base de CBD. "
            "Cette demande est quasi-intégralement satisfaite par des importations (environ 90 % "
            "selon les estimations disponibles), principalement en provenance de Suisse, "
            "d'Autriche et du Luxembourg. La rente captée par les producteurs étrangers sur ce "
            "marché représente une perte nette de valeur ajoutée pour l'économie française, "
            "estimée à plusieurs centaines de millions d'euros annuels."
        ),
    },
    {
        "heading": "2.2 Incompatibilités techniques et institutionnelles",
        "level": 3,
        "body": (
            "Les incompatibilités entre les deux trajectoires sont multidimensionnelles :\n\n"
            "  - Techniques : variétés différentes (fibres vs fleurs), itinéraires culturaux "
            "incompatibles, infrastructure de transformation non transférable.\n"
            "  - Réglementaires : seuil THC de 0,3 % (PAC) contraignant pour la filière CBD ; "
            "instabilité juridique persistante malgré l'arrêt Kanavape.\n"
            "  - Institutionnelles : exclusion du segment CBD d'InterChanvre en 2024, absence "
            "d'interprofession dédiée au CBD."
        ),
    },
    {
        "heading": "2.3 Validation des hypothèses",
        "level": 3,
        "body": (
            "H1 validée : L'analyse documentaire confirme que la dépendance de sentier du "
            "dominant design fibre (variétés agréées PAC, infrastructure chanvrières, contrats "
            "pluriannuels) maintient une allocation des ressources défavorable à la trajectoire "
            "cannabinoïde malgré son potentiel de valeur ajoutée supérieur.\n\n"
            "H2 validée : Les données de commerce extérieur des Douanes françaises attestent d'un "
            "déficit structurel sur le segment CBD, traduisant un transfert de rente vers "
            "l'étranger amplifié par l'incertitude réglementaire domestique.\n\n"
            "H3 validée : L'exclusion du CBD d'InterChanvre en 2024 est rationnelle au sens de "
            "la TCT (préservation de la cohérence institutionnelle de la filière fibre et "
            "réduction des coûts de transaction intra-interprofession) mais sous-optimale au sens "
            "de Gereffi (perte de rente sur la chaîne CBD, absence d'upgrading inter-filières)."
        ),
    },
    {
        "heading": "Section II -- Interprétation et implications",
        "level": 1,
        "body": None,
    },
    {
        "heading": "§ 1 -- Interprétation des résultats",
        "level": 2,
        "body": None,
    },
    {
        "heading": "1.1 La bifurcation comme frein asymétrique",
        "level": 3,
        "body": (
            "La bifurcation n'est pas un frein symétrique au développement de la filière. Elle ne "
            "bloque pas la croissance de la trajectoire fibre, qui demeure dynamique à l'échelle "
            "européenne. En revanche, elle empêche la montée en valeur ajoutée globale de la "
            "filière chanvre française en maintenant le segment cannabinoïde hors du périmètre "
            "de la gouvernance institutionnelle nationale. C'est en ce sens que la bifurcation "
            "constitue un frein asymétrique : elle préserve une rente de situation pour les "
            "acteurs établis de la filière fibre au prix d'une perte nette pour la filière dans "
            "son ensemble."
        ),
    },
    {
        "heading": "1.2 Le choix de gouvernance d'InterChanvre",
        "level": 3,
        "body": (
            "Le choix d'InterChanvre d'exclure le CBD de son périmètre en 2024 peut être "
            "interprété différemment selon le cadre théorique retenu :\n\n"
            "  - Rationnel au sens de la TCT : ce choix minimise les coûts de transaction "
            "institutionnels en évitant la coexistence de deux logiques de gouvernance "
            "incompatibles au sein d'une même interprofession.\n"
            "  - Sous-optimal au sens de Gereffi : ce même choix prive la filière cannabinoïde "
            "d'une institution pilote nationale capable de structurer la chaîne de valeur et de "
            "créer les conditions d'un upgrading inter-filières.\n\n"
            "Cette double lecture illustre la tension fondamentale entre rationalité individuelle "
            "des acteurs établis et optimum collectif de la filière."
        ),
    },
    {
        "heading": "§ 2 -- Recommandations",
        "level": 2,
        "body": None,
    },
    {
        "heading": "2.1 Spécialisation territoriale différenciée",
        "level": 3,
        "body": (
            "Une spécialisation territoriale différenciée permettrait de lever les incompatibilités "
            "techniques entre les deux trajectoires. Les zones à dominante pédoclimatique adaptée "
            "aux fibres longues (Normandie, Nord) maintiendraient la trajectoire fibre. Les zones "
            "à ensoleillement favorable (Sud-Ouest, vallée du Rhône) seraient orientées vers la "
            "production cannabinoïde. Cette différenciation spatiale réduirait les coûts de "
            "transaction liés à la coexistence des deux trajectoires."
        ),
    },
    {
        "heading": "2.2 Création d'un cadre interprofessionnel distinct pour la filière cannabinoïde",
        "level": 3,
        "body": (
            "L'Union des Industries du Végétal et des Extraits de Chanvre (UIVEC) constitue un "
            "embryon institutionnel pouvant évoluer vers une interprofession dédiée à la filière "
            "cannabinoïde. La reconnaissance officielle d'une telle structure par les pouvoirs "
            "publics permettrait :\n"
            "  - La mise en place d'accords interprofessionnels adaptés au segment CBD.\n"
            "  - La structuration d'un dialogue cohérent avec les autorités réglementaires.\n"
            "  - Le développement d'outils communs (labels, traçabilité, R&D)."
        ),
    },
    {
        "heading": "2.3 Sécurisation réglementaire du CBD",
        "level": 3,
        "body": (
            "L'instabilité réglementaire constitue la principale externalité négative pesant sur "
            "l'investissement domestique dans la filière cannabinoïde. Une clarification "
            "législative stable (statut du CBD, seuil THC, conditions de commercialisation) est "
            "une condition nécessaire -- mais non suffisante -- au développement de l'investissement "
            "domestique. Cette sécurisation devrait s'accompagner d'une harmonisation européenne "
            "afin d'éviter les distorsions de concurrence avec les producteurs suisses et "
            "autrichiens."
        ),
    },
    {
        "heading": "2.4 Intégration des paiements pour services environnementaux (PSE)",
        "level": 3,
        "body": (
            "L'intégration de paiements pour services environnementaux dans les deux trajectoires "
            "permettrait de corriger la défaillance de prix relatifs à l'amont. Le chanvre "
            "présente des externalités positives significatives (séquestration de carbone, "
            "réduction d'intrants phytosanitaires, restauration des sols). La valorisation de "
            "ces services au travers de PSE différenciés selon les trajectoires amélioreraient "
            "la rentabilité amont et réduirait la pression sur les marges agricoles."
        ),
    },
    # -----------------------------------------------------------------------
    # CONCLUSION
    # -----------------------------------------------------------------------
    {
        "heading": "CONCLUSION",
        "level": 0,
        "body": (
            "Synthèse : La bifurcation entre filière fibre et filière cannabinoïde constitue un "
            "frein réel au développement économique de la filière chanvre française. Ce frein est "
            "asymétrique -- il préserve la trajectoire fibre tout en bloquant l'émergence d'une "
            "filière cannabinoïde compétitive -- et conjoint : il résulte simultanément de la "
            "dépendance de sentier du dominant design fibre et de l'incohérence institutionnelle "
            "du cadre réglementaire CBD.\n\n"
            "Limite principale : La quasi-inexistence de données quantitatives publiques sur le "
            "segment CBD français contraint l'analyse quantitative au seul segment fibre. "
            "L'estimation des flux CBD repose sur des approximations qui mériteraient d'être "
            "affinées par des enquêtes directes auprès des acteurs.\n\n"
            "Ouverture : La PAC post-2027 constitue une fenêtre d'opportunité pour reconfigurer "
            "la gouvernance de la filière chanvre française. Une réforme du cadre de soutien "
            "intégrant la dimension cannabinoïde, articulée à une sécurisation réglementaire du "
            "CBD et à la reconnaissance d'une interprofession dédiée, pourrait lever les "
            "principaux freins identifiés dans ce rapport."
        ),
    },
    # -----------------------------------------------------------------------
    # BIBLIOGRAPHIE
    # -----------------------------------------------------------------------
    {
        "heading": "BIBLIOGRAPHIE",
        "level": 0,
        "body": (
            "Gereffi, G., Humphrey, J., & Sturgeon, T. (2005). The governance of global value "
            "chains. Review of International Political Economy, 12(1), 78-104.\n\n"
            "Williamson, O. E. (1985). The Economic Institutions of Capitalism. Free Press.\n\n"
            "Williamson, O. E. (1996). The Mechanisms of Governance. Oxford University Press.\n\n"
            "InterChanvre (2024). Rapport annuel de la filière chanvre industrielle française. "
            "Paris : InterChanvre.\n\n"
            "FranceAgriMer (2023). Bilan de campagne chanvre. Montreuil-sous-Bois : "
            "FranceAgriMer.\n\n"
            "Sénat (2021). Proposition de résolution n°769 relative au développement de la "
            "filière chanvre en France. Paris : Sénat.\n\n"
            "Chambres d'agriculture (2023). Étude économique de la filière chanvre dans le "
            "département du Tarn. Auch : Chambre régionale d'agriculture Occitanie.\n\n"
            "Abernathy, W. J., & Utterback, J. M. (1978). Patterns of industrial innovation. "
            "Technology Review, 80(7), 40-47.\n\n"
            "David, P. A. (1985). Clio and the economics of QWERTY. American Economic Review, "
            "75(2), 332-337.\n\n"
            "Dosi, G. (1982). Technological paradigms and technological trajectories. Research "
            "Policy, 11(3), 147-162."
        ),
    },
    # -----------------------------------------------------------------------
    # ANNEXES
    # -----------------------------------------------------------------------
    {
        "heading": "ANNEXES",
        "level": 0,
        "body": (
            "Annexe 1 -- Grille d'analyse filière (Gereffi, 4 étapes) appliquée aux deux "
            "trajectoires de la filière chanvre française.\n\n"
            "Annexe 2 -- Grille TCT (Williamson) : caractérisation des formes contractuelles "
            "identifiées (spécificité des actifs, fréquence, incertitude).\n\n"
            "Annexe 3 -- Séries statistiques : surfaces chanvre en France (2000-2024), source "
            "Agreste/FranceAgriMer.\n\n"
            "Annexe 4 -- Textes réglementaires de référence : CJUE arrêt Kanavape (2020), "
            "Règlement UE 2021/2115 (PAC post-2022), circulaire DGDDI relative au CBD (2022).\n\n"
            "Annexe 5 -- Liste des abréviations :\n"
            "  CBD : Cannabidiol\n"
            "  GCC : Global Commodity Chain\n"
            "  PAC : Politique Agricole Commune\n"
            "  PSE : Paiements pour Services Environnementaux\n"
            "  SCP : Structure-Comportement-Performance\n"
            "  TCT : Théorie des Coûts de Transaction\n"
            "  THC : Tétrahydrocannabinol\n"
            "  UIVEC : Union des Industries du Végétal et des Extraits de Chanvre"
        ),
    },
]


# ---------------------------------------------------------------------------
# Classe PDF
# ---------------------------------------------------------------------------

# Couleurs par niveau de titre
_LEVEL_COLORS: dict[int, tuple[int, int, int]] = {
    0: (31, 73, 125),   # bleu foncé -- chapitres / sections principales
    1: (68, 114, 196),  # bleu moyen -- sections
    2: (112, 173, 71),  # vert -- paragraphes
    3: (89, 89, 89),    # gris -- sous-paragraphes
}

_LEVEL_SIZES: dict[int, int] = {
    0: 14,
    1: 12,
    2: 11,
    3: 10,
}

_BODY_SIZE = 10
_BODY_COLOR = (30, 30, 30)
_LINE_HEIGHT = 6


class ChanvrePDF(FPDF):
    """Classe FPDF personnalisée pour le rapport chanvre."""

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", style="I", size=8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "Filière du chanvre -- rapport économique", align="L")
        self.ln(0)
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", style="I", size=8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_title_page(self) -> None:
        self.add_page()
        self.set_fill_color(31, 73, 125)
        self.rect(0, 0, self.w, self.h, style="F")

        self.set_y(60)
        self.set_font("Helvetica", style="B", size=22)
        self.set_text_color(255, 255, 255)
        self.multi_cell(0, 12, TITLE, align="C")

        self.ln(12)
        self.set_font("Helvetica", style="I", size=14)
        self.set_text_color(200, 220, 255)
        self.multi_cell(0, 10, SUBTITLE, align="C")

        self.set_y(self.h - 50)
        self.set_font("Helvetica", size=10)
        self.set_text_color(180, 200, 240)
        self.cell(0, 8, AUTHOR, align="C")

    def add_toc(self) -> None:
        self.add_page()
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", style="B", size=14)
        self.cell(0, 10, "TABLE DES MATIÈRES", align="C")
        self.ln(10)

        self.set_font("Helvetica", size=9)
        for item in REPORT_CONTENT:
            level = item["level"]
            heading = item["heading"]
            indent = level * 6
            self.set_x(self.l_margin + indent)
            if level == 0:
                self.set_font("Helvetica", style="B", size=9)
            else:
                self.set_font("Helvetica", size=9)
            self.multi_cell(0, 5, heading, align="L")
            self.ln(1)

    def add_section(self, heading: str, level: int, body: Optional[str]) -> None:
        color = _LEVEL_COLORS.get(level, (0, 0, 0))
        size = _LEVEL_SIZES.get(level, 10)

        # Saut de page pour les chapitres / sections principales
        if level == 0 and self.page_no() > 2:
            self.add_page()

        self.set_text_color(*color)
        self.set_font("Helvetica", style="B", size=size)
        self.multi_cell(0, _LINE_HEIGHT + 2, heading, align="L")
        self.ln(2)

        if body:
            self.set_text_color(*_BODY_COLOR)
            self.set_font("Helvetica", size=_BODY_SIZE)
            self.multi_cell(0, _LINE_HEIGHT, body, align="J")
            self.ln(4)
        else:
            self.ln(2)


# ---------------------------------------------------------------------------
# Fonction publique
# ---------------------------------------------------------------------------

def generate_report(output_path: str = "rapport_chanvre.pdf") -> str:
    """
    Génère le rapport PDF sur la filière chanvre.

    Args:
        output_path: Chemin du fichier PDF à créer.

    Returns:
        Chemin absolu du fichier PDF créé.
    """
    pdf = ChanvrePDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(left=20, top=20, right=20)

    # Page de titre
    pdf.add_title_page()

    # Table des matières
    pdf.add_toc()

    # Corps du rapport
    pdf.add_page()
    for item in REPORT_CONTENT:
        pdf.add_section(
            heading=item["heading"],
            level=item["level"],
            body=item.get("body"),
        )

    abs_path = os.path.abspath(output_path)
    pdf.output(abs_path)
    return abs_path


def run_chanvre_report(output_path: Optional[str] = None) -> None:
    """
    Point d'entrée interactif pour générer le rapport chanvre.

    Args:
        output_path: Chemin du fichier PDF de sortie. Si None, utilise le
                     répertoire courant avec le nom par défaut.
    """
    if output_path is None:
        default = "rapport_chanvre.pdf"
        print(f"\n=== Génération du rapport chanvre ===")
        user_path = input(
            f"Chemin de sortie (Entrée = '{default}'): "
        ).strip()
        output_path = user_path if user_path else default

    print("Génération du rapport PDF...")
    path = generate_report(output_path)
    print(f"Rapport généré : {path}")
