import os
import sys
import json
from google import genai
from google.genai import types

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # Get inputs from environment variables
    pipeline_name = os.getenv("PIPELINE_NAME", "unknown")
    error_type = os.getenv("ERROR_TYPE", "UNKNOWN")
    error_message = os.getenv("ERROR_MESSAGE", "")
    affected_table = os.getenv("AFFECTED_TABLE", "unknown")
    schema_info = os.getenv("SCHEMA_INFO", "")
    sample_data = os.getenv("SAMPLE_DATA", "")

    # Construct the prompt
    prompt = f"""
You are Kestra Aegis, an automated self-healing pipeline assistant.
Your task is to analyze a failed data pipeline run and generate a fix.

Failure details:
- Pipeline Name: {pipeline_name}
- Error Type: {error_type}
- Error Message: {error_message}
- Affected Table: {affected_table}
- Schema Info: {schema_info}
- Sample Data: {sample_data}

Target Database is DuckDB. Use DuckDB-compatible SQL syntax.
Never generate DROP, DELETE, or TRUNCATE statements.

If the fix is a SQL query, set fix_type to 'SQL' and fix_code to the SQL statement.
If the fix is a python script, set fix_type to 'PYTHON' and fix_code to the Python script.
If the pipeline should be retried later, set fix_type to 'RETRY'.
If the error is unknown or cannot be fixed safely, set fix_type to 'SKIP' and risk_assessment to 'HIGH'.
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "root_cause": types.Schema(type=types.Type.STRING),
                        "fix_type": types.Schema(type=types.Type.STRING, enum=["SQL", "PYTHON", "RETRY", "SKIP"]),
                        "fix_code": types.Schema(type=types.Type.STRING),
                        "explanation": types.Schema(type=types.Type.STRING),
                        "confidence": types.Schema(type=types.Type.NUMBER),
                        "risk_assessment": types.Schema(type=types.Type.STRING, enum=["LOW", "HIGH"])
                    },
                    required=["root_cause", "fix_type", "fix_code", "explanation", "confidence", "risk_assessment"]
                )
            )
        )
        
        result_json = json.loads(response.text)
    except Exception as e:
        print(f"Gemini API or Parse Error: {e}", file=sys.stderr)
        # Fallback response
        result_json = {
            "root_cause": f"Error during Gemini diagnosis: {str(e)}",
            "fix_type": "SKIP",
            "fix_code": "",
            "explanation": "Aegis failed to diagnose the issue using Gemini API.",
            "confidence": 0.0,
            "risk_assessment": "HIGH"
        }

    # Write output to Kestra format
    print(f"::{json.dumps({'outputs': result_json})}::", flush=True)

if __name__ == "__main__":
    main()
