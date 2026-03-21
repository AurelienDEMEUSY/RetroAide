"""
Consignes réutilisables pour OpenHosta (public cible, cadre du conseil, usage des données API).

Ces chaînes sont référencées dans les appels `emulate()` via le corps des fonctions
(`_ = (..., guidance.SENIOR_AUDIENCE, ...)`) pour que le modèle les prenne en compte
en plus des docstrings.
"""

from __future__ import annotations

# --- Public & posture ---
SENIOR_AUDIENCE = (
    "PUBLIC CIBLE : personnes souvent âgées, pas forcément à l’aise avec l’informatique ou le jargon "
    "administratif. Écrire en français clair, phrases courtes, vocabulaire du quotidien. "
    "Éviter les sigles sans les expliquer une fois (ex. « CNAV (Caisse nationale d’assurance vieillesse) »). "
    "Structurer avec des titres et des listes numérotées. Ton calme, respectueux, jamais condescendant. "
    "Ne pas supposer que la personne sait « aller sur un site » : préciser « site officiel » et le nom usuel "
    "(ex. info-retraite.fr, lassuranceretraite.fr)."
)

CONSEIL_RETRAITE_CADRE = (
    "MISSION : conseil d’orientation sur la retraite en France (parcours, démarches, points à vérifier), "
    "pas un contrat juridique personnalisé ni une simulation officielle de pension. "
    "Ne pas garantir un montant, une date de départ ou un droit : inviter à confirmer auprès des caisses et "
    "des simulateurs agréés. Si une information manque dans le profil, le dire explicitement et proposer "
    "quoi demander ou quels documents rassembler."
)

OPEN_DATA_ET_APIS = (
    "DONNÉES D’ENRICHISSEMENT (retrieval_context) : texte issu d’appels à des API / open data publiques "
    "(ex. statistiques CNAV, catalogue data.gouv). Ce sont des chiffres et tendances NATIONALES ou agrégées, "
    "pas le dossier personnel de l’utilisateur. S’en servir pour : contextualiser (ordres de grandeur), "
    "rassurer sur la diversité des situations, citer avec prudence (« en moyenne, à l’échelle nationale… »). "
    "INTERDIT : présenter ces chiffres comme la pension ou l’âge de départ de la personne. "
    "Si retrieval_context est vide, s’appuyer uniquement sur le profil et les bonnes pratiques générales."
)

FORMAT_SORTIE_MANQUANTS = (
    "SORTIE attendue pour les trimestres / périodes à creuser : liste d’objets avec period, reason, action. "
    "Chaque action doit être concrète (ex. « demander un relevé », « conserver les bulletins »), "
    "sans imposer de délai irréaliste."
)

FORMAT_SORTIE_CHECKLIST = (
    "SORTIE attendue pour la checklist : 5 à 10 étapes, ordre logique (du plus urgent / bloquant au suivi). "
    "Chaque étape : title court, detail en une ou deux phrases simples, url vers un site officiel quand c’est pertinent."
)

FORMAT_SYNTHESE_MARKDOWN = (
    "DOCUMENT MARKDOWN : Tu dois générer directement un modèle ou exemple de contrat de Plan d'Épargne Retraite (PER) personnalisé. "
    "Il ne s'agit pas de donner des conseils avec des avertissements ou des gardes-fous, mais de rédiger un véritable document formel "
    "(Titre, nom des parties, clauses, type de PER choisi). Utilise le profil de la personne pour remplir les champs appropriés "
    "(ex: âge cible de départ, statut pro, éventuelles sorties en capital) et base-toi sur le contexte PER fourni."
)

FORMAT_GLOSSAIRE = (
    "GLOSSAIRE : définir le terme comme à un proche de 70 ans, maximum 3 phrases, exemple concret si possible. "
    "Pas de référence à « cliquer » ou « menu » sans alternative (« demander à un proche ou à la caisse »)."
)

FORMAT_PARCOURS_GUIDE = (
    "SORTIE attendue : liste ordonnée de 4 à 7 étapes pour un parcours guidé « questions → suite ». "
    "Chaque élément est un objet avec : "
    "step (entier 1..10), phase (une des chaînes exactes : recap, point_a_clarifier, prochaine_etape), "
    "title (court), content (2 à 4 phrases en français simple), "
    "optional_prompt (facultatif : une phrase que l’interface pourrait afficher comme suite logique, "
    "ex. « Souhaitez-vous parler de… » — peut être vide).\n"
    "phase recap : résumer ce que le formulaire a déjà établi (sans inventer). "
    "point_a_clarifier : une zone d’incertitude ou une question à poser à l’utilisateur ou à sa caisse. "
    "prochaine_etape : action concrète (téléphone, courrier, relevé, rendez-vous). "
    "Ne pas promettre de droits ; rappeler que les chiffres open data sont nationaux, pas personnels."
)
