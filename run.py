import os
from app import create_app
from app.database import init_db

app = create_app()

if __name__ == '__main__':
    # Ensure initialized on startup
    with app.app_context():
        init_db(seed=True)
    
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
    print(f"[*] The Seven-Phase Ascension Life RPG starting on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

