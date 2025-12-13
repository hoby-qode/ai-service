from PIL import Image
import io
import numpy as np
from typing import Tuple

class BackgroundRemovalService:
    """Service pour supprimer l'arrière-plan des images de vêtements"""

    def __init__(self):
        """Initialise le service de suppression d'arrière-plan"""
        self.rembg_available = False
        try:
            from rembg import remove
            self.remove_func = remove
            self.rembg_available = True
        except ImportError:
            print("⚠️ rembg n'est pas disponible. Utilisation d'un fallback simple.")
            self.remove_func = None

    def remove_background(self, image_bytes: bytes) -> Tuple[bytes, dict]:
        """
        Supprime l'arrière-plan d'une image

        Args:
            image_bytes: Bytes de l'image d'entrée

        Returns:
            Tuple[bytes, dict]: (image_sans_arriere_plan_bytes, metadata)

        Raises:
            ValueError: Si l'image est invalide
        """
        try:
            # Charger l'image
            input_image = Image.open(io.BytesIO(image_bytes))

            # Vérifier le format
            if input_image.format not in ['JPEG', 'PNG', 'WEBP']:
                raise ValueError(f"Format d'image non supporté: {input_image.format}")

            # Convertir en RGBA si nécessaire
            if input_image.mode != 'RGBA':
                input_image = input_image.convert('RGBA')

            if self.rembg_available and self.remove_func:
                # Utiliser rembg si disponible
                output_image = self.remove_func(input_image)
            else:
                # Fallback simple : créer une image avec fond transparent simulé
                # Pour le MVP, on retourne simplement l'image originale avec un canal alpha
                output_image = input_image

                # Simulation simple : rendre les pixels blancs transparents
                # (très basique, juste pour le développement)
                data = np.array(output_image)
                # Rendre les pixels très clairs transparents
                mask = (data[:, :, 0] > 240) & (data[:, :, 1] > 240) & (data[:, :, 2] > 240)
                data[mask, 3] = 0  # Alpha = 0 pour les pixels blancs
                output_image = Image.fromarray(data, 'RGBA')

            # Convertir en bytes
            output_buffer = io.BytesIO()
            output_image.save(output_buffer, format='PNG')
            output_bytes = output_buffer.getvalue()

            # Métadonnées
            metadata = {
                'original_size': input_image.size,
                'original_mode': input_image.mode,
                'processed_size': output_image.size,
                'processed_mode': output_image.mode,
                'has_transparency': output_image.mode == 'RGBA',
                'method': 'rembg' if self.rembg_available else 'fallback'
            }

            return output_bytes, metadata

        except Exception as e:
            raise ValueError(f"Erreur lors de la suppression d'arrière-plan: {str(e)}")

    def remove_background_from_file(self, image_path: str, output_path: str = None) -> dict:
        """
        Supprime l'arrière-plan d'un fichier image

        Args:
            image_path: Chemin vers l'image d'entrée
            output_path: Chemin de sortie (optionnel)

        Returns:
            dict: Métadonnées du traitement
        """
        try:
            # Charger l'image
            input_image = Image.open(image_path)

            if self.rembg_available and self.remove_func:
                # Utiliser rembg si disponible
                output_image = self.remove_func(input_image)
                method = 'rembg'
            else:
                # Fallback simple
                output_image = input_image.convert('RGBA')
                method = 'fallback'

            # Sauvegarder si output_path fourni
            if output_path:
                output_image.save(output_path, format='PNG')

            # Métadonnées
            metadata = {
                'input_path': image_path,
                'output_path': output_path,
                'original_size': input_image.size,
                'processed_size': output_image.size,
                'method': method,
                'success': True
            }

            return metadata

        except Exception as e:
            return {
                'input_path': image_path,
                'output_path': output_path,
                'error': str(e),
                'method': 'failed',
                'success': False
            }

# Instance globale du service
background_removal_service = BackgroundRemovalService()