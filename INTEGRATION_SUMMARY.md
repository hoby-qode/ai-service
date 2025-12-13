# 🎨 Intégration AI Service avec Serahly - Résumé des Changements

## 📝 Vue d'ensemble

Le service AI a été mis à jour pour utiliser les vraies données du projet Serahly (Strapi + App mobile) au lieu de valeurs fictives.

## ✅ Changements Effectués

### 1. **Configuration Centralisée** (`config.py`)

- ✅ Types de vêtements synchronisés avec l'enum Strapi `clothing-item.type`
- ✅ Styles extraits de `seed-wardrobe.js`
- ✅ Couleurs basées sur les données de seed existantes
- ✅ Tailles adaptées par type de vêtement
- ✅ Matières et motifs étendus

### 2. **Utilitaires Mis à Jour** (`utils.py`)

- ✅ Import des constantes depuis `config.py`
- ✅ Fonction `analyze_image()` retourne un format compatible Strapi
- ✅ Embedding de 128 dimensions pour recherche de similarité
- ✅ Support multi-styles (1 à 3 styles par vêtement)

### 3. **Documentation** (`README.md`)

- ✅ Guide complet d'intégration avec Strapi
- ✅ Exemples de code pour créer un `clothing-item`
- ✅ Mapping des champs avec le schema Strapi
- ✅ Roadmap des évolutions futures

### 4. **Tests** (`test_service.py`)

- ✅ Script de validation du service
- ✅ Vérification de la compatibilité Strapi

## 📊 Données Synchronisées

### Types de Vêtements (Strapi Enum)

```python
["haut", "bas", "chaussure", "accessoire", "autre"]
```

**Source:** `backend/src/api/clothing-item/content-types/clothing-item/schema.json`

### Styles Disponibles

```python
["Casual", "Chic", "Streetwear", "Sportif", "Vintage", "Bohème", "Minimaliste", "Rock"]
```

**Source:** `backend/scripts/seed-wardrobe.js` (stylesData)

### Couleurs

```python
["noir", "blanc", "gris", "beige", "bleu", "marron", "kaki", "rouge",
 "vert", "jaune", "rose", "multicolore", "camel", "doré"]
```

**Source:** Exemples de `backend/scripts/seed-wardrobe.js` (clothingItemsData)

## 🔄 Format de Réponse

### Avant

```json
{
  "category": "T-shirt",
  "material": "Coton",
  "color": "Bleu clair",
  "pattern": "Uni",
  "style": "Casual",
  "embedding": [...]
}
```

### Après (Compatible Strapi)

```json
{
  "name": "Lin blanc",
  "type": "haut",
  "color": "blanc",
  "size": "M",
  "material": "Lin",
  "pattern": "Uni",
  "styles": ["Casual", "Minimaliste"],
  "embedding": [...],
  "brand": null,
  "confidence": 0.89
}
```

## 🔗 Intégration avec Strapi

### Workflow Complet

```javascript
// 1. Analyser l'image via AI Service
const formData = new FormData();
formData.append("file", imageFile);
const response = await fetch("http://localhost:8000/analyze", {
  method: "POST",
  body: formData,
});
const aiData = await response.json();

// 2. Récupérer les IDs des styles depuis Strapi
const styleIds = [];
for (const styleName of aiData.styles) {
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
      name: aiData.name,
      type: aiData.type, // ✅ Compatible avec enum Strapi
      color: aiData.color,
      size: aiData.size,
      brand: aiData.brand, // null par défaut
      style: styleIds, // ✅ Relations avec collection Style
      owner: userId,
      for_sale: false,
      publishedAt: Date.now(),
    },
  });
```

## 🧪 Comment Tester

```bash
# 1. Aller dans le dossier ai-service
cd d:/KANDRA/Serahly/ai-service

# 2. Installer les dépendances (si nécessaire)
pip install -r requirements.txt

# 3. Lancer les tests
python test_service.py

# 4. Démarrer le service
uvicorn main:app --reload --port 8000
```

## 📁 Fichiers Modifiés

- ✅ `config.py` - **NOUVEAU** - Configuration centralisée
- ✅ `utils.py` - Mis à jour avec les vraies données
- ✅ `test_service.py` - **NOUVEAU** - Tests de validation
- ✅ `README.md` - **NOUVEAU** - Documentation complète
- ✅ `INTEGRATION_SUMMARY.md` - **NOUVEAU** - Ce fichier

## 🎯 Prochaines Étapes

### À Faire Côté App Mobile (React Native)

1. Créer un service pour appeler l'AI endpoint `/analyze`
2. Implémenter l'upload d'images depuis la caméra/galerie
3. Mapper la réponse AI vers le format d'envoi Strapi
4. Gérer les relations avec les styles
5. Ajouter un UI de confirmation/édition avant sauvegarde

### À Faire Côté Backend (Strapi)

1. Créer un endpoint custom pour recevoir image + métadonnées AI
2. Sauvegarder l'image dans la media library Strapi
3. Créer automatiquement le clothing-item avec les bonnes relations
4. Optionnel : Stocker les embeddings pour recherche de similarité

### Évolutions Futures AI Service

- [ ] Modèle spécialisé pour vêtements (Fashion-MNIST, DeepFashion)
- [ ] Détection de couleur réelle par analyse d'image
- [ ] OCR pour détecter les marques
- [ ] API de similarité (recherche par embedding)
- [ ] Fine-tuning avec dataset custom

## 📞 Points de Contact

- **AI Service:** `http://localhost:8000`
- **Endpoint:** `POST /analyze`
- **Backend Strapi:** `http://192.168.0.190:3002`
- **Schema:** `api::clothing-item.clothing-item`

## ✨ Avantages

✅ **Cohérence des données** - Utilise les mêmes valeurs que Strapi
✅ **Type-safe** - Enum Strapi respecté
✅ **Maintenable** - Configuration centralisée
✅ **Extensible** - Facile d'ajouter de nouvelles valeurs
✅ **Testé** - Script de validation inclus
✅ **Documenté** - README complet avec exemples
