import pymem # библиотека для работы с памятью
import time # библиотека для работы с временем

pm = pymem.Pymem('cs2.exe') # процесс Counter-Strike 2
client = pymem.process.module_from_name(pm.process_handle, 'client.dll').lpBaseOfDll # .dll файл с оффсетами

dwLocalPlayerPawn = 0x17C17F0 # longlong
dwEntityList = 0x1954568 # longlong
dwGameRules = 0x19B1558 # longlong

__gamepaused__ = 0x4C # bool
__shoot__ = 0x17BA020 # int
__health__ = 0x324 # int
__index__ = 0x13A8 # int
__team__ = 0x3C3 # int

previous_health = None  # Переменная для хранения предыдущего значения здоровья

# Приветствие
print('꧁ ༺ HITMOD ༻ ꧂') #1.0.4
print('    От watakaka\n')

while True:
    # Классы
    entityList = pm.read_longlong(client + dwEntityList) # Класс листа сущностей
    localPlayerPawn = pm.read_longlong(client + dwLocalPlayerPawn) # Класс пешки игрока
    gameRules = pm.read_longlong(client + dwGameRules) # Класс правил сервера (матча)

    # Переменные
    entIndex = pm.read_int(localPlayerPawn + __index__) # Index игрока на котором прицел
    gamePaused = pm.read_bool(dwGameRules + __gamepaused__) # Остановлен-ли сервер
    team = pm.read_int(localPlayerPawn + __team__) # Команда за которую играет игрок
    shoot = pm.read_int(client + __shoot__) # Левая кнопка мыши

    try:
            # Если есть игрок перед прицелом (индекс сущности)
            if shoot == 65537 and entIndex != -1: # Если ЛКМ и индекс сущности не -1 (то-есть воздух)
                # Получаем контроллер из индекса сущности
                listEntry = pm.read_longlong(entityList + 8 * ((entIndex & 0x7FF) >> 9) + 16)
                # Получаем пешку игрока из контроллера индекса сущности
                currentPawn = pm.read_longlong(listEntry + 120 * (entIndex & 0x1FF))

                # Получаем здоровье и команду
                healthID = pm.read_int(currentPawn + __health__)
                teamID = pm.read_int(currentPawn + __team__)

                # Основной скрипт
                # Урон/убийство
                if team == 2 and teamID == 3 or team == 3 and teamID == 2:  # Проверка команды
                    if previous_health is not None and healthID != previous_health:  # Проверяем изменение здоровья
                        if healthID == 0:
                            print('Убийство!')
                        else:
                            print(f'Попадание! {healthID}♡')
                    previous_health = healthID  # Обновляем предыдущий показатель здоровья

                # Дружественный огонь вкл/выкл
                elif team == 2 and teamID == 2 or team == 3 and teamID == 3:
                    if friendlyfire:
                        if previous_health is not None and healthID != previous_health:  # Проверяем изменение здоровья
                            if healthID == 0:
                                print('Союзник: Убийство!')
                            else:
                                print(f'Союзник: Попадание! {healthID}♡')
                        previous_health = healthID  # Обновляем предыдущий показатель здоровья

    except Exception as e: # В случае ошибки
        print(f"Ошибка: {e}")

    try:
        time.sleep(0.001)  # Задержка в цикле для снижения нагрузки на CPU
    except KeyboardInterrupt: # В случае закрытия программы
        print('\nОкончание работы программы.')
        exit(0)
