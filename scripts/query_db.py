import duckdb
import os

def main():
    db_path = "/app/data/pipeline.duckdb"
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    con = duckdb.connect(db_path)
    try:
        print("--- Table schema for 'orders' ---")
        schema = con.execute("PRAGMA table_info('orders')").fetchall()
        for col in schema:
            print(col)

        print("\n--- Rows in 'orders' (limit 20) ---")
        rows = con.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    main()
