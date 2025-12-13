from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from utils import analyze_image
from content_moderation import ContentModerationError
from background_removal import background_removal_service
from config import CLOTHING_TYPES, STYLES, COLORS, MODEL_CONFIG, CONTENT_MODERATION_CONFIG
import io

app = FastAPI(
    title="AI Clothing Service - Serahly",
    description="Service d'analyse d'images de vêtements pour le projet Serahly",
    version="1.0.0"
)

# Autoriser toutes les origines pour le MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "message": "AI Clothing Service is running",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /analyze",
            "remove-background": "POST /remove-background",
            "health": "GET /health",
            "config": "GET /config"
        }
    }

@app.get("/health")
def health_check():
    """Vérification de l'état du service"""
    return {
        "status": "healthy",
        "service": "ai-clothing-service",
        "model": "MobileNetV2",
        "features": ["analysis", "background_removal", "content_moderation"]
    }

@app.get("/config")
def get_config():
    """Retourne la configuration du service"""
    return {
        "clothing_types": CLOTHING_TYPES,
        "styles": STYLES,
        "colors": COLORS,
        "model_config": MODEL_CONFIG,
        "content_moderation": {
            "enabled": CONTENT_MODERATION_CONFIG["enabled"],
            "nsfw_threshold": CONTENT_MODERATION_CONFIG["nsfw_threshold"]
        }
    }

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Analyse une image de vêtement et retourne les métadonnées
    
    MODÉRATION DE CONTENU : Les images contenant de la nudité ou du contenu 
    inapproprié seront automatiquement rejetées avec un code d'erreur 451.
    
    Returns:
        - name: Nom descriptif généré
        - type: Type de vêtement (haut, bas, chaussure, accessoire, autre)
        - color: Couleur détectée
        - size: Taille appropriée au type
        - material: Matière estimée
        - pattern: Motif détecté
        - styles: Liste de 1 à 3 styles compatibles
        - embedding: Vecteur de 128 dimensions pour recherche de similarité
        - brand: null (à remplir par l'utilisateur)
        - confidence: Score de confiance (0-1)
        - moderation: Résultat de la modération de contenu
        
    Raises:
        400: Fichier invalide ou trop volumineux
        451: Contenu inapproprié détecté (nudité, violence, etc.)
        500: Erreur serveur lors de l'analyse
    """
    try:
        # Vérifier le type de fichier
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Le fichier doit être une image (JPEG, PNG, etc.)"
            )
        
        # Lire et analyser l'image
        image_bytes = await file.read()
        result = analyze_image(image_bytes)
        
        return result
    
    except ContentModerationError as e:
        # Erreur 451 : Unavailable For Legal Reasons (bloqué pour des raisons légales)
        # Utilisé pour indiquer un contenu interdit
        raise HTTPException(
            status_code=451,
            detail={
                "error": "content_blocked",
                "message": e.message,
                "reason": e.reason,
                "confidence": e.confidence,
                "help": "Veuillez uploader une image de vêtement appropriée. Les images contenant de la nudité ou du contenu inapproprié ne sont pas acceptées."
            }
        )
    
    except ValueError as e:
        # Erreur 400 : Image invalide
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_image",
                "message": str(e)
            }
        )
    
    except Exception as e:
        # Erreur 500 : Erreur serveur
        raise HTTPException(
            status_code=500,
            detail={
                "error": "analysis_failed",
                "message": f"Erreur lors de l'analyse: {str(e)}"
            }
        )

@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    """
    Supprime l'arrière-plan d'une image de vêtement

    Utilise rembg (basé sur U²-Net) pour une suppression d'arrière-plan de haute qualité.
    L'image de sortie sera au format PNG avec transparence.

    Returns:
        Image PNG avec arrière-plan supprimé

    Raises:
        400: Fichier invalide ou trop volumineux
        500: Erreur lors du traitement
    """
    try:
        # Vérifier le type de fichier
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Le fichier doit être une image (JPEG, PNG, etc.)"
            )

        # Vérifier la taille du fichier (max 10MB)
        file_size = 0
        content = b""
        chunk_size = 1024 * 1024  # 1MB chunks

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            content += chunk
            file_size += len(chunk)

            if file_size > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(
                    status_code=400,
                    detail="Le fichier est trop volumineux (max 10MB)"
                )

        # Traiter l'image
        processed_image_bytes, metadata = background_removal_service.remove_background(content)

        # Retourner l'image traitée
        return StreamingResponse(
            io.BytesIO(processed_image_bytes),
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=processed_{file.filename}",
                "X-Original-Size": f"{metadata['original_size'][0]}x{metadata['original_size'][1]}",
                "X-Processed-Size": f"{metadata['processed_size'][0]}x{metadata['processed_size'][1]}",
                "X-Has-Transparency": str(metadata['has_transparency']).lower()
            }
        )

    except ValueError as e:
        # Erreur 400 : Image invalide
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_image",
                "message": str(e)
            }
        )

    except Exception as e:
        # Erreur 500 : Erreur serveur
        raise HTTPException(
            status_code=500,
            detail={
                "error": "background_removal_failed",
                "message": f"Erreur lors de la suppression d'arrière-plan: {str(e)}"
            }
        )

# Servir les fichiers statiques après les routes API
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
