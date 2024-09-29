import pymem  # library for memory operations
import time  # library for working with time

# Btw the file itself called "entitiesCPP.py",
# but there's nothing with C++ or stuff like that.
# I dont know, it just fun and i like it.

pm = pymem.Pymem('cs2.exe')  # Counter-Strike 2 process
client = pymem.process.module_from_name(pm.process_handle, 'client.dll').lpBaseOfDll  # .dll with offsets

dwLocalPlayerPawn = 0x17C17F0  # address/longlong
dwEntityList = 0x1954568  # address/longlong
dwGameRules = 0x19B1558  # address/longlong

__nickname__ = 0x640 # string
__steamid__ = 0x6C8 # integral
__gamepaused__ = 0x4C  # boolean
__shoot__ = 0x17BA020  # integral
__health__ = 0x324  # integral
__index__ = 0x13A8  # integral
__team__ = 0x3C3  # integral

previous_health = None  # Variable to store previous health value
lastIndex = None  # Variable to store the last entity index
lastIndexTime = 0  # Time when last entity was targeted

# Greeting
print('꧁ ༺ HITMOD ༻ ꧂')  # 1.0.45
print('    By watakaka\n')

while True:
    # Classes
    try:
        entityList = pm.read_longlong(client + dwEntityList)  # Entity list class
        localPlayerPawn = pm.read_longlong(client + dwLocalPlayerPawn)  # Player pawn class
        gameRules = pm.read_longlong(client + dwGameRules)  # Game rules class

        # Variables
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
            if previous_health is not None and healthID != previous_health:  # Check health change
                if healthID == 0:
                    print(f'Kill! ✘\n')
                elif healthID != 100:
                    print(f'Hit! {healthID}♡')
            previous_health = healthID  # Update previous health

        # Friendly fire on/off
        elif team == 2 and teamID == 2 or team == 3 and teamID == 3:
            if previous_health is not None and healthID != previous_health:  # Check health change
                if healthID == 0:
                    print(f'⚠ Friendly: Kill! ✘\n')
                elif healthID != 100:
                    print(f'⚠ Friendly: Hit! {healthID}♡')
            previous_health = healthID  # Update previous health

        # Update lastIndex and lastIndexTime
        lastIndex = entIndex
        lastIndexTime = time.time()

    try:
        time.sleep(0.001)  # Sleep to reduce CPU load
    except KeyboardInterrupt:  # On program exit
        print('\nProgram terminated. Thanks for using!')
        exit(0)
