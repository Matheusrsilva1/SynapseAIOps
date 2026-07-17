import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Get paths dynamically
src_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(src_dir)
load_dotenv(os.path.join(base_dir, ".env"))

class DBConnection:
    def __init__(self):
        self.using_supabase = False
        self.engine = None
        self.duck_con = None
        
        # Local paths for fallback
        self.data_dir = os.path.join(base_dir, "data")
        self.db_path = os.path.join(self.data_dir, "synapse_aiops.db")
        
        db_url = os.getenv("SUPABASE_DB_URL")
        
        if db_url:
            try:
                # SQLAlchemy requires postgresql:// instead of postgres://
                if db_url.startswith("postgres://"):
                    db_url = db_url.replace("postgres://", "postgresql://", 1)
                
                self.engine = create_engine(db_url)
                # Test connection
                with self.engine.connect() as conn:
                    pass
                self.using_supabase = True
                print("Connected to Supabase PostgreSQL Database!")
            except Exception as e:
                print(f"Supabase connection failed: {e}. Falling back to local DuckDB.")
                
        if not self.using_supabase:
            import duckdb
            os.makedirs(self.data_dir, exist_ok=True)
            self.duck_con = duckdb.connect(self.db_path)
            print(f"Connected to local DuckDB Database at {self.db_path}!")

    def execute(self, query, params=None):
        if self.using_supabase:
            conn = self.engine.connect()
            trans = conn.begin()
            try:
                res = conn.execute(text(query), params or {})
                trans.commit()
                return SQLAResultWrapper(res, conn)
            except Exception as e:
                trans.rollback()
                conn.close()
                raise e
        else:
            res = self.duck_con.execute(query, params)
            return DuckDBResultWrapper(res)

    def close(self):
        if self.duck_con:
            self.duck_con.close()
        if self.engine:
            self.engine.dispose()

class SQLAResultWrapper:
    def __init__(self, result, connection):
        self.result = result
        self.connection = connection

    def fetchone(self):
        try:
            if self.result.returns_rows:
                row = self.result.fetchone()
                return row
            return None
        except Exception:
            return None
        finally:
            self.connection.close()

    def fetchdf(self):
        try:
            if self.result.returns_rows:
                columns = self.result.keys()
                df = pd.DataFrame(self.result.fetchall(), columns=columns)
                return df
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()
        finally:
            self.connection.close()

class DuckDBResultWrapper:
    def __init__(self, result):
        self.result = result

    def fetchone(self):
        return self.result.fetchone()

    def fetchdf(self):
        return self.result.fetchdf()
