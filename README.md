# Standalone BigQuery MCP Music Assistant Architecture

Standalone single-runtime AI Assistant deployed on Vertex AI Agent Engine utilizing the official **Google-Managed BigQuery MCP Toolset** to query BigQuery datasets seamlessly.

## Architecture Blueprints

- Exposes `dj_root_agent` Singleton/Single-turn LlmAgent.
- equipped with Google MCP Toolsets over connection endpoints `https://bigquery.googleapis.com/mcp`.
- Bypasses raw SQL Python files entirely, delegating DB tools (`execute_sql_readonly`) dynamically via Gemini models!

---

## ⚙️ Environment Setup & Virtualenv

 DO NOT invoke steps #1 & #2 from the dj_standalone_agent_identify DIRECTORY, doing so will result in a failure.  

Bootstrap the Python 3 virtual environment and install dependencies prior to deployment:

```bash
# 1. Running the following command in your HOME DIRECTORY
python3 -m venv ../venv_standalone

# 2. Activate environment in your HOME DIRECTORY
source ../venv_standalone/bin/activate


# 3. Install package dependencies
pip install -r requirements.txt
```

---

## 🗄️ Google BigQuery Ingestion Setup

Ingest the mock table `disk_jockeys` into your project's BQ datasets:

```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"

bq --project_id=$GOOGLE_CLOUD_PROJECT query \
    --use_legacy_sql=false < setup.sql
```

---

## 📋 Customizable Interactive Deployments for Agent Gateway Integration

To provide complete flexibility to deploy your agent with **any custom Project ID, Location, or Agent Gateway**, run the programmatic deployment script `deploy.py`. 

When executed, this script **interactively prompts you** to explicitly enter each value (non-empty inputs are strictly enforced and there are no silent fallback defaults):

```bash
# Run the interactive deployment script
python3 deploy.py
```

Example terminal interaction:
```text
Enter Google Cloud Project ID: deepakmichael
Enter Google Cloud Location/Region (e.g., us-central1): us-central1
Enter Agent Gateway ID: egress-agw
```

The script dynamically generates `.agent_engine_config.json` and deploys the agent seamlessly.



---

## 🔐 IAM Roles & Security Permissions

When deploying with **Agent Identity** (enabled via `.agent_engine_config.json`), the permissions are split between the **deployer principal** and the **agent identity principal** itself, adhering to the principle of least privilege.

### 1. Deployer Permissions (Researcher / Deploying Principal)
The executing principal that triggers `adk deploy` (e.g. your local Google Cloud user credential or VM Service Account) requires:
*   **Vertex AI User** (`roles/aiplatform.user`): To create and manage Reasoning Engine instances.
*   **Storage Admin** (`roles/storage.admin`) or **Storage Object Creator/Viewer** (`roles/storage.objectCreator` & `roles/storage.objectViewer`): Required to stage the deployment artifacts in the GCS bucket.

### 2. Agent Permissions (Granted to the Agent Identity)
Once deployed, the agent executes with its own unique principal ID format:
`principal://agents.global.org-ORGANIZATION_ID.system.id.goog/resources/aiplatform/projects/PROJECT_NUMBER/locations/LOCATION/reasoningEngines/AGENT_ENGINE_ID`

Grant the following roles to the **Agent Identity** (SPIFFE principal) so it can access BQ and models securely:
*   **BigQuery User** (`roles/bigquery.user`): To execute queries and jobs inside BigQuery.
*   **BigQuery Data Viewer** (`roles/bigquery.dataViewer`): Required on the target dataset to query table data.
*   **Vertex AI Express User** (`roles/aiplatform.expressUser`): To invoke Gemini models and call MCP tools.
*   **MCP Tool User** (`roles/mcp.toolUser`): Required to authorize calling Google-Managed MCP servers.

#### 1. Granting permissions to the Agent Identity using gcloud:
```bash
# Set environment variables
export PROJECT_ID="deepakmichael"
export PROJECT_NUMBER="1005790925927"
export ORG_ID="888160148396"
export AGENT_ENGINE_ID="3944964707332390912"

export AGENT_MEMBER="principal://agents.global.org-$ORG_ID.system.id.goog/resources/aiplatform/projects/$PROJECT_NUMBER/locations/us-central1/reasoningEngines/$AGENT_ENGINE_ID"

# Grant roles to the Agent Identity
gcloud alpha projects add-iam-policy-binding $PROJECT_ID --member="$AGENT_MEMBER" --role="roles/aiplatform.expressUser"
gcloud alpha projects add-iam-policy-binding $PROJECT_ID --member="$AGENT_MEMBER" --role="roles/bigquery.user"
gcloud alpha projects add-iam-policy-binding $PROJECT_ID --member="$AGENT_MEMBER" --role="roles/bigquery.dataViewer"
gcloud alpha projects add-iam-policy-binding $PROJECT_ID --member="$AGENT_MEMBER" --role="roles/mcp.toolUser"
```

#### 2. Granting permissions to Service Agents & Gateway SA:
To ensure successful routing and container operations, grant `roles/aiplatform.expressUser` and `roles/mcp.toolUser` to both the **Reasoning Engine Service Agent** and the **Agent Gateway Service Account**:

```bash
# Reasoning Engine Service Agent
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
    --role="roles/aiplatform.expressUser"

# Agent Gateway Service Account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-dep.iam.gserviceaccount.com" \
    --role="roles/mcp.toolUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-dep.iam.gserviceaccount.com" \
    --role="roles/aiplatform.expressUser"
```

---

## 🔧 Troubleshooting & Error Mitigation

### container upload package limits
* **Mitigation**: Reasoning Engine packages and stages all files in your current working directory (`.`) to GCS, which includes the `venv/` folder if created inside your codebase workspace, triggering payload size limit failures (> 8MB limit). 

To mitigate this seamlessly for any user, establish and bootstrap your virtual environment in the parent directory or another separate external path (e.g. `../venv_standalone/`) rather than inside the codebase directory itself. Reasoning Engine resolves and installs dependencies securely in its isolated cloud container automatically using only your `requirements.txt` file.

Example:
```bash
# Create virtual environment in parent directory
python3 -m venv ../venv_standalone
source ../venv_standalone/bin/activate
pip install -r requirements.txt

# Deploy seamlessly without payload limit bloat
adk deploy agent_engine \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --display_name="Travel Agent for DJs" \
    .
```
