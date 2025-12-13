#!/usr/bin/env python3
"""
Tests pour le service de suppression d'arrière-plan
"""

from background_removal import BackgroundRemovalService

def test_background_removal_service():
    """Test basique du service de suppression d'arrière-plan"""
    service = BackgroundRemovalService()

    # Créer une image de test simple (carré rouge sur fond blanc)
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='white')
    # Ajouter un carré rouge au centre
    for x in range(40, 60):
        for y in range(40, 60):
            img.putpixel((x, y), (255, 0, 0))

    # Convertir en bytes
    import io
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()

    # Traiter l'image
    result_bytes, metadata = service.remove_background(image_bytes)

    # Vérifications
    assert isinstance(result_bytes, bytes)
    assert len(result_bytes) > 0
    assert 'original_size' in metadata
    assert 'processed_size' in metadata
    assert metadata['original_size'] == (100, 100)
    assert metadata['has_transparency'] == True
    assert 'method' in metadata

    # Vérifier que l'image traitée peut être chargée
    processed_img = Image.open(io.BytesIO(result_bytes))
    assert processed_img.mode == 'RGBA'

    print(f"✅ Test réussi - Méthode utilisée: {metadata['method']}")

if __name__ == "__main__":
    test_background_removal_service()
    print("✅ Tests du service de suppression d'arrière-plan réussis")