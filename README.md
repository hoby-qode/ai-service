# AI Clothing Service - Serahly

#Voici la commande bash pour lancer le serveur AI :
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

Service d'analyse d'images de vêtements utilisant l'IA pour le projet Serahly.

## 🎯 Objectif

Ce service analyse des images de vêtements et retourne des métadonnées structurées compatibles avec le schéma Strapi du projet Serahly.

## 🖼️ Suppression d'Arrière-Plan

Le service inclut un **système de suppression d'arrière-plan automatique** utilisant rembg (basé sur U²-Net) pour isoler les vêtements sur fond transparent.

### Endpoint

**POST** `/remove-background`

**Body** : `multipart/form-data`

- `file` : Image du vêtement (JPEG, PNG, WEBP)

**Response** : Image PNG avec arrière-plan supprimé

**Headers de réponse** :

- `Content-Disposition`: Nom du fichier traité
- `X-Original-Size`: Dimensions originales (WxH)
- `X-Processed-Size`: Dimensions traitées (WxH)
- `X-Has-Transparency`: true/false

### Utilisation

```javascript
const formData = new FormData();
formData.append("file", imageFile);

const response = await fetch("http://localhost:8000/remove-background", {
  method: "POST",
  body: formData,
});

if (response.ok) {
  const processedImageBlob = await response.blob();
  // Utiliser l'image traitée (format PNG avec transparence)
}
```

### Limites

- Taille maximale : 10MB
- Formats supportés : JPEG, PNG, WEBP
- Sortie : Toujours PNG avec canal alpha

### ⚠️ Limitations Windows

**rembg n'est pas compatible avec Windows** en raison de problèmes de compilation avec les dépendances scikit-image et pythran. Le service utilise automatiquement un **fallback simple** qui rend les pixels blancs transparents.

**Pour la production sur Linux/macOS** :

```bash
pip install rembg>=2.0.0
```

Le fallback garantit le fonctionnement sur tous les environnements, mais la qualité de suppression d'arrière-plan sera inférieure sans rembg.

## 🛡️ Modération de Contenu

Le service inclut un **système de modération automatique** qui bloque les images inappropriées :

- ✅ Détection de nudité
- ✅ Détection de contenu sexuel
- ✅ Protection automatique avec erreur HTTP 451
- ✅ Configurable via `config.py`

**Voir [CONTENT_MODERATION.md](CONTENT_MODERATION.md) pour plus de détails.**

### Codes d'Erreur

| Code | Signification | Description                        |
| ---- | ------------- | ---------------------------------- |
| 200  | ✅ Succès     | Image analysée avec succès         |
| 400  | ❌ Invalide   | Image invalide ou trop volumineuse |
| 451  | 🛡️ Bloqué     | Contenu inapproprié détecté        |
| 500  | ❌ Erreur     | Erreur serveur                     |

## 📋 Données Retournées

Le service analyse une image et retourne les informations suivantes, basées sur le schéma Strapi `clothing-item` :

### Structure de Réponse

```json
{
  "name": "Lin blanc",
  "type": "haut",
  "color": "blanc",
  "size": "M",
  "material": "Lin",
  "pattern": "Uni",
  "styles": ["Casual", "Minimaliste"],
  "embedding": [0.123, 0.456, ...],
  "brand": null,
  "confidence": 0.89
}
```

### Champs

| Champ        | Type   | Description                               | Valeurs Possibles                                                                          |
| ------------ | ------ | ----------------------------------------- | ------------------------------------------------------------------------------------------ |
| `name`       | string | Nom descriptif généré                     | "{material} {color}"                                                                       |
| `type`       | enum   | Type de vêtement (conforme Strapi)        | `haut`, `bas`, `chaussure`, `accessoire`, `autre`                                          |
| `color`      | string | Couleur détectée                          | `noir`, `blanc`, `gris`, `beige`, `bleu`, `marron`, `kaki`, `multicolore`, `camel`, `doré` |
| `size`       | string | Taille (adaptée au type)                  | Varie selon le type (XS-XXL, 34-44, etc.)                                                  |
| `material`   | string | Matière estimée                           | `Coton`, `Lin`, `Polyester`, `Laine`, `Cuir`, `Denim`, `Soie`, `Synthétique`               |
| `pattern`    | string | Motif                                     | `Uni`, `Rayé`, `À carreaux`, `Fleuri`, `Graphique`, `Imprimé`                              |
| `styles`     | array  | Liste de 1 à 3 styles                     | `Casual`, `Chic`, `Streetwear`, `Sportif`, `Vintage`, `Bohème`, `Minimaliste`, `Rock`      |
| `embedding`  | array  | Vecteur de 128 dimensions pour similarité | Float[]                                                                                    |
| `brand`      | null   | Marque (à remplir par utilisateur)        | -                                                                                          |
| `confidence` | float  | Score de confiance (0-1)                  | 0.0 - 1.0                                                                                  |

## 🔧 Intégration avec Strapi

### Mapping Direct

Les champs retournés correspondent directement au modèle `clothing-item` de Strapi :

**Schema Strapi** (`backend/src/api/clothing-item/content-types/clothing-item/schema.json`) :

- ✅ `type` → enum conforme
- ✅ `color` → string
- ✅ `size` → string
- ✅ `brand` → string
- ✅ `name` → string

### Styles

Les styles retournés correspondent aux entrées de la collection `style` de Strapi. Pour créer un `clothing-item`, il faut :

1. Analyser l'image via `/analyze`
2. Récupérer les styles correspondants depuis Strapi
3. Créer le `clothing-item` avec les relations

**Exemple d'intégration** :

```javascript
// 1. Analyser l'image
const formData = new FormData();
formData.append("file", imageFile);
const aiResult = await fetch("http://localhost:8000/analyze", {
  method: "POST",
  body: formData,
});
const data = await aiResult.json();

// 2. Récupérer les IDs des styles depuis Strapi
const styleIds = [];
for (const styleName of data.styles) {
  const style = await strapi.query("api::style.style").findOne({
    where: { name: styleName },
  });
  if (style) styleIds.push(style.id);
}

// 3. Créer le clothing-item dans Strapi
const clothingItem = await strapi
  .documents("api::clothing-item.clothing-item")
  .create({
    data: {
      name: data.name,
      type: data.type,
      color: data.color,
      size: data.size,
      brand: data.brand, // null par défaut
      style: styleIds,
      owner: userId,
      publishedAt: Date.now(),
    },
  });
```

## 🚀 Utilisation

### Démarrer le Service

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
uvicorn main:app --reload --port 8000
```

### Endpoint

**POST** `/analyze`

**Body** : `multipart/form-data`

- `file` : Image du vêtement

**Response** : JSON avec les métadonnées du vêtement

**POST** `/remove-background`

**Body** : `multipart/form-data`

- `file` : Image du vêtement

**Response** : Image PNG avec arrière-plan supprimé

## 📊 Sources de Données

Les valeurs possibles sont basées sur :

- **Types** : `backend/src/api/clothing-item/content-types/clothing-item/schema.json`
- **Styles** : `backend/scripts/seed-wardrobe.js` (stylesData)
- **Couleurs** : Exemples de `backend/scripts/seed-wardrobe.js` (clothingItemsData)

## 🔮 Évolutions Futures

- [x] Suppression d'arrière-plan automatique (rembg)
- [ ] Modèle spécialisé dans la classification de vêtements
- [ ] Détection de couleur réelle via analyse d'image
- [ ] OCR pour détecter la marque automatiquement
- [ ] Détection de motifs par vision par ordinateur
- [ ] API de similarité utilisant les embeddings
- [ ] Fine-tuning du modèle avec dataset de vêtements
