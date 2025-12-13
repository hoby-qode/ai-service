# 🛡️ Modération de Contenu - AI Service

## Vue d'ensemble

Le service AI inclut maintenant un système de **modération de contenu** pour bloquer automatiquement les images inappropriées (nudité, contenu sexuel, etc.).

## ✅ Fonctionnalités

### Protection Automatique

- ✅ Détection de nudité
- ✅ Détection de contenu sexuel
- ✅ Analyse du pourcentage de peau visible
- ✅ Vérification des dimensions et formats suspects
- ✅ Blocage automatique avec code d'erreur HTTP 451

### Configuration

La modération est configurable via `config.py` :

```python
CONTENT_MODERATION_CONFIG = {
    "enabled": True,              # Activer/désactiver
    "nsfw_threshold": 0.6,        # Seuil de détection (0-1)
    "block_nsfw": True,           # Bloquer les images NSFW
    "block_violence": True,       # Bloquer les images violentes
}
```

## 🔍 Comment ça fonctionne

### Algorithme de Détection

1. **Analyse de couleur de peau** (heuristique RGB)
   - Détecte les pixels correspondant à la couleur chair
   - Calcule le pourcentage de peau dans l'image
2. **Vérification de luminosité**
   - Images trop claires ou trop sombres suspectes
3. **Analyse de composition**

   - Ratio largeur/hauteur
   - Concentration de peau

4. **Décision**
   - Si pourcentage de peau > seuil → BLOQUÉ
   - Sinon → ACCEPTÉ

### Seuils par Défaut

| Seuil            | Valeur     | Description              |
| ---------------- | ---------- | ------------------------ |
| `nsfw_threshold` | 0.6 (60%)  | Si >60% de peau → bloqué |
| Borderline       | 0.4-0.5    | Zone d'alerte            |
| Safe             | <0.4 (40%) | Image considérée sûre    |

## 📡 Codes de Réponse HTTP

### ✅ 200 OK - Image Acceptée

```json
{
  "name": "Coton noir",
  "type": "haut",
  "color": "noir",
  ...
  "moderation": {
    "is_safe": true,
    "checked": true
  }
}
```

### ❌ 451 Unavailable For Legal Reasons - Contenu Bloqué

```json
{
  "detail": {
    "error": "content_blocked",
    "message": "Image refusée : contenu inapproprié détecté",
    "reason": "nudité détectée",
    "confidence": 0.78,
    "help": "Veuillez uploader une image de vêtement appropriée..."
  }
}
```

### ❌ 400 Bad Request - Image Invalide

```json
{
  "detail": {
    "error": "invalid_image",
    "message": "Image trop petite. Minimum 50x50 pixels requis."
  }
}
```

## 🧪 Tests

### Tester la Modération

```bash
cd ai-service
python test_moderation.py
```

### Exemple de Test Manuel

```python
from content_moderation import validate_image_for_clothing

# Charger une image
with open('image.jpg', 'rb') as f:
    image_bytes = f.read()

# Valider
try:
    result = validate_image_for_clothing(image_bytes)
    print(f"✅ Image acceptée: {result['is_safe']}")
except ContentModerationError as e:
    print(f"❌ Image bloquée: {e.reason}")
```

## 🔧 Intégration Frontend

### React Native / Expo

```typescript
const uploadClothingImage = async (imageUri: string) => {
  try {
    const formData = new FormData();
    formData.append("file", {
      uri: imageUri,
      type: "image/jpeg",
      name: "clothing.jpg",
    });

    const response = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      body: formData,
    });

    if (response.status === 451) {
      // Contenu inapproprié détecté
      const error = await response.json();
      Alert.alert(
        "Image refusée",
        "Cette image contient du contenu inapproprié. Veuillez uploader une photo de vêtement.",
        [{ text: "OK" }]
      );
      return null;
    }

    if (!response.ok) {
      throw new Error("Erreur lors de l'analyse");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Erreur:", error);
    throw error;
  }
};
```

### JavaScript / Fetch

```javascript
async function analyzeImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      body: formData,
    });

    if (response.status === 451) {
      const error = await response.json();
      alert(`Image bloquée: ${error.detail.reason}`);
      return null;
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Erreur:", error);
    throw error;
  }
}
```

## ⚙️ Configuration Personnalisée

### Ajuster le Seuil

Pour rendre la détection plus stricte :

```python
# config.py
CONTENT_MODERATION_CONFIG = {
    "enabled": True,
    "nsfw_threshold": 0.4,  # Plus strict (40%)
    "block_nsfw": True,
}
```

Pour rendre la détection plus permissive :

```python
# config.py
CONTENT_MODERATION_CONFIG = {
    "enabled": True,
    "nsfw_threshold": 0.75,  # Plus permissif (75%)
    "block_nsfw": True,
}
```

### Désactiver la Modération (Développement)

```python
# config.py
CONTENT_MODERATION_CONFIG = {
    "enabled": False,  # Désactivé
    "nsfw_threshold": 0.6,
    "block_nsfw": True,
}
```

## 📊 Métriques

Le système retourne des métriques de détection :

```python
{
  "is_safe": false,
  "reasons": ["nudité détectée"],
  "skin_percentage": 0.78,    # 78% de peau détectée
  "brightness": 185.5,        # Luminosité moyenne
  "confidence": 0.78          # Confiance de la détection
}
```

## 🚀 Évolutions Futures

### Pour Production

- [ ] Modèle ML spécialisé (NudeNet, NSFW Detector)
- [ ] Détection de visages
- [ ] Détection de contenu violent
- [ ] Cache de modération (hash des images)
- [ ] Logging et analytics
- [ ] API de révision manuelle

### Modèles ML Recommandés

1. **NudeNet** - Détection NSFW précise
2. **CLIP** - Analyse sémantique du contenu
3. **OpenAI Moderation API** - Service cloud
4. **Google Cloud Vision** - API de modération

## ⚠️ Limitations

### Détection Basique (MVP)

- Utilise une heuristique de couleur de peau
- Peut avoir des faux positifs/négatifs
- Ne détecte pas le contexte sémantique

### Faux Positifs Possibles

- Photos de maillots de bain sur mannequin
- Portraits en gros plan
- Images très claires/surexposées

### Faux Négatifs Possibles

- Contenu censuré/flouté
- Images sombres
- Certains types de contenu inapproprié

## 💡 Recommandations

### Pour le MVP

✅ La détection actuelle est suffisante pour un MVP
✅ Protège contre les cas d'abus évidents
✅ Configurable et facile à ajuster

### Pour la Production

⚠️ Envisager un modèle ML spécialisé
⚠️ Ajouter une révision manuelle
⚠️ Implémenter un système de signalement utilisateur

## 📞 Support

Pour toute question sur la modération :

1. Vérifier la configuration dans `config.py`
2. Consulter les logs du serveur
3. Tester avec `test_moderation.py`
4. Ajuster le seuil `nsfw_threshold` si nécessaire
