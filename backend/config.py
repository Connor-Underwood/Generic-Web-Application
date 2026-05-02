import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'site.db')

# SQLite is effectively SERIALIZABLE: it serializes write transactions through a
# database-level lock, so two concurrent writers cannot observe each other's
# uncommitted state. The level is explicitly so the choice is visible in code.

SQLALCHEMY_ENGINE_OPTIONS = {
    "isolation_level": "SERIALIZABLE",
}
