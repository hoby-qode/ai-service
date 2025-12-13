"""
Script de test pour vérifier l'analyse d'image
"""
from utils import analyze_image, CLOTHING_TYPES, STYLES, COLORS
from PIL import Image
import io
import json

def create_test_image():
    """Crée une image de test simple"""
    img = Image.new('RGB', (224, 224), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()

def test_analyze():
    """Test de la fonction analyze_image"""
    print("🧪 Test du service AI - Analyse de vêtements\n")
    print("=" * 60)
    
    # Créer une image de test
    test_image = create_test_image()
    
    # Analyser
    result = analyze_image(test_image)
    
    # Afficher les résultats
    print("\n📊 Résultat de l'analyse :\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Vérifications
    print("\n" + "=" * 60)
    print("\n✅ Vérifications :")
    
    # Vérifier le type
    assert result['type'] in CLOTHING_TYPES, f"Type invalide : {result['type']}"
    print(f"   ✓ Type valide : {result['type']}")
    
    # Vérifier les styles
    for style in result['styles']:
        assert style in STYLES, f"Style invalide : {style}"
    print(f"   ✓ Styles valides : {', '.join(result['styles'])}")
    
    # Vérifier la couleur
    assert result['color'] in COLORS, f"Couleur invalide : {result['color']}"
    print(f"   ✓ Couleur valide : {result['color']}")
    
    # Vérifier l'embedding
    assert len(result['embedding']) == 128, f"Embedding doit avoir 128 dimensions"
    print(f"   ✓ Embedding : {len(result['embedding'])} dimensions")
    
    # Vérifier la confiance
    assert 0 <= result['confidence'] <= 1, "Confidence doit être entre 0 et 1"
    print(f"   ✓ Confiance : {result['confidence']:.2%}")
    
    print("\n" + "=" * 60)
    print("\n🎉 Tous les tests passent avec succès !")
    print("\n📝 Informations de compatibilité Strapi :")
    print(f"   • Type de vêtement (enum) : {result['type']}")
    print(f"   • Styles compatibles : {len(result['styles'])} style(s)")
    print(f"   • Prêt pour intégration avec backend Strapi")

if __name__ == "__main__":
    test_analyze()
