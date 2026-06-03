import argparse
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Classify error risk level")
    parser.add_argument("--error-type", type=str, required=True, help="Type of failure error")
    parser.add_argument("--error-message", type=str, required=True, help="Failure error message")
    args = parser.parse_args()

    error_type = args.error_type.upper()
    error_msg = args.error_message

    # Rule-based risk assessment mapping
    HIGH_RISK_TYPES = ["SCHEMA_DRIFT", "DATA_LOSS", "PERMISSION_ERROR"]
    LOW_RISK_TYPES = ["TYPE_MISMATCH", "NULL_VIOLATION", "API_TIMEOUT", "STALE_DATA"]

    if error_type in HIGH_RISK_TYPES:
        risk_level = "HIGH"
    elif error_type in LOW_RISK_TYPES:
        risk_level = "LOW"
    else:
        # Default to HIGH for safety if type is unknown
        risk_level = "HIGH"

    outputs = {
        "risk_level": risk_level,
        "error_type": error_type,
        "error_message": error_msg
    }

    # Output to Kestra
    outputs_file = os.getenv("KESTRA_OUTPUTS_FILE")
    if outputs_file:
        with open(outputs_file, "w") as f:
            json.dump(outputs, f)
        print(f"Wrote outputs to Kestra: {outputs}")
    else:
        # Print to stdout if running locally
        print(json.dumps(outputs, indent=2))

if __name__ == "__main__":
    main()
