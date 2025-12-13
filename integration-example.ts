/**
 * Service d'analyse d'images de vêtements avec modération de contenu
 * Intégration avec l'AI Service pour le projet Serahly
 */

import { Alert } from "react-native";

// Configuration de l'API
const AI_SERVICE_URL = "http://localhost:8000"; // À remplacer par l'URL de production

// Types TypeScript
interface AnalysisResult {
  name: string;
  type: "haut" | "bas" | "chaussure" | "accessoire" | "autre";
  color: string;
  size: string;
  material: string;
  pattern: string;
  styles: string[];
  embedding: number[];
  brand: null | string;
  confidence: number;
  moderation: {
    is_safe: boolean;
    checked: boolean;
  };
}

interface ContentBlockedError {
  error: "content_blocked";
  message: string;
  reason: string;
  confidence: number;
  help: string;
}

interface InvalidImageError {
  error: "invalid_image";
  message: string;
}

// Service de l'AI
class AIClothingService {
  /**
   * Analyse une image de vêtement
   * @param imageUri URI de l'image (local ou distant)
   * @returns Résultat de l'analyse ou null si erreur
   */
  static async analyzeClothingImage(
    imageUri: string
  ): Promise<AnalysisResult | null> {
    try {
      // Créer le FormData
      const formData = new FormData();
      formData.append("file", {
        uri: imageUri,
        type: "image/jpeg",
        name: "clothing.jpg",
      } as any);

      // Envoyer la requête
      const response = await fetch(`${AI_SERVICE_URL}/analyze`, {
        method: "POST",
        body: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      // Gérer les différents codes d'erreur
      if (response.status === 451) {
        // Contenu inapproprié détecté
        const error: ContentBlockedError = await response.json();
        this.handleContentBlocked(error);
        return null;
      }

      if (response.status === 400) {
        // Image invalide
        const error: InvalidImageError = await response.json();
        this.handleInvalidImage(error);
        return null;
      }

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
      }

      // Succès
      const result: AnalysisResult = await response.json();
      return result;
    } catch (error) {
      console.error("Erreur lors de l'analyse:", error);
      Alert.alert(
        "Erreur",
        "Impossible d'analyser l'image. Veuillez réessayer.",
        [{ text: "OK" }]
      );
      return null;
    }
  }

  /**
   * Gère le cas d'un contenu bloqué (erreur 451)
   */
  private static handleContentBlocked(error: ContentBlockedError) {
    Alert.alert(
      "🛡️ Image inappropriée",
      "Cette image ne peut pas être analysée car elle contient du contenu inapproprié.\n\n" +
        `Raison: ${error.reason}\n\n` +
        "Veuillez choisir une photo de vêtement appropriée.",
      [
        {
          text: "Choisir une autre image",
          style: "default",
        },
      ]
    );
  }

  /**
   * Gère le cas d'une image invalide (erreur 400)
   */
  private static handleInvalidImage(error: InvalidImageError) {
    Alert.alert(
      "Image invalide",
      error.message || "L'image sélectionnée n'est pas valide.",
      [{ text: "OK" }]
    );
  }

  /**
   * Vérifie la santé du service
   */
  static async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${AI_SERVICE_URL}/health`);
      const data = await response.json();
      return data.status === "healthy";
    } catch (error) {
      console.error("Service AI inaccessible:", error);
      return false;
    }
  }

  /**
   * Récupère la configuration du service
   */
  static async getConfig() {
    try {
      const response = await fetch(`${AI_SERVICE_URL}/config`);
      return await response.json();
    } catch (error) {
      console.error("Erreur lors de la récupération de la config:", error);
      return null;
    }
  }
}

export default AIClothingService;

// ============================================
// EXEMPLE D'UTILISATION
// ============================================

/**
 * Exemple 1: Analyser une image depuis la caméra
 */
export const exampleAnalyzeFromCamera = async () => {
  // Supposons que vous avez déjà pris une photo
  const imageUri = "file:///path/to/photo.jpg";

  // Analyser l'image
  const result = await AIClothingService.analyzeClothingImage(imageUri);

  if (result) {
    console.log("✅ Analyse réussie!");
    console.log("Type:", result.type);
    console.log("Couleur:", result.color);
    console.log("Styles:", result.styles.join(", "));

    // Utiliser les données pour créer un clothing-item dans Strapi
    // ... (voir exemple ci-dessous)
  } else {
    console.log("❌ Analyse échouée ou contenu bloqué");
  }
};

/**
 * Exemple 2: Intégration complète avec Strapi
 */
export const exampleFullIntegration = async (
  imageUri: string,
  userId: number
) => {
  // 1. Analyser l'image avec l'AI
  const aiResult = await AIClothingService.analyzeClothingImage(imageUri);

  if (!aiResult) {
    return null; // Erreur déjà gérée par le service
  }

  // 2. Uploader l'image vers Strapi
  const uploadedImage = await uploadImageToStrapi(imageUri);

  // 3. Récupérer les IDs des styles depuis Strapi
  const styleIds = await getStyleIdsByNames(aiResult.styles);

  // 4. Créer le clothing-item dans Strapi
  const clothingItem = await createClothingItemInStrapi({
    name: aiResult.name,
    type: aiResult.type,
    color: aiResult.color,
    size: aiResult.size,
    brand: aiResult.brand,
    image: uploadedImage.id,
    style: styleIds,
    owner: userId,
    for_sale: false,
  });

  return clothingItem;
};

/**
 * Helper: Upload d'image vers Strapi
 */
async function uploadImageToStrapi(imageUri: string) {
  const formData = new FormData();
  formData.append("files", {
    uri: imageUri,
    type: "image/jpeg",
    name: "clothing.jpg",
  } as any);

  const response = await fetch("http://192.168.0.190:3002/upload", {
    method: "POST",
    body: formData,
    headers: {
      Authorization: `Bearer YOUR_TOKEN`,
    },
  });

  const data = await response.json();
  return data[0]; // Retourne le premier fichier uploadé
}

/**
 * Helper: Récupérer les IDs des styles par leurs noms
 */
async function getStyleIdsByNames(styleNames: string[]): Promise<number[]> {
  const styleIds: number[] = [];

  for (const styleName of styleNames) {
    const response = await fetch(
      `http://192.168.0.190:3002/api/styles?filters[name][$eq]=${styleName}`,
      {
        headers: {
          Authorization: `Bearer YOUR_TOKEN`,
        },
      }
    );

    const data = await response.json();
    if (data.data.length > 0) {
      styleIds.push(data.data[0].id);
    }
  }

  return styleIds;
}

/**
 * Helper: Créer un clothing-item dans Strapi
 */
async function createClothingItemInStrapi(itemData: any) {
  const response = await fetch("http://192.168.0.190:3002/api/clothing-items", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer YOUR_TOKEN`,
    },
    body: JSON.stringify({ data: itemData }),
  });

  const data = await response.json();
  return data.data;
}

/**
 * Exemple 3: Vérifier la santé du service avant utilisation
 */
export const exampleCheckServiceHealth = async () => {
  const isHealthy = await AIClothingService.checkHealth();

  if (!isHealthy) {
    Alert.alert(
      "Service indisponible",
      "Le service d'analyse d'images est temporairement indisponible. Veuillez réessayer plus tard.",
      [{ text: "OK" }]
    );
    return false;
  }

  return true;
};
