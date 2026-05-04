import json
import os
import subprocess
import sys

def main():
    # 1. Resolve variables dynamically via user prompts with fallback defaults
    default_project = os.getenv("GOOGLE_CLOUD_PROJECT") or "deepakmichael"
    default_location = os.getenv("GOOGLE_CLOUD_LOCATION") or "us-central1"
    default_gateway = os.getenv("AGENT_GATEWAY_ID") or "egress-agw"

    try:
        PROJECT_ID = input(f"Enter Google Cloud Project ID [{default_project}]: ").strip() or default_project
        LOCATION = input(f"Enter Google Cloud Location/Region [{default_location}]: ").strip() or default_location
        GATEWAY_ID = input(f"Enter Agent Gateway ID [{default_gateway}]: ").strip() or default_gateway
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
