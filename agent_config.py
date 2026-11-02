"""
SENTINELNET Monitoring Agent Configuration
"""

# ---------------------------------------------------------
# AGENT INFORMATION
# ---------------------------------------------------------

AGENT_ID = "SENTINEL-AGENT-001"

AGENT_NAME = "SentinelNet Monitoring Agent"


# ---------------------------------------------------------
# SECURITY CONSOLE CONNECTION
# ---------------------------------------------------------

# For development on the SAME computer as the Console:
CONSOLE_HOST = "127.0.0.1"

# Port used by the SentinelNet Security Console.
CONSOLE_PORT = 5000


# ---------------------------------------------------------
# SECURITY CONSOLE API
# ---------------------------------------------------------

# Endpoint that the Agent will use to send monitoring data.
DATA_ENDPOINT = "/api/agent/data"


# Complete URL is constructed from the settings above.
CONSOLE_URL = (
    f"http://{CONSOLE_HOST}:{CONSOLE_PORT}"
    f"{DATA_ENDPOINT}"
)


# ---------------------------------------------------------
# MONITORING SETTINGS
# ---------------------------------------------------------

# Number of seconds between Agent data collections.
COLLECTION_INTERVAL = 5


# ---------------------------------------------------------
# NETWORK SETTINGS
# ---------------------------------------------------------

# How long the Agent waits for a Console response.
REQUEST_TIMEOUT = 5


# ---------------------------------------------------------
# LOCAL AGENT SETTINGS
# ---------------------------------------------------------

# Maximum number of processes sent in one monitoring packet.
MAX_PROCESSES = 50

# Maximum number of network connections sent in one packet.
MAX_NETWORK_CONNECTIONS = 100