from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); print("
Table Structure:
"); [print(f"{c.name}: {str(c.type)} ({NOT NULL if not c.nullable else NULL}) { PRIMARY KEY if c.primary_key else } {f" DEFAULT {c.server_default.arg if c.server_default else c.default}" if c.server_default or c.default else }") for c in db.metadata.tables["user"].columns]
