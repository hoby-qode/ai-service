#!/usr/bin/env python3
"""
Script de démarrage du serveur avec gestion d'erreurs
"""

import sys
import traceback

try:
    from main import app
    import uvicorn

    print("🚀 Démarrage du serveur AI Clothing Service...")
    print("📍 Endpoints disponibles:")
    print("   - GET  /")
    print("   - GET  /health")
    print("   - GET  /config")
    print("   - POST /analyze")
    print("   - POST /remove-background")
    print("")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True
    )

except Exception as e:
    print(f"❌ Erreur lors du démarrage du serveur: {e}")
    traceback.print_exc()
    sys.exit(1)