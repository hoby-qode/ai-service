"""
Configuration centralisée basée sur les données Strapi du projet Serahly
Synchronisé avec :
- backend/src/api/clothing-item/content-types/clothing-item/schema.json
- backend/scripts/seed-wardrobe.js
"""

# Types de vêtements (enum du schema Strapi clothing-item)
# Source: backend/src/api/clothing-item/content-types/clothing-item/schema.json
CLOTHING_TYPES = [
    "haut",
    "bas",
    "chaussure",
    "accessoire",
    "autre"
]

# Styles disponibles dans Strapi
# Source: backend/scripts/seed-wardrobe.js (stylesData)
STYLES = [
    "Casual",
    "Chic", 
    "Streetwear",
    "Sportif",
    "Vintage",
    "Bohème",
    "Minimaliste",
    "Rock"
]

# Couleurs fréquentes (basées sur les exemples de seed)
# Source: backend/scripts/seed-wardrobe.js (clothingItemsData)
COLORS = [
    "noir",
    "blanc",
    "gris",
    "beige",
    "bleu",
    "marron",
    "kaki",
    "rouge",
    "vert",
    "jaune",
    "rose",
    "multicolore",
    "camel",
    "doré"
]

# Tailles par type de vêtement
SIZES = {
    "haut": ["XS", "S", "M", "L", "XL", "XXL"],
    "bas": ["34", "36", "38", "40", "42", "44", "46"],
    "chaussure": ["35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45"],
    "accessoire": ["unique"],
    "autre": ["unique", "S", "M", "L"]
}

# Matières courantes
MATERIALS = [
    "Coton",
    "Lin",
    "Polyester",
    "Laine",
    "Cuir",
    "Denim",
    "Soie",
    "Synthétique",
    "Velours",
    "Satin",
    "Jean",
    "Jersey"
]

# Motifs
PATTERNS = [
    "Uni",
    "Rayé",
    "À carreaux",
    "Fleuri",
    "Graphique",
    "Imprimé",
    "Pois",
    "Animal",
    "Géométrique"
]

# Marques populaires (optionnel, pour future utilisation)
BRANDS = [
    "Zara",
    "H&M",
    "Mango",
    "Uniqlo",
    "Nike",
    "Adidas",
    "Levi's",
    "Supreme",
    "Stussy",
    "Vintage",
    "Autre"
]

# Configuration du modèle
MODEL_CONFIG = {
    "embedding_dimensions": 128,  # Dimensions du vecteur d'embedding
    "min_confidence": 0.0,  # Confiance minimale pour accepter une prédiction
    "min_styles": 1,  # Nombre minimum de styles à retourner
    "max_styles": 3,  # Nombre maximum de styles à retourner
}

# Configuration de la modération de contenu
CONTENT_MODERATION_CONFIG = {
    "enabled": True,  # Activer/désactiver la modération
    "nsfw_threshold": 0.6,  # Seuil de détection NSFW (0-1)
    "block_nsfw": True,  # Bloquer les images NSFW
    "block_violence": True,  # Bloquer les images violentes
}
