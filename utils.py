from PIL import Image
import io
import torch
from torchvision import transforms, models
import random
from config import (
    CLOTHING_TYPES,
    STYLES,
    COLORS,
    SIZES,
    MATERIALS,
    PATTERNS,
    MODEL_CONFIG
)
from content_moderation import validate_image_for_clothing, ContentModerationError

# Modèle léger pré-entraîné MobileNet pour MVP
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
model.eval()  # mode évaluation

# Transformation image
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def analyze_image(image_bytes):
    """
    Analyse une image de vêtement et retourne les infos de base + embedding
    Utilise les vraies données du projet Serahly (Strapi schema)
    
    Raises:
        ContentModerationError: Si du contenu inapproprié est détecté
        ValueError: Si l'image est invalide
    """
    # 1. VALIDATION ET MODÉRATION DU CONTENU
    # Cette étape bloque les images inappropriées avant l'analyse
    moderation_result = validate_image_for_clothing(image_bytes)
    
    # 2. ANALYSE DE L'IMAGE
    # Chargement image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_tensor = transform(image).unsqueeze(0)  # ajout batch dimension

    # Prédiction avec le modèle
    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs, 1)
    
    # Sélection aléatoire basée sur la prédiction (pour MVP)
    random.seed(predicted.item())
    
    # Type de vêtement (mapping vers enum Strapi)
    clothing_type = CLOTHING_TYPES[predicted.item() % len(CLOTHING_TYPES)]
    
    # Sélection de styles compatibles (configurable)
    num_styles = random.randint(
        MODEL_CONFIG["min_styles"],
        MODEL_CONFIG["max_styles"]
    )
    selected_styles = random.sample(STYLES, num_styles)
    
    # Couleur aléatoire
    color = random.choice(COLORS)
    
    # Taille basée sur le type
    size = random.choice(SIZES.get(clothing_type, ["M"]))
    
    # Matière et motif
    material = random.choice(MATERIALS)
    pattern = random.choice(PATTERNS)
    
    # Génération d'un nom descriptif
    name = f"{material} {color}"

    # Embedding (vecteur de features pour similarité)
    embedding_size = MODEL_CONFIG["embedding_dimensions"]
    embedding = outputs.squeeze(0).tolist()[:embedding_size]
    
    # Score de confiance
    confidence = float(torch.softmax(outputs, 1).max().item())

    # 3. RETOUR FORMAT COMPATIBLE STRAPI
    # Retour format compatible avec Strapi clothing-item
    return {
        "name": name,
        "type": clothing_type,  # enum: haut, bas, chaussure, accessoire, autre
        "color": color,
        "size": size,
        "material": material,
        "pattern": pattern,
        "styles": selected_styles,  # Liste de styles compatibles
        "embedding": embedding,  # Vecteur pour recherche de similarité
        "brand": None,  # À remplir par l'utilisateur
        "confidence": confidence,  # Score de confiance
        "moderation": {  # Résultat de la modération
            "is_safe": moderation_result["is_safe"],
            "checked": True
        }
    }
