import requests
import yaml

# Fetch data from URLs
offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()['client.dll']
client = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()['client.dll']
buttons = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/buttons.json').json()['client.dll']

# Define the configuration to be written to the YAML file
configuration = {
    # addresses
    'localplayerpawn': offsets['dwLocalPlayerPawn'],
    'entitylist': offsets['dwEntityList'],
    'gamerules': offsets['dwGameRules'],

    # offsets
    'warmup': client['classes']['C_CSGameRules']['fields']['m_bWarmupPeriod'],
    'rounds': client['classes']['C_CSGameRules']['fields']['m_totalRoundsPlayed'],
    'nickname': client['classes']['CBasePlayerController']['fields']['m_iszPlayerName'],
    'steamid': client['classes']['CBasePlayerController']['fields']['m_steamID'],
    'rounds': client['classes']['C_CSGameRules']['fields']['m_totalRoundsPlayed'],
    'gamepaused': client['classes']['C_CSGameRules']['fields']['m_bServerPaused'],
    'health': client['classes']['C_BaseEntity']['fields']['m_iHealth'],
    'index': client['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex'],
    'team': client['classes']['C_BaseEntity']['fields']['m_iTeamNum'],
    'onground': client['classes']['C_BaseEntity']['fields']['m_fFlags'],
    'scoped': client['classes']['C_CSPlayerPawn']['fields']['m_bIsScoped'],

    # buttons
    'lmb': buttons['attack'],
    'rmb': buttons['attack2'],
    'jump': buttons['jump'],
}

# Write the configuration to a YAML file
def offsets():
    with open('assets/offsets.yml', 'w') as yaml_file:
        yaml.dump(configuration, yaml_file)