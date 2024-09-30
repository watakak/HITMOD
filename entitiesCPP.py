import pymem  # library for memory operations
import time  # library for working with time
import yaml  # library for config read

pm = pymem.Pymem('cs2.exe')  # Counter-Strike 2 process
client = pymem.process.module_from_name(pm.process_handle, 'client.dll').lpBaseOfDll  # .dll with offsets

with open('config.yml', 'r') as file:  # config read
    cfg = yaml.safe_load(file)

dwLocalPlayerPawn = 0x17C17F0  # address/longlong
dwEntityList = 0x1954568  # address/longlong
dwGameRules = 0x19B1558  # address/longlong

__rounds__ = 0x84  # integral
__nickname__ = 0x640  # string
__steamid__ = 0x6C8  # integral
__gamepaused__ = 0x4C  # boolean
__shoot__ = 0x17BA020  # integral
__health__ = 0x324  # integral
__index__ = 0x13A8  # integral
__team__ = 0x3C3  # integral

cfgHitmarkes = cfg['hitMarkers']
cfgKillCount = cfg['killCount']

kills = 0
rounds = None
previousHealth = None  # Variable to store previous health value
lastIndex = None  # Variable to store the last entity index
lastIndexTime = 0  # Time when last entity was targeted

# Greeting
print('꧁ ༺ HITMOD ༻ ꧂')  # 1.1.4
print('    By watakaka\n')

while True:
    # Classes
    try:
        entityList = pm.read_longlong(client + dwEntityList)  # Entity list class
        localPlayerPawn = pm.read_longlong(client + dwLocalPlayerPawn)  # Player pawn class
        gameRules = pm.read_longlong(client + dwGameRules)  # Game rules class

        # Variables
        round = pm.read_int(gameRules + __rounds__)
        entIndex = pm.read_int(localPlayerPawn + __index__)  # Player index in crosshair
        gamePaused = pm.read_bool(gameRules + __gamepaused__)  # Is the server paused
        team = pm.read_int(localPlayerPawn + __team__)  # Team of the player
        shoot = pm.read_int(client + __shoot__)  # Left mouse button
    except pymem.exception.MemoryReadError as e:
        continue

    # If no entity is targeted, but recently one was
    if entIndex == -1 and lastIndex is not None:
        # Keep last target for 1 second
        if time.time() - lastIndexTime < 2:
            entIndex = lastIndex
        else:
            lastIndex = None  # Reset after 1 second

    # If shooting and entity in crosshair
    if shoot == 65537 and entIndex != -1:  # Left mouse button and not air
        try:
            # Get Player Pawn
            listEntry = pm.read_longlong(entityList + 8 * ((entIndex & 0x7FF) >> 9) + 16)
            currentPawn = pm.read_longlong(listEntry + 120 * (entIndex & 0x1FF))

            # Get health and team
            healthID = pm.read_int(currentPawn + __health__)
            teamID = pm.read_int(currentPawn + __team__)

        except pymem.exception.MemoryReadError as e:
            continue

        # Damage/kill
        if team == 2 and teamID == 3 or team == 3 and teamID == 2:  # Check team
            if previousHealth is not None and healthID != previousHealth:  # Check health change
                if healthID == 0:
                    if cfgHitmarkes and cfgKillCount:
                        print(f'Kill! ✘')
                    if cfgHitmarkes and not cfgKillCount:
                        print(f'Kill! ✘\n')

                    if cfgKillCount:
                        kills = kills + 1
                        if kills == 1:
                            print('First blood! ☆\n')
                        elif kills == 2:
                            print('Double kill! ☆☆\n')
                        elif kills == 3:
                            print('Triple kill! ☆☆☆\n')
                        elif kills == 4:
                            print('Mega kill! ☆☆☆☆\n')
                        elif kills == 5:
                            print('Monster kill! ☆☆☆☆☆\n')
                        else:
                            print(f'Ultra kill! {('☆' * kills)}\n')

                elif healthID != 100:
                    if cfgHitmarkes:
                        print(f'Hit! {healthID}♡')
            previousHealth = healthID  # Update previous health

        # Friendly fire on/off
        elif team == 2 and teamID == 2 or team == 3 and teamID == 3:
            if previous_health is not None and healthID != previousHealth:  # Check health change
                if healthID == 0:
                    print(f'⚠ Friendly: Kill! ✘\n')
                elif healthID != 100:
                    print(f'⚠ Friendly: Hit! {healthID}♡')
            previousHealth = healthID  # Update previous health

        # Update lastIndex and lastIndexTime
        lastIndex = entIndex
        lastIndexTime = time.time()

    try:
        time.sleep(0.001)  # Sleep to reduce CPU load
    except KeyboardInterrupt:  # On program exit
        print('\nProgram terminated. Thanks for using!')
        exit(0)
