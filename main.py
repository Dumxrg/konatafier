#hey person reading this code, have a good day :)
import os
import winreg
import ctypes
import sys
import time
import json
import msvcrt
from datetime import datetime

EVENTS = {
    "WindowsLogon": "Запуск Windows",
    "SystemExit": "Завершение работы Windows",
    "SystemExclamation": "Восклицание",
    "SystemAsterisk": "Звездочка",
    "SystemHand": "Критическая ошибка",
    "SystemNotification": "Системное уведомление",
    "Notification": "Уведомление",
    "Default": "Стандартный звук",
    "WindowsUAC": "Контроль учетных записей"
}

EVENTS_EN = {
    "WindowsLogon": "Windows Logon",
    "SystemExit": "System Exit",
    "SystemExclamation": "Exclamation",
    "SystemAsterisk": "Asterisk",
    "SystemHand": "Critical Error",
    "SystemNotification": "System Notification",
    "Notification": "Notification",
    "Default": "Default Sound",
    "WindowsUAC": "Windows UAC"
}

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BACKUP_PATH = os.path.join(BASE_DIR, "firstbackup.json")
language = "ru"

def toggle_language():
    global language
    language = "en" if language == "ru" else "ru"

def create_backup(backup_name=None):
    if backup_name is None:
        backup_name = datetime.now().strftime("%d%m%Y_%H%M") + ".json"
    else:
        if not backup_name.lower().endswith('.json'):
            backup_name += '.json'
    
    backup_path = os.path.join(BASE_DIR, backup_name)
    
    backup = {}
    for event_key in EVENTS:
        if event_key == "WindowsUAC":
            key_path = r"AppEvents\Schemes\Apps\Explorer\WindowsUAC\.Current"
        else:
            key_path = fr"AppEvents\Schemes\Apps\.Default\{event_key}\.Current"
        
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
            value, _ = winreg.QueryValueEx(reg_key, "")
            backup[event_key] = value
            winreg.CloseKey(reg_key)
        except:
            backup[event_key] = ""
    
    try:
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup, f)
        print(f":) Резервная копия создана: {backup_path}" if language == 'ru' else f":D Backup created: {backup_path}")
        return True
    except Exception as e:
        print(f":( Ошибка при создании резервной копии: {e}" if language == 'ru' else f":( Error creating backup: {e}")
        return False

def backup_menu():
    while True:
        print("\033[H\033[J")
        print("Меню резервного копирования\n" if language == "ru" else "Backup Menu\n")
        print("1) Создать резервную копию" if language == "ru" else "1) Create backup")
        print("2) Вернуться в главное меню" if language == "ru" else "2) Back to main menu")
        
        choice = input("\nВыберите действие (1-2): " if language == "ru" else "\nChoose an option (1-2): ")
        
        if choice == "1":
            print("\n" + ("(⌐■_■) Введите имя файла (без пробелов!) или нажмите Enter для автоматического имени:" if language == "ru" else "(⌐■_■) Enter filename (no spaces!) or press Enter for automatic name:"))
            backup_name = input().strip()
            if backup_name:
                if ' ' in backup_name:
                    print("[!] :( Имя файла не должно содержать пробелов!" if language == "ru" else "[!] :( Filename should not contain spaces!")
                    input("\nНажмите Enter для продолжения..." if language == "ru" else "\nPress Enter to continue...")
                    continue
                backup_name += '.json'
            else:
                backup_name = None
            
            if create_backup(backup_name):
                input("\n" + ("Нажмите Enter для продолжения..." if language == "ru" else "Press Enter to continue..."))
        elif choice == "2":
            break

def toggle_logon_sounds(enable: bool):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Authentication\LogonUI\BootAnimation"
    try:
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        winreg.SetValueEx(reg_key, "DisableStartupSound", 0, winreg.REG_DWORD, 0 if enable else 1)
        winreg.CloseKey(reg_key)
        print(f"Звук входа {'включён' if enable else 'отключён'}" if language == "ru" else f"Logon sound {'enabled' if enable else 'disabled'}")
    except Exception as e:
        print(":( Не удалось изменить параметр:", e)

def get_logon_sound_state():
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Authentication\LogonUI\BootAnimation"
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        value, _ = winreg.QueryValueEx(reg_key, "DisableStartupSound")
        winreg.CloseKey(reg_key)
        return value == 0
    except:
        return None

def set_event_sound(event, wav_path):
    try:
        if event == "Default":
            key_path = r"AppEvents\Schemes\Apps\.Default\.Default\.Current"
        elif event == "WindowsUAC":
            base_path = r"AppEvents\Schemes\Apps\Explorer\WindowsUAC"
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, base_path)
            
            for path in [base_path + r"\.Current",
                        r"AppEvents\Schemes\Apps\.Default\WindowsUAC\.Current"]:
                try:
                    reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
                    winreg.SetValueEx(reg_key, "", 0, winreg.REG_SZ, wav_path)
                    winreg.CloseKey(reg_key)
                except Exception as e:
                    print(f"Ошибка установки {path}: {e}")
            
            try:
                label_path = r"AppEvents\EventLabels\WindowsUAC"
                reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, label_path)
                winreg.SetValueEx(reg_key, "", 0, winreg.REG_SZ, wav_path)
                winreg.CloseKey(reg_key)
            except:
                pass
            
            return True
        elif event == "Notification":
            key_path = r"AppEvents\Schemes\Apps\.Default\Notification.Default\.Current"
            
            reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(reg_key, "", 0, winreg.REG_SZ, wav_path)
            winreg.CloseKey(reg_key)
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"AppEvents\Schemes") as schemes_key:
                    current_scheme, _ = winreg.QueryValueEx(schemes_key, "")
            except Exception as e:
                print(f"Ошибка получения текущей схемы: {e}")
                current_scheme = ".None"
            
            if current_scheme != ".None":
                scheme_path = fr"AppEvents\Schemes\{current_scheme}\.Default\Notification\.Current"
                try:
                    reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, scheme_path)
                    winreg.SetValueEx(reg_key, "", 0, winreg.REG_SZ, wav_path)
                    winreg.CloseKey(reg_key)
                except Exception as e:
                    print(f"Ошибка установки звука для схемы {current_scheme}: {e}")
            
            known_schemes = ["WindowsDefault", ".None", "WindowsUAC"]
            for scheme in known_schemes:
                scheme_path = fr"AppEvents\Schemes\{scheme}\.Default\Notification\.Current"
                try:
                    reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, scheme_path)
                    winreg.SetValueEx(reg_key, "", 0, winreg.REG_SZ, wav_path)
                    winreg.CloseKey(reg_key)
                except:
                    continue
            
            return True
        else:
            key_path = fr"AppEvents\Schemes\Apps\.Default\{event}\.Current"
        
        reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(reg_key, "", 0, winreg.REG_SZ, wav_path)
        winreg.CloseKey(reg_key)
        
        if event not in ["Default", "WindowsUAC", "Notification"]:
            key_path = fr"AppEvents\EventLabels\{event}"
            reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(reg_key, "", 0, winreg.REG_SZ, wav_path)
            winreg.CloseKey(reg_key)
        
        return True
    except Exception as e:
        print(f":( {EVENTS.get(event, event)} — ошибка: {e}")
        return False

def refresh_sound_scheme():
    try:
        ctypes.windll.user32.PostMessageW(0xFFFF, 0x1C, 0, 0)
        return True
    except:
        return False

def backup_current_sounds():
    return create_backup("firstbackup.json")

def load_backup_sounds():
    if not os.path.isfile(BACKUP_PATH):
        print(":( Бэкап не найден, невозможно восстановить." if language == "ru" else ":( Backup not found, cannot restore.")
        return
    
    with open(BACKUP_PATH, "r", encoding="utf-8") as f:
        backup = json.load(f)
    
    for event_key, value in backup.items():
        set_event_sound(event_key, value)
    
    print("\n:) Звуки восстановлены из резервной копии" if language == "ru" else "\n:) Sounds restored from backup")
    input("\nНажмите Enter для возврата в меню..." if language == "ru" else "\nPress Enter to return to menu...")

def apply_custom_sounds():
    print("\nВыполняется замена звуков...\n" if language == "ru" else "\nApplying custom sounds...\n")
    
    success = True
    
    for event_key, display_name in (EVENTS if language == "ru" else EVENTS_EN).items():
        wav_path = os.path.join(BASE_DIR, f"{event_key}.wav")
        print(f"\nПроверяем файл: {wav_path}" if language == "ru" else f"\nChecking file: {wav_path}")
        if os.path.isfile(wav_path):
            print("Файл найден, пытаемся установить..." if language == "ru" else f"File found, trying to install...")
            if set_event_sound(event_key, wav_path):
                print(f":) {display_name} — успешно" if language == "ru" else f":) {display_name} — success")
            else:
                success = False
                print(f":( {display_name} — ошибка установки" if language == "ru" else f":( {display_name} — error")
        else:
            success = False
            print(f":\ {display_name} — файл не найден" if language == "ru" else f":\ {display_name} — file not found")
    
    refresh_sound_scheme()

    if success:
        print("\n:D Все звуки успешно заменены!" if language == "ru" else "\n:D All sounds replaced successfully!")
    else:
        print("\n:( Не все звуки удалось заменить" if language == "ru" else "\n:( Not all sounds were replaced")
    
    input("\nНажмите Enter для возврата в меню..." if language == "ru" else "\nPress Enter to return to menu...")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)

def show_admin_alert():
    print(":( Ошибка: Для запуска этой программы требуются права администратора.\nПожалуйста, запустите программу от имени администратора" "\n:( Error: This program requires administrator privileges. \nPlease run the program as administrator")
    time.sleep(999999)

def show_warning():
    print("\033[H\033[J")
    warning_msg = """Используя Konatafier, вы понимаете, что доверяете ваш комп этому коду, а как работает этот код знает только Бог.
Программа писалась под Windows 10, и у меня все работает отлично.
Я не знаю как программа может работать на другой винде.
За возможные последствия (смерть вашего любимого хомяка, разбитый экран телефона, 2 по всемирной истории на следующей неделе и так далее) я не отвечаю.

By using Konatafier, you understand that you believe in my coding skills. (i belive in myself btw) 
Konatafier was written for Windows 10, it works perfectly fine on mine PC.
Idk how it will act on Windows 11, 7, 8, etc.
I am not responsible for any possible consequences(death of your beloved hamster, broken screen of your phone, F on a chemistry test next week, etc).

>:3"""
    print(warning_msg)
    print("\nНажмите Enter, чтобы продолжить или Esc для выхода...\nPress Enter to continue or Esc to exit...")
    while True:
        key = msvcrt.getch()
        if key == b'\x1b':
            sys.exit()
        elif key == b'\r':
            break
    
    if not os.path.exists(BACKUP_PATH):
        backup_current_sounds()

def main_menu():
    while True:
        print("\033[H\033[J")
        print("erkv\n")
        print("Добро пожаловать в Konatafier!" if language == "ru" else "Welcome to the Konatafier!")
        print("1) Изменить звуки системы" if language == "ru" else "1) Change system sounds")
        print("2) Вернуть изначальные звуки" if language == "ru" else "2) Reset")
        print("3) Включение/выключение звука входа" if language == "ru" else "3) Logon sound settings")
        print("4) Резервное копирование" if language == "ru" else "4) Backup")
        print("5) Сменить язык/Change language")
        print("6) Выйти" if language == "ru" else "6) Exit")

        choice = input("\nВыберите действие (1-6): " if language == "ru" else "\nChoose an action (1-6): ")

        if choice == "1":
            change_sounds()
        elif choice == "2":
            reset_sounds()
        elif choice == "3":
            toggle_logon_sounds_menu()
        elif choice == "4":
            backup_menu()
        elif choice == "5":
            toggle_language()
        elif choice == "6":
            sys.exit()
        else:
            print(":( Неверный выбор." if language == "ru" else ":( Invalid choice.")
            input("\nНажмите Enter для продолжения..." if language == "ru" else "\nPress Enter to continue...")

def change_sounds():
    print("\033[H\033[J")
    confirm = input("Вы уверены, что хотите сделать свой компьютер крутым (изменить звуки)? (y/n): " if language == "ru" else "Are you sure you want to make you PC awesome (change the sounds)? (y/n): ").lower()
    if confirm == "y":
        apply_custom_sounds()
    main_menu()

def reset_sounds():
    print("\033[H\033[J")
    confirm = input("Вы уверены, что хотите сделать свой компьютер серьезным (восстановить звуки)? (y/n): " if language == "ru" else "Are you sure you want to make your PC serious (restore sounds?) (y/n): ").lower()
    if confirm == "y":
        load_backup_sounds()
    main_menu()

def toggle_logon_sounds_menu():
    while True:
        print("\033[H\033[J")
        enabled = get_logon_sound_state()
        status = "ON :)" if enabled else "OFF :("
        print("Включение/выключение звука входа\n" if language == "ru" else "Logon Sound Settings\n")
        print(f"Звук входа: {status}" if language == "ru" else f"Logon sound: {status}")
        print("1) Включить/выключить звук входа" if language == "ru" else "1) Toggle logon sound")
        print("2) Вернуться обратно" if language == "ru" else "2) Back to main menu")
        choice = input("\nВыберите действие (1-2): " if language == "ru" else "\nChoose an option (1-2): ")

        if choice == "1":
            toggle_logon_sounds(not enabled)
            input("\nНажмите Enter для продолжения..." if language == "ru" else "\nPress Enter to continue...")
        elif choice == "2":
            break

def main():
    os.system("title Konatafier")
    if not is_admin():
        show_admin_alert()
        run_as_admin()
    else:
        show_warning()
        main_menu()

if __name__ == "__main__":
    main()