import json
import os
import subprocess
import sys

def main():
    # 1. Resolve variables from environment with sensible defaults
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or "deepakmichael"
    LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION") or "us-central1"
    GATEWAY_ID = os.getenv("AGENT_GATEWAY_ID") or "egress-agw"

    # 2. Construct config data dynamically
    config_data = {
        "identity_type": "AGENT_IDENTITY",
        "agent_gateway_config": {
            "agent_to_anywhere_config": {
                "agent_gateway": f"projects/{PROJECT_ID}/locations/{LOCATION}/agentGateways/{GATEWAY_ID}"
            }
        },
        "env_vars": {
            "GOOGLE_API_PREVENT_AGENT_TOKEN_SHARING_FOR_GCP_SERVICES": "false"
        }
    }

    # 3. Write to .agent_engine_config.json
    config_path = ".agent_engine_config.json"
    try:
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)
        print(f"Successfully generated {config_path} dynamically.")
    except Exception as e:
        print(f"Failed to write config file: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Run adk deploy
    cmd = [
        "adk", "deploy", "agent_engine",
        f"--project={PROJECT_ID}",
        f"--region={LOCATION}",
        "--display_name=Travel Agent for DJs",
        "."
    ]
    print(f"Running deployment command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("Deployment completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
