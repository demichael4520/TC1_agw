import sys
import os
from typing import Any, Dict, Optional
import google.auth
import google.auth.transport.requests
from google.adk.agents import LlmAgent
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams


def get_auth_headers(context: Optional[Any] = None) -> Dict[str, str]:
  """Dynamically fetches regional authentication Bearer tokens to pass to Google MCP servers."""
  print('[HeaderProvider] Refreshing Google credentials...', file=sys.stderr)
  try:
    credentials, project = google.auth.default(
        scopes=[
            'https://www.googleapis.com/auth/bigquery',
            'https://www.googleapis.com/auth/cloud-platform',
        ]
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    token = credentials.token

    # Resolve project ID dynamically, prioritizing user-supplied environment variables over credentials context to prevent tenant container billing project resolution issues
    target_project = os.getenv('GOOGLE_CLOUD_PROJECT') or project

    print(
        f'[HeaderProvider] Token refreshed for project {target_project}.',
        file=sys.stderr,
    )
    return {
        'Authorization': f'Bearer {token}',
        'x-goog-user-project': target_project,
    }
  except Exception as e:
    print(f'[HeaderProvider] Error fetching credentials: {e}', file=sys.stderr)
    return {}


# Define connection parameters for Google Managed BigQuery MCP toolset
connection_params = StreamableHTTPConnectionParams(
    url='https://bigquery.googleapis.com/mcp'
)

# Instanciate official Google BigQuery MCP Toolset
bigquery_mcp_tools = McpToolset(
    connection_params=connection_params,
    header_provider=get_auth_headers,
)



# Define Standalone DJ Root Agent utilizing BQ MCP tools
dj_root_agent = LlmAgent(
    name='dj_root_agent',
    model='gemini-2.5-flash',
    instruction=(
        'You are a travel and music concierge assistant. Assist users querying'
        ' the BigQuery database using your tools. You MUST use the BigQuery'
        ' execute_sql or execute_sql_readonly tool to query the database.'
        ' Query against the active project or the specific project ID supplied'
        ' by the user. You have access to the table `travel_app_ds.disk_jockeys`'
        ' (e.g. `SELECT * FROM travel_app_ds.disk_jockeys` or'
        ' `SELECT * FROM user_project_id.travel_app_ds.disk_jockeys`).'
    ),
    description='Standalone ADK agent utilizing Google Managed BigQuery MCP tools.',
    tools=[bigquery_mcp_tools],
)

root_agent = dj_root_agent
