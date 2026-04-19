import os
import sys

from backend import create_app, db
from sqlalchemy import create_engine, text

def migrate():
    print('=============================================')
    print('🚀 SQLite to InsForge PostgreSQL Migrator')
    print('=============================================')
    postgres_url = input("Enter your InsForge Postgres Connection String:\n> ").strip()
    
    if not postgres_url:
        print("URL cannot be empty!")
        return

    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

    app = create_app()

    with app.app_context():
        sqlite_engine = db.engine
        pg_engine = create_engine(postgres_url)
        
        print("\n📦 Setting up database schema on InsForge...")
        db.metadata.create_all(pg_engine)
        
        with sqlite_engine.connect() as sqlite_conn:
            with pg_engine.begin() as pg_conn:
                for table in db.metadata.sorted_tables:
                    # Clear existing data in Postgres table just in case
                    pg_conn.execute(table.delete())
                    
                    rows = sqlite_conn.execute(table.select()).mappings().all()
                    print(f"Migrating {len(rows)} records into `{table.name}`...")
                    if rows:
                        pg_conn.execute(table.insert(), [dict(row) for row in rows])
                    
                    # Fix Sequences so Postgres doesn't throw Duplicate Key errors on new Inserts
                    if 'id' in table.columns:
                        seq_name = f"{table.name}_id_seq"
                        try:
                            # Safely set the sequence to MAX(id) + 1
                            pg_conn.execute(text(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX(id)+1 FROM {table.name}), 1), false);"))
                        except Exception as e:
                            pass
                            
        print("\n✅ Migration complete! Your cloud database is ready for Render.")

if __name__ == '__main__':
    migrate()
