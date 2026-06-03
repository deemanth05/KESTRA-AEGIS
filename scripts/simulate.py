import sys
import argparse
import json
import os
import duckdb

def main():
    parser = argparse.ArgumentParser(description="Simulate data pipeline failures in DuckDB")
    parser.add_argument("--type", type=str, required=True, choices=["TYPE_MISMATCH", "NULL_VIOLATION", "SCHEMA_DRIFT"], help="Failure scenario type")
    args = parser.parse_args()

    db_path = "/app/data/pipeline.duckdb"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found. Please run setup_database first.", file=sys.stderr)
        sys.exit(1)

    con = duckdb.connect(db_path)
    
    pipeline_name = "daily_orders_ingest"
    affected_table = "orders"
    schema_info = "order_id INTEGER, customer_name VARCHAR, amount DECIMAL(10,2), order_date DATE"
    
    payload = {}

    try:
        if args.type == "TYPE_MISMATCH":
            # Attempt to insert a bad record to trigger conversion error
            try:
                # We force conversion error in DuckDB
                con.execute("INSERT INTO orders VALUES (16, 'Bad Charlie', 'not_a_number', '2026-06-03')")
                # If it somehow succeeds, fetch it
                error_msg = "Successfully inserted but value type is incorrect"
            except Exception as e:
                error_msg = str(e)
            
            payload = {
                "pipeline_name": pipeline_name,
                "error_type": "TYPE_MISMATCH",
                "error_message": f"Column 'amount' expected DECIMAL but got VARCHAR 'not_a_number'. Database error: {error_msg}",
                "affected_table": affected_table,
                "schema_info": schema_info,
                "sample_data": "Row 16: (16, 'Bad Charlie', 'not_a_number', '2026-06-03')",
                "stack_trace": "Traceback (most recent call last):\n  File \"daily_orders_ingest.py\", line 45, in load_csv\n    con.execute(\"INSERT INTO orders VALUES (?, ?, ?, ?)\", row)\nConversionException: Conversion Error: Could not convert string 'not_a_number' to DOUBLE"
            }

        elif args.type == "NULL_VIOLATION":
            # Set some amounts to NULL to simulate a data quality failure (e.g. amount is mandatory)
            con.execute("UPDATE orders SET amount = NULL WHERE order_id IN (2, 8)")
            
            payload = {
                "pipeline_name": pipeline_name,
                "error_type": "NULL_VIOLATION",
                "error_message": "Data Quality check failed: 'amount' column contains NULL values in non-nullable constraints.",
                "affected_table": affected_table,
                "schema_info": schema_info,
                "sample_data": "Row 2: (2, 'Bob Johnson', NULL, '2026-06-01'), Row 8: (8, 'Hannah Abbott', NULL, '2026-06-03')",
                "stack_trace": "AssertionError: Column 'amount' in table 'orders' failed validation rule 'not_null_check'."
            }

        elif args.type == "SCHEMA_DRIFT":
            # Simulate a scenario where a new column is in the source data but doesn't exist in the database table schema
            payload = {
                "pipeline_name": pipeline_name,
                "error_type": "SCHEMA_DRIFT",
                "error_message": "Schema mismatch: Source CSV contains 5 columns, but target table 'orders' expects 4 columns. Missing column in target: 'discount_code'",
                "affected_table": affected_table,
                "schema_info": schema_info,
                "sample_data": "Header: order_id,customer_name,amount,order_date,discount_code\nRow 1: (1, 'Alice Smith', 120.50, '2026-06-01', 'SAVE10')",
                "stack_trace": "ValueError: Columns in source data do not match target database schema."
            }
            
        # Write Kestra outputs
        try:
            from kestra import Kestra
            Kestra.outputs({"payload": payload})
            print("Successfully wrote Kestra outputs.")
        except ImportError:
            # If running locally without Kestra package, just output JSON to stdout
            print(json.dumps(payload, indent=2))

    finally:
        con.close()

if __name__ == "__main__":
    main()
