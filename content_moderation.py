"""
Module de modération de contenu pour détecter les images inappropriées
Détecte : nudité, contenu sexuel, violence, contenu gore
"""
from PIL import Image
import io
from config import CONTENT_MODERATION_CONFIG

class ContentModerationError(Exception):
    """Exception levée quand du contenu inapproprié est détecté"""
    def __init__(self, message, reason, confidence=None):
        self.message = message
        self.reason = reason
        self.confidence = confidence
        super().__init__(self.message)

def analyze_skin_percentage(image):
    """
    Analyse simple du pourcentage de peau visible dans l'image
    Utilise une détection de couleur de peau basique (heuristique)
    """
    import numpy as np
    
    # Convertir en numpy array
    img_array = np.array(image)
    
    # Détection basique de couleur de peau (gamme RGB)
    # Cette méthode est simple mais efficace pour un MVP
    r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
    
    # Conditions pour détecter la peau (heuristique simple)
    skin_mask = (
        (r > 95) & (g > 40) & (b > 20) &
        (r > g) & (r > b) &
        (abs(r - g) > 15) &
        (r - g > 15)
    )
    
    skin_percentage = np.sum(skin_mask) / skin_mask.size
    return skin_percentage

def check_image_brightness(image):
    """
    Vérifie si l'image est trop sombre ou trop claire (peut indiquer un contenu suspect)
    """
    import numpy as np
    from PIL import ImageStat
    
    stat = ImageStat.Stat(image)
    mean_brightness = sum(stat.mean) / len(stat.mean)
    
    return mean_brightness

def detect_inappropriate_content(image_bytes):
    """
    Détecte si l'image contient du contenu inapproprié
    
    Args:
        image_bytes: Bytes de l'image à analyser
        
    Returns:
        dict: {
            "is_safe": bool,
            "reasons": list[str],
            "skin_percentage": float,
            "confidence": float
        }
        
    Raises:
        ContentModerationError: Si du contenu inapproprié est détecté
    """
    if not CONTENT_MODERATION_CONFIG["enabled"]:
        return {
            "is_safe": True,
            "reasons": [],
            "skin_percentage": 0.0,
            "confidence": 0.0,
            "moderation_disabled": True
        }
    
    # Charger l'image
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # Analyser le pourcentage de peau
    skin_percentage = analyze_skin_percentage(image)
    
    # Vérifier la luminosité
    brightness = check_image_brightness(image)
    
    reasons = []
    is_safe = True
    
    # Règles de modération
    nsfw_threshold = CONTENT_MODERATION_CONFIG["nsfw_threshold"]
    
    # 1. Vérifier le pourcentage de peau excessive (possible nudité)
    if skin_percentage > nsfw_threshold:
        reasons.append("nudité détectée")
        is_safe = False
    
    # 2. Vérifier si l'image est principalement constituée de peau
    elif skin_percentage > (nsfw_threshold - 0.2) and brightness > 150:
        reasons.append("contenu suspect - forte présence de peau")
        is_safe = False
    
    # 3. Vérifier dimensions et ratio (images de type "selfie" en sous-vêtements)
    width, height = image.size
    if skin_percentage > (nsfw_threshold - 0.1) and (width / height) < 0.7:
        reasons.append("format et contenu suspects")
        is_safe = False
    
    result = {
        "is_safe": is_safe,
        "reasons": reasons,
        "skin_percentage": float(skin_percentage),
        "brightness": float(brightness),
        "confidence": float(skin_percentage) if not is_safe else 0.0
    }
    
    # Lever une exception si contenu inapproprié détecté
    if not is_safe and CONTENT_MODERATION_CONFIG["block_nsfw"]:
        raise ContentModerationError(
            message="Image refusée : contenu inapproprié détecté",
            reason=", ".join(reasons),
            confidence=result["confidence"]
        )
    
    return result

def validate_image_for_clothing(image_bytes):
    """
    Valide qu'une image est appropriée pour l'analyse de vêtements
    
    Args:
        image_bytes: Bytes de l'image
        
    Returns:
        dict: Résultat de la modération
        
    Raises:
        ContentModerationError: Si contenu inapproprié
        ValueError: Si image invalide
    """
    try:
        # Vérifier que c'est une image valide
        image = Image.open(io.BytesIO(image_bytes))
        
        # Vérifier les dimensions minimales
        width, height = image.size
        if width < 50 or height < 50:
            raise ValueError("Image trop petite. Minimum 50x50 pixels requis.")
        
        # Vérifier la taille du fichier (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise ValueError("Image trop volumineuse. Maximum 10MB.")
        
        # Analyser le contenu
        moderation_result = detect_inappropriate_content(image_bytes)
        
        return moderation_result
        
    except ContentModerationError:
        raise
    except Exception as e:
        raise ValueError(f"Image invalide : {str(e)}")
