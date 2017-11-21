from louisebot.config import config

# Load config
endpoint = config.get('default', 'endpoint')
API_TOKEN = config.get(endpoint, 'bot_token')

DEFAULT_REPLY = "Touche à ton cul"
PLUGINS = [
    'louisebot.plugins',
]

