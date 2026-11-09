import os
from flask import Flask
from dotenv import load_dotenv
from app.database import init_db, close_db, DEFAULT_DB_PATH

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "seven-phase-ascension-arcane-secret-key-2026"),
        DATABASE=os.getenv("DATABASE_PATH", DEFAULT_DB_PATH),
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    # Ensure database is initialized
    db_path = app.config["DATABASE"]
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        with app.app_context():
            init_db(db_path=db_path, seed=True)

    # Register teardown
    app.teardown_appcontext(close_db)

    # Register Blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.api_campaigns import campaigns_bp
    from app.blueprints.api_quests import quests_bp
    from app.blueprints.api_grimoire import grimoire_bp
    from app.blueprints.api_reliquary import reliquary_bp
    from app.blueprints.api_oracle import oracle_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(quests_bp)
    app.register_blueprint(grimoire_bp)
    app.register_blueprint(reliquary_bp)
    app.register_blueprint(oracle_bp)

    return app

