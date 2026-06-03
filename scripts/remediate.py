import os
import sys
import json
import duckdb
import sqlglot

def main():
    fix_type = os.getenv("FIX_TYPE", "SKIP").upper()
    fix_code = os.getenv("FIX_CODE", "").strip()
    db_path = "/app/data/pipeline.duckdb"

    if not fix_code:
        print("No fix code provided.", file=sys.stderr)
        outputs = {
            "status": "SKIPPED",
            "method": "NONE",
            "error_message": "No fix code provided."
        }
        print(f"::{json.dumps({'outputs': outputs})}::", flush=True)
        sys.exit(0)

    # ── Safety Check — AST-based SQL validation via sqlglot ──
    ALLOWED_SQL_TYPES = {"update", "alter", "insert"}
    try:
        parsed = sqlglot.parse(fix_code, dialect="duckdb")
        for stmt in parsed:
            if stmt is None:
                continue
            stmt_type = stmt.key.lower()
            if stmt_type not in ALLOWED_SQL_TYPES:
                err_msg = f"Safety violation: blocked statement type '{stmt_type.upper()}' (only UPDATE/ALTER/INSERT allowed)"
                print(err_msg, file=sys.stderr)
                outputs = {
                    "status": "FAILED",
                    "method": "SAFETY_CHECK",
                    "error_message": err_msg
                }
                print(f"::{json.dumps({'outputs': outputs})}::", flush=True)
                sys.exit(1)
        print(f"✅ SQL safety check passed (statement type: {', '.join(s.key.upper() for s in parsed if s)})")
    except sqlglot.errors.ParseError as e:
        err_msg = f"Safety violation: unparseable SQL blocked — {e}"
        print(err_msg, file=sys.stderr)
        outputs = {
            "status": "FAILED",
            "method": "SAFETY_CHECK",
            "error_message": err_msg
        }
        print(f"::{json.dumps({'outputs': outputs})}::", flush=True)
        sys.exit(1)

    # ── Execution ──────────────────────────────────
    if fix_type == "SQL":
        if not os.path.exists(db_path):
            err_msg = f"Database file not found at {db_path}."
            print(err_msg, file=sys.stderr)
            outputs = {
                "status": "FAILED",
                "method": "AUTO_SQL",
                "error_message": err_msg
            }
            print(f"::{json.dumps({'outputs': outputs})}::", flush=True)
            sys.exit(1)

        print(f"Connecting to DuckDB at {db_path}...")
        con = duckdb.connect(db_path)
        try:
            print(f"Executing SQL Fix:\n{fix_code}")
            con.execute(fix_code)
            print("SQL executed successfully.")
            outputs = {
                "status": "FIXED",
                "method": "AUTO_SQL",
                "executed_code": fix_code
            }
        except Exception as e:
            err_msg = f"SQL error: {str(e)}"
            print(err_msg, file=sys.stderr)
            outputs = {
                "status": "FAILED",
                "method": "AUTO_SQL",
                "error_message": err_msg
            }
        finally:
            con.close()

    elif fix_type == "PYTHON":
        print("⚠️ Python execution blocked for security. Manual review required.")
        print(f"Proposed Python code:\n{fix_code}")
        outputs = {
            "status": "BLOCKED",
            "method": "PYTHON_BLOCKED",
            "error_message": "Python execution disabled for security. Review fix_code manually.",
            "proposed_code": fix_code
        }

    else:
        # For SKIP or RETRY
        outputs = {
            "status": "SKIPPED",
            "method": fix_type,
            "error_message": f"Execution skipped for fix type: {fix_type}."
        }

    # Write output to Kestra format
    print(f"::{json.dumps({'outputs': outputs})}::", flush=True)
    
    if outputs["status"] == "FAILED":
        sys.exit(1)

if __name__ == "__main__":
    main()
