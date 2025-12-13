import socket

def get_local_ip():
    """Récupère l'IP locale de la machine"""
    try:
        # Créer un socket pour trouver l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connexion à une adresse externe (pas besoin que ce soit accessible)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback
        return socket.gethostbyname(socket.gethostname())

if __name__ == "__main__":
    ip = get_local_ip()
    print("=" * 60)
    print("🌐 Configuration AI Service pour Mobile")
    print("=" * 60)
    print()
    print(f"📱 Votre IP locale : {ip}")
    print()
    print("📝 Modifiez le fichier : serahly/src/config/ai.config.ts")
    print()
    print("Remplacez la ligne 'mobile' par :")
    print(f'    mobile: "http://{ip}:8000",')
    print()
    print("=" * 60)
