from app import create_app
import os
from alembic import command
from alembic.config import Config as AlembicConfig

app = create_app()

def run_migrations():
    """Run Alembic migrations on startup."""
    try:
        alembic_cfg = AlembicConfig("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Alembic migrations applied successfully.")
    except Exception as e:
        print(f"❌ Failed to apply migrations: {e}")

if __name__ == "__main__":
    with app.app_context():
        run_migrations()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true"
    )
