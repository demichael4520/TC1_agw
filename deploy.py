import json
import os
import subprocess
import sys

def main():
    # 1. Resolve variables dynamically via strict user prompts without fallback defaults
    try:
        PROJECT_ID = input("Enter Google Cloud Project ID: ").strip()
        while not PROJECT_ID:
            PROJECT_ID = input("Project ID is required. Enter Google Cloud Project ID: ").strip()

        LOCATION = input("Enter Google Cloud Location/Region (e.g., us-central1): ").strip()
        while not LOCATION:
            LOCATION = input("Location is required. Enter Google Cloud Location/Region: ").strip()

        GATEWAY_ID = input("Enter Agent Gateway ID: ").strip()
        while not GATEWAY_ID:
            GATEWAY_ID = input("Gateway ID is required. Enter Agent Gateway ID: ").strip()
    except KeyboardInterrupt:
        print("\nDeployment cancelled by user.")
        sys.exit(0)

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
