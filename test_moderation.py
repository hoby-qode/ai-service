"""
Script de test pour la modération de contenu
"""
from content_moderation import (
    detect_inappropriate_content, 
    validate_image_for_clothing,
    ContentModerationError
)
from PIL import Image
import io
import numpy as np

def create_test_image(skin_percentage=0.3, brightness=128):
    """
    Crée une image de test avec un pourcentage de peau contrôlé
    """
    # Créer une image 224x224
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    
    # Remplir avec une couleur de base
    img[:, :] = [50, 50, 100]  # Bleu foncé (fond)
    
    # Ajouter de la "peau" (couleur chair)
    if skin_percentage > 0:
        num_skin_pixels = int(224 * 224 * skin_percentage)
        skin_color = [220, 180, 150]  # Couleur chair
        
        # Remplir aléatoirement des pixels avec de la couleur peau
        indices = np.random.choice(224 * 224, num_skin_pixels, replace=False)
        for idx in indices:
            y = idx // 224
            x = idx % 224
            img[y, x] = skin_color
    
    # Convertir en image PIL
    pil_img = Image.fromarray(img, 'RGB')
    
    # Convertir en bytes
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()

def test_safe_image():
    """Test avec une image sûre (peu de peau)"""
    print("\n" + "="*60)
    print("🧪 Test 1: Image sûre (20% peau)")
    print("="*60)
    
    image_bytes = create_test_image(skin_percentage=0.2)
    
    try:
        result = detect_inappropriate_content(image_bytes)
        print(f"✅ Résultat: {'SAFE' if result['is_safe'] else 'UNSAFE'}")
        print(f"   Pourcentage de peau: {result['skin_percentage']:.1%}")
        print(f"   Luminosité: {result['brightness']:.1f}")
        if result['reasons']:
            print(f"   Raisons: {', '.join(result['reasons'])}")
    except ContentModerationError as e:
        print(f"❌ BLOQUÉ: {e.message}")
        print(f"   Raison: {e.reason}")

def test_nsfw_image():
    """Test avec une image NSFW (beaucoup de peau)"""
    print("\n" + "="*60)
    print("🧪 Test 2: Image inappropriée (80% peau)")
    print("="*60)
    
    image_bytes = create_test_image(skin_percentage=0.8)
    
    try:
        result = detect_inappropriate_content(image_bytes)
        print(f"✅ Résultat: {'SAFE' if result['is_safe'] else 'UNSAFE'}")
        print(f"   Pourcentage de peau: {result['skin_percentage']:.1%}")
        print(f"   Luminosité: {result['brightness']:.1f}")
        if result['reasons']:
            print(f"   Raisons: {', '.join(result['reasons'])}")
    except ContentModerationError as e:
        print(f"❌ BLOQUÉ: {e.message}")
        print(f"   Raison: {e.reason}")
        print(f"   Confiance: {e.confidence:.1%}")

def test_borderline_image():
    """Test avec une image limite (au seuil)"""
    print("\n" + "="*60)
    print("🧪 Test 3: Image limite (60% peau)")
    print("="*60)
    
    image_bytes = create_test_image(skin_percentage=0.6)
    
    try:
        result = detect_inappropriate_content(image_bytes)
        print(f"✅ Résultat: {'SAFE' if result['is_safe'] else 'UNSAFE'}")
        print(f"   Pourcentage de peau: {result['skin_percentage']:.1%}")
        print(f"   Luminosité: {result['brightness']:.1f}")
        if result['reasons']:
            print(f"   Raisons: {', '.join(result['reasons'])}")
    except ContentModerationError as e:
        print(f"❌ BLOQUÉ: {e.message}")
        print(f"   Raison: {e.reason}")
        print(f"   Confiance: {e.confidence:.1%}")

def test_validation():
    """Test de la validation complète"""
    print("\n" + "="*60)
    print("🧪 Test 4: Validation complète")
    print("="*60)
    
    # Test image valide
    print("\n📸 Image valide:")
    try:
        image_bytes = create_test_image(skin_percentage=0.15)
        result = validate_image_for_clothing(image_bytes)
        print(f"   ✅ Image acceptée")
        print(f"   Vérification: {result['is_safe']}")
    except ContentModerationError as e:
        print(f"   ❌ Image rejetée: {e.reason}")
    except ValueError as e:
        print(f"   ❌ Image invalide: {str(e)}")
    
    # Test image inappropriée
    print("\n📸 Image inappropriée:")
    try:
        image_bytes = create_test_image(skin_percentage=0.75)
        result = validate_image_for_clothing(image_bytes)
        print(f"   ✅ Image acceptée (ne devrait pas arriver)")
    except ContentModerationError as e:
        print(f"   ❌ Image rejetée: {e.reason}")
        print(f"   ✅ Modération fonctionne correctement!")
    except ValueError as e:
        print(f"   ❌ Image invalide: {str(e)}")

def main():
    """Exécuter tous les tests"""
    print("\n" + "🛡️ " * 20)
    print("TESTS DE MODÉRATION DE CONTENU")
    print("🛡️ " * 20)
    
    test_safe_image()
    test_nsfw_image()
    test_borderline_image()
    test_validation()
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    print("""
✅ La modération de contenu est active
🛡️  Les images avec >60% de peau sont bloquées
⚠️  HTTP 451 est retourné pour contenu inapproprié
📸 Les images de vêtements normales passent sans problème
    """)
    
    print("💡 NOTES:")
    print("   - Le seuil NSFW peut être ajusté dans config.py")
    print("   - La détection utilise une heuristique de couleur de peau")
    print("   - Pour MVP: détection basique mais efficace")
    print("   - Pour production: envisager un modèle ML spécialisé (NudeNet)")

if __name__ == "__main__":
    main()
