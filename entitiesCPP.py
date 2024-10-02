import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # disable pygame greeting

import threading  # library for properly image timer render
import updater  # automaticly update offsets from github
import simage  # library for images render
import pygame  # library for playing audio/sound
import ctypes  # library for keyboard reading
import pymem  # library for memory operations
import time  # library for working with time
import yaml  # library for config read

updater.offsets()

pm = pymem.Pymem('cs2.exe')  # Counter-Strike 2 process
client = pymem.process.module_from_name(pm.process_handle, 'client.dll').lpBaseOfDll  # .dll with offsets

def configUpdate():
    global cfg

    with open('config.yml', 'r') as file:  # config read
        cfg = yaml.safe_load(file)

configUpdate()

with open('assets/offsets.yml', 'r') as file:  # config read
    offsets = yaml.safe_load(file)

# inits
pygame.mixer.init()
simage.init(1920, 1080)

# audio play system
def sound(audio):
    pygame.mixer.Sound(audio).play()

dwLocalPlayerPawn = offsets['localplayerpawn']  # address/longlong
dwEntityList = offsets['entitylist']  # address/longlong
dwGameRules = offsets['gamerules']  # address/longlong

__warmup__ = offsets['warmup']  # boolean
__rounds__ = offsets['rounds']  # integral
__nickname__ = offsets['nickname']  # string
__steamid__ = offsets['steamid']  # integral
__gamepaused__ = offsets['steamid']  # boolean
__health__ = offsets['health']  # integral
__index__ = offsets['index']  # integral
__team__ = offsets['team']  # integral
__onground__ = offsets['onground']  # integral
__scoped__ = offsets['scoped']  # boolean

__lmb__ = offsets['lmb']  # integral
__rmb__ = offsets['rmb']  # integral
__jump__ = offsets['jump']  # integral

cfgHitMarkers = cfg['hitMarkers']['enabled']
cfgHitMarkersSound = cfg['hitMarkers']['sound']
cfgHitMarkersKillSound = cfg['hitMarkers']['killSound']
cfgHitMarkersRender = cfg['hitMarkers']['render']['enabled']

cfgHMSizeHit = int(cfg['hitMarkers']['render']['sizeHit'])
cfgHMSizeKill = int(cfg['hitMarkers']['render']['sizeKill'])
cfgHMScopeSizeHit = int(cfg['hitMarkers']['render']['scopeSizeHit'])
cfgHMScopeSizeKill = int(cfg['hitMarkers']['render']['scopeSizeKill'])

cfgHMTimeHit = int(cfg['hitMarkers']['render']['timeHit'])
cfgHMTimeKill = int(cfg['hitMarkers']['render']['timeKill'])

cfgKillCount = cfg['killCount']['enabled']
cfgKillCountSound = cfg['killCount']['sound']

autoJump = cfg['autoJump']['enabled']
autoJumpSound = cfg['autoJump']['sound']

# Dynamic variables

previousRound = 0  # To store the previous round number
roundCounter = 0  # To keep track of total rounds
previousWarmup = None  # Initialize variable to track previous warmup state
warmupCounter = 0  # Initialize variable to track previous warmup state

kills = 0  # to store kills
randomStepKCSound = 0
previousHealth = None  # Variable to store previous health value
lastIndex = None  # Variable to store the last entity index
lastIndexTime = 0  # Time when last entity was targeted

roundChangeTime = None  # Variable to store the time when the round changed
warmupChangeTime = None  # Variable to store the time when the round changed

doubledJumpCheck = False

# Greetingd
print('꧁ ༺ HITMOD ༻ ꧂')  # 1.3.4
print('    By watakaka\n')

def main():
    global previousRound, roundCounter, previousWarmup, warmupCounter, kills, randomStepKCSound, previousHealth
    global lastIndex, lastIndexTime, roundChangeTime, warmupChangeTime, doubledJumpCheck

    while True:
        # Classes
        try:
            entityList = pm.read_longlong(client + dwEntityList)  # Entity list class
            localPlayerPawn = pm.read_longlong(client + dwLocalPlayerPawn)  # Player pawn class
            gameRules = pm.read_longlong(client + dwGameRules)  # Game rules class

            # Variables
            currentRound = pm.read_int(gameRules + __rounds__)  # Current round number
            warmup = pm.read_bool(gameRules + __warmup__)
            entIndex = pm.read_int(localPlayerPawn + __index__)  # Player index in crosshair
            gamePaused = pm.read_bool(gameRules + __gamepaused__)  # Is the server paused
            team = pm.read_int(localPlayerPawn + __team__)  # Team of the player
            leftMouseButton = pm.read_int(client + __lmb__)  # Left mouse button
            rightMouseButton = pm.read_int(client + __rmb__)  # Left mouse button
            jump = pm.read_int(client + __jump__)  # Jump button
            onGround = pm.read_int(localPlayerPawn + __onground__)  # Checks if player is on ground
            scoped = pm.read_int(localPlayerPawn + __scoped__)  # Checks if player is on ground
        except pymem.exception.MemoryReadError as e:
            continue

        # Round change detection
        if previousRound is None:  # First iteration setup
            previousRound = currentRound
        elif currentRound != previousRound:  # If the round changes
            previousRound = currentRound  # Update previous round
            roundCounter += 1  # Increment the total round counter
            roundChangeTime = time.time()  # Store the time of the round change

        # Warmup change detection
        if previousWarmup is None:  # First iteration setup
            previousWarmup = warmup
        elif warmup != previousWarmup:  # If warmup state changes
            previousWarmup = warmup  # Update the warmup state
            warmupCounter += 1  # Increment the warmup counter
            warmupChangeTime = time.time()  # Store the time of the warmup change

        # Delay the round message output by 2 seconds
        if roundChangeTime and time.time() - roundChangeTime >= 10:
            kills = 0  # Reset kill count

            print(f'New Round! Total Rounds: {roundCounter}\n')
            roundChangeTime = None  # Reset the timer after printing

        if warmupChangeTime and time.time() - warmupChangeTime >= 1:
            kills = 0  # Reset kill count

            if warmup:
                print('Warmup started!\n')
            else:
                print('Warmup/Match ended!\n')
            warmupChangeTime = None  # Reset the timer after printing

        # If no entity is targeted, but recently one was
        if entIndex == -1 and lastIndex is not None:
            # Keep last target for 1 second
            if time.time() - lastIndexTime < 2:
                entIndex = lastIndex
            else:
                lastIndex = None  # Reset after 1 second

        # Functions

        # If shooting and entity in crosshair
        if leftMouseButton == 65537 and entIndex != -1 or rightMouseButton == 65537 and entIndex != -1:  # Left mouse button and not air
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
            if team == 2 and teamID == 3 or team == 3 and teamID == 2 or team == 2 and teamID == 2 or team == 3 and teamID == 3:  # Check team
                if previousHealth is not None and healthID != previousHealth:  # Check health change
                    if healthID == 0:
                        if cfgHitMarkers and cfgKillCount:
                            print(f'Kill! ✘')
                            if cfgHitMarkersRender and scoped:
                                simage.show('assets/images/hitmarkers/kill.png', duration=cfgHMTimeKill,
                                            sizex=cfgHMScopeSizeKill, sizey=cfgHMScopeSizeKill)
                            elif cfgHitMarkersRender and not scoped:
                                simage.show('assets/images/hitmarkers/kill.png', duration=cfgHMTimeKill,
                                            sizex=cfgHMSizeKill, sizey=cfgHMSizeKill)
                            if cfgHitMarkersSound:
                                sound(f'assets/sounds/hitmarkers/{cfg['sounds']['hitMarkers']['hit']}')
                                if cfgHitMarkersKillSound:
                                    sound(f'assets/sounds/hitmarkers/{cfg['sounds']['hitMarkers']['kill']}')
                        if cfgHitMarkers and not cfgKillCount:
                            print(f'Kill! ✘\n')
                            if cfgHitMarkersRender and scoped:
                                simage.show('assets/images/hitmarkers/kill.png', duration=cfgHMTimeKill,
                                            sizex=cfgHMScopeSizeKill, sizey=cfgHMScopeSizeKill)
                            elif cfgHitMarkersRender and not scoped:
                                simage.show('assets/images/hitmarkers/kill.png', duration=cfgHMTimeKill,
                                            sizex=cfgHMSizeKill, sizey=cfgHMSizeKill)
                            if cfgHitMarkersSound:
                                sound(f'assets/sounds/hitmarkers/{cfg['sounds']['hitMarkers']['hit']}')
                                if cfgHitMarkersKillSound:
                                    sound(f'assets/sounds/hitmarkers/{cfg['sounds']['hitMarkers']['kill']}')

                        if cfgKillCount:
                            kills += 1
                            if kills == 1:
                                print(f'First blood! {("☆" * kills)}\n')
                                if cfgKillCountSound:
                                    sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][1]}')
                            elif kills == 2:
                                print(f'Double kill! {("☆" * kills)}\n')
                                if cfgKillCountSound:
                                    sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][2]}')
                            elif kills == 3:
                                print(f'Triple kill! {("☆" * kills)}\n')
                                if cfgKillCountSound:
                                    sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][3]}')
                            elif kills == 4:
                                print(f'Mega kill! {("☆" * kills)}\n')
                                if cfgKillCountSound:
                                    sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][4]}')
                            elif kills == 5:
                                print(f'Monster kill! {("☆" * kills)}\n')
                                if cfgKillCountSound:
                                    sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][5]}')
                            else:
                                if randomStepKCSound == 0:  # 6
                                    print(f'Ultra kill! {("☆" * kills)}\n')
                                    if cfgKillCountSound:
                                        sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][6]}')
                                    randomStepKCSound = randomStepKCSound + 1
                                elif randomStepKCSound == 1:  # 7
                                    print(f'Killing spree! {kills}x ☆\n')
                                    if cfgKillCountSound:
                                        sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][7]}')
                                    randomStepKCSound = randomStepKCSound + 1
                                elif randomStepKCSound == 2:  # 8
                                    print(f'Rampage! {kills}x ☆\n')
                                    if cfgKillCountSound:
                                        sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][8]}')
                                    randomStepKCSound = randomStepKCSound + 1
                                elif randomStepKCSound == 3:  # 9
                                    print(f'Ownage! {kills}x ☆\n')
                                    if cfgKillCountSound:
                                        sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][9]}')
                                    randomStepKCSound = randomStepKCSound + 1
                                elif randomStepKCSound == 4:  # 10
                                    print(f'Godlike! {kills}x ☆\n')
                                    if cfgKillCountSound:
                                        sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][10]}')
                                    randomStepKCSound = randomStepKCSound + 1
                                elif randomStepKCSound == 5:  # 11
                                    print(f'Unstoppable! {kills}x ☆\n')
                                    if cfgKillCountSound:
                                        sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][11]}')
                                    randomStepKCSound = randomStepKCSound + 1
                                elif randomStepKCSound == 6:  # 12
                                    print(f'Dominating! {kills}x ☆\n')
                                    if cfgKillCountSound:
                                        sound(f'assets/sounds/killcount/{cfg['sounds']['killCount'][12]}')
                                    randomStepKCSound = 1

                    elif healthID != 100:
                        if cfgHitMarkers:
                            print(f'Hit! {healthID}♡')
                            if cfgHitMarkersRender and scoped:
                                simage.show('assets/images/hitmarkers/hit.png', duration=cfgHMTimeHit,
                                            sizex=cfgHMScopeSizeHit, sizey=cfgHMScopeSizeHit)
                            elif cfgHitMarkersRender and not scoped:
                                simage.show('assets/images/hitmarkers/hit.png', position='right', duration=cfgHMTimeHit,
                                            sizex=cfgHMSizeHit, sizey=cfgHMSizeHit)
                            if cfgHitMarkersSound:
                                sound(f'assets/sounds/hitmarkers/{cfg['sounds']['hitMarkers']['hit']}')
                previousHealth = healthID  # Update previous health

            # Update lastIndex and lastIndexTime
            lastIndex = entIndex
            lastIndexTime = time.time()

        if autoJump:
            if ctypes.windll.user32.GetAsyncKeyState(0x20):  # Space
                if onGround == 65665 or onGround == 65667:
                    if not doubledJumpCheck and autoJumpSound:
                        sound(f'assets/sounds/{cfg["sounds"]["autoJump"]["jump"]}')
                        doubledJumpCheck = True
                    pm.write_int(client + __jump__, 65537)
                    time.sleep(0.0265)
                    pm.write_int(client + __jump__, 16777472)
                    time.sleep(0.0265)
                else:
                    doubledJumpCheck = False

        try:
            time.sleep(0.001)  # Sleep to reduce CPU load
        except KeyboardInterrupt:  # On program exit
            print('\nProgram terminated. Thanks for using!')
            exit(0)

thread = threading.Thread(target=main)
thread.daemon = True  # Allow the thread to exit when the main program exits
thread.start()

simage.overlay()  # Start overlay