import duckdb
import os
import sys

def main():
    db_path = "/app/data/pipeline.duckdb"
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        sys.exit(1)

    con = duckdb.connect(db_path)
    try:
        print("--- TABLES ---")
        tables = con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
        print(tables)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    main()
