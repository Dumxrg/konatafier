#hey person reading this code, have a good day :)
# thank u mate, u too :3
import os
import winreg
import ctypes
import sys
import time
import json
import msvcrt
from datetime import datetime
    
test1 = (
    'powershell -Command "Add-Type -AssemblyName PresentationFramework; '
    '[System.Windows.MessageBox]::Show(\'This is a test\', \'Test\', '
    '[System.Windows.MessageBoxButton]::OK, '
    '[System.Windows.MessageBoxImage]::Error)"'
    )
test2 = (
    'powershell -Command "Add-Type -AssemblyName PresentationFramework; '
    '[System.Windows.MessageBox]::Show(\'This is a test\', \'Test\', '
    '[System.Windows.MessageBoxButton]::OK, '
    '[System.Windows.MessageBoxImage]::Information)"'
)

# Sound event mappings
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
translations = {}
available_languages = []

def discover_languages():
    """Find all available language JSON files in the JSON directory"""
    global available_languages
    available_languages = []
    json_dir = os.path.join(BASE_DIR, "..", "JSON")
    
    try:
        if os.path.exists(json_dir):
            for file in os.listdir(json_dir):
                if file.endswith('.json') and file != 'template.json':
                    lang_code = file.split('.')[0]
                    available_languages.append(lang_code)
            return True
        else:
            print(f"JSON directory not found: {json_dir}")
            return False
    except Exception as e:
        print(f"Error discovering languages: {e}")
        return False

def get_language_name(lang_code):
    """Return the human-readable name of a language code"""
    language_names = {
        "en": "English",
        "ru": "Русский",
        # Add more languages as they become available
    }
    return language_names.get(lang_code, lang_code.upper())

def load_translations(lang="en"):
    """Load translations from the JSON file based on language selection"""
    global translations
    json_path = os.path.join(BASE_DIR, "..", "JSON", f"{lang}.json")
    
    try:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                translations = json.load(f)
            return True
        else:
            print(f"Translation file not found: {json_path}")
            return False
    except Exception as e:
        print(f"Error loading translations: {e}")
        return False

def get_translation(category, key, default=None):
    """Get a translation by category and key, with fallback to default value"""
    try:
        return translations.get(category, {}).get(key, default)
    except:
        return default

def toggle_language():
    """Cycle through available languages"""
    global language
    
    # If we have no discovered languages, try to discover them
    if not available_languages:
        discover_languages()
    
    # If still no languages found, fallback to just en/ru toggle
    if not available_languages:
        language = "en" if language == "ru" else "ru"
    else:
        # Find current language index
        try:
            current_index = available_languages.index(language)
            # Set to next language in the list, or back to first if at end
            next_index = (current_index + 1) % len(available_languages)
            language = available_languages[next_index]
        except ValueError:
            # If current language not in list, default to first available
            language = available_languages[0] if available_languages else "en"
    
    load_translations(language)

def language_menu():
    """Menu for selecting a language from available options"""
    global language
    
    while True:
        print("\033[H\033[J")
        print("Language Selection / Выбор языка\n")
        
        # Discover available languages
        discover_languages()
        
        if not available_languages:
            print("No language files found! / Языковые файлы не найдены!")
            input("\nPress Enter to continue... / Нажмите Enter для продолжения...")
            return
        
        # Display available languages
        for i, lang in enumerate(available_languages, 1):
            current = " (current)" if lang == language else ""
            print(f"{i}) {get_language_name(lang)}{current}")
        
        print(f"{len(available_languages) + 1}) Back to main menu / Вернуться в главное меню")
        
        choice = input("\nSelect language / Выберите язык (1-{}): ".format(len(available_languages) + 1))
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_languages):
                language = available_languages[choice_num - 1]
                load_translations(language)
                print(f"\nLanguage changed to {get_language_name(language)} / Язык изменен на {get_language_name(language)}")
                input("\nPress Enter to continue... / Нажмите Enter для продолжения...")
                return
            elif choice_num == len(available_languages) + 1:
                return
        except ValueError:
            pass
        
        print("\nInvalid choice / Неверный выбор")
        input("\nPress Enter to continue... / Нажмите Enter для продолжения...")

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
        print(get_translation("create_backup", "backup_created", ":D Backup created: ") + backup_path)
        return True
    except Exception as e:
        print(get_translation("create_backup", "backup_error", ":( Error creating backup: ") + str(e))
        return False

def backup_menu():
    while True:
        print("\033[H\033[J")
        print(get_translation("backup_menu", "backup_menu", "Backup Menu\n"))
        print(get_translation("backup_menu", "option_1", "1) Create backup"))
        print(get_translation("backup_menu", "option_2", "2) Back to main menu"))
        
        choice = input("\n" + get_translation("main_menu", "choose_option", "Choose an option (1-2): "))
        
        if choice == "1":
            print("\n" + get_translation("backup_menu", "choices", {}).get("choice_1", 
                          "(⌐■_■) Enter filename (no spaces!) or press Enter for automatic name:"))
            backup_name = input().strip()
            if backup_name:
                if ' ' in backup_name:
                    print(get_translation("backup_menu", "choices", {}).get("space_in_filename", 
                          "[!] :( Filename should not contain spaces!"))
                    input("\n" + get_translation("exceptions", "continue", "Press Enter to continue..."))
                    continue
                backup_name += '.json'
            else:
                backup_name = None
            
            if create_backup(backup_name):
                input("\n" + get_translation("exceptions", "continue", "Press Enter to continue..."))
        elif choice == "2":
            break

def toggle_logon_sounds(enable: bool):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Authentication\LogonUI\BootAnimation"
    try:
        reg_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        winreg.SetValueEx(reg_key, "DisableStartupSound", 0, winreg.REG_DWORD, 0 if enable else 1)
        winreg.CloseKey(reg_key)
        status_msg = "Logon sound enabled" if enable else "Logon sound disabled"
        print(status_msg)
    except Exception as e:
        print(":( Failed to change parameter:", e)

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
                    print(f"Error setting {path}: {e}")
            
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
                print(f"Error getting current scheme: {e}")
                current_scheme = ".None"
            
            if current_scheme != ".None":
                scheme_path = fr"AppEvents\Schemes\{current_scheme}\.Default\Notification\.Current"
                try:
                    reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, scheme_path)
                    winreg.SetValueEx(reg_key, "", 0, winreg.REG_SZ, wav_path)
                    winreg.CloseKey(reg_key)
                except Exception as e:
                    print(f"Error setting sound for scheme {current_scheme}: {e}")
            
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
        event_name = EVENTS.get(event, event) if language == "ru" else EVENTS_EN.get(event, event)
        print(f":( {event_name} — error: {e}")
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
        print(get_translation("load_backup_sounds", "backup_error", ":( Backup not found, cannot restore."))
        return
    
    with open(BACKUP_PATH, "r", encoding="utf-8") as f:
        backup = json.load(f)
    
    for event_key, value in backup.items():
        set_event_sound(event_key, value)
    
    print(get_translation("load_backup_sounds", "restored_sound", "\n:) Sounds restored from backup"))
    input("\n" + get_translation("exceptions", "continue", "Press Enter to return to menu..."))

def apply_custom_sounds():
    print(get_translation("applying_custom_sounds", "applying_custom_sounds", "\nApplying custom sounds...\n"))
    
    success = True
    event_display = EVENTS if language == "ru" else EVENTS_EN
    
    for event_key, display_name in event_display.items():
        wav_path = os.path.join(BASE_DIR, "..", "assets", "audio", f"{event_key}.wav")
        print(get_translation("applying_custom_sounds", "checking_file", "\nChecking file: ") + wav_path)
        if os.path.isfile(wav_path):
            print(get_translation("applying_custom_sounds", "file_found", "File found, trying to install..."))
            if set_event_sound(event_key, wav_path):
                print(f":) {display_name}" + get_translation("applying_custom_sounds", "success", " — success"))
            else:
                success = False
                print(f":( {display_name}" + get_translation("applying_custom_sounds", "not_success", " — error"))
        else:
            success = False
            print(f":\ {display_name}" + get_translation("applying_custom_sounds", "not_found", " — file not found"))
    
    refresh_sound_scheme()

    if success:
        print(get_translation("applying_custom_sounds", "files_replaced", "\n:D All sounds replaced successfully!"))
    else:
        print("\n:( Not all sounds were replaced")
    
    input("\n" + get_translation("exceptions", "continue", "Press Enter to return to menu..."))

def is_admin():
    # can u please remove this, is not necessary to run as admin, i didnt need in my machine
    return True

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)

def show_admin_alert():
    print(":( Error: This program requires administrator privileges. \nPlease run the program as administrator")
    time.sleep(999999)

def show_warning():
    print("\033[H\033[J")
    warning_msg = get_translation("greetings", "welcome_text", 
                                 "Running KONATAFIER v0.2 by erkv! By proceeding, you confirm that you have read our LICENSE.\nAvailable in\nhttps://github.com/er1k0v/konatafier/blob/main/LICENSE")
    print(warning_msg) 
    print("\nPress Enter to continue or Esc to exit...")
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
        print(get_translation("main_menu", "welcome", "Welcome to the Konatafier!"))
        print(get_translation("main_menu", "option_1", "1) Change system sounds"))
        print(get_translation("main_menu", "option_2", "2) Reset"))
        print(get_translation("main_menu", "option_3", "3) Logon sound settings"))
        print(get_translation("main_menu", "option_4", "4) Backup"))
        print(get_translation("main_menu", "option_5", "5) Change language"))
        print(get_translation("main_menu", "option_6", "6) Test sounds"))
        print(get_translation("main_menu", "option_7", "7) Exit"))

        choice = input("\n" + get_translation("main_menu", "choose_option", "Choose an option (1-7): "))

        if choice == "1":
            change_sounds()
        elif choice == "2":
            reset_sounds()
        elif choice == "3":
            toggle_logon_sounds_menu()
        elif choice == "4":
            backup_menu()
        elif choice == "5":
            language_menu()
        elif choice == "6":
            os.system(test1)
            os.system(test2)
            input("\n" + get_translation("exceptions", "continue", "Press Enter to continue..."))
        elif choice == "7":
            sys.exit()
        else:
            print(get_translation("exceptions", "error", ":( Invalid choice."))
            input("\n" + get_translation("exceptions", "continue", "Press Enter to continue..."))

def change_sounds():
    print("\033[H\033[J")
    confirm = input(get_translation("change_sounds", "change", 
                   "Are you sure you want to make you PC awesome (change the sounds)? (y/n): ")).lower()
    if confirm == "y":
        apply_custom_sounds()
    main_menu()

def reset_sounds():
    print("\033[H\033[J")
    confirm = input(get_translation("change_sounds", "reset", 
                   "Are you sure you want to make your PC serious (restore sounds?) (y/n): ")).lower()
    if confirm == "y":
        load_backup_sounds()
    main_menu()

def toggle_logon_sounds_menu():
    while True:
        print("\033[H\033[J")
        enabled = get_logon_sound_state()
        status = "ON :)" if enabled else "OFF :("
        print(get_translation("toggle_logon_sounds", "enabled", "Logon Sound Settings") + "\n")
        print(f"Logon sound: {status}")
        print("1) Toggle logon sound")
        print("2) Back to main menu")
        choice = input("\n" + get_translation("main_menu", "choose_option", "Choose an option (1-2): "))

        if choice == "1":
            toggle_logon_sounds(not enabled)
            input("\n" + get_translation("exceptions", "continue", "Press Enter to continue..."))
        elif choice == "2":
            break

def main():
    os.system("title Konatafier")
    
    # Discover available languages
    discover_languages()
    
    # Try to load system language or default to English
    if 'LANG' in os.environ:
        system_lang = os.environ['LANG'].split('_')[0]
        if system_lang in available_languages:
            global language
            language = system_lang
    
    # Load translations
    load_translations(language)
    
    if not is_admin():
        show_admin_alert()
        run_as_admin()
    else:
        show_warning()
        main_menu()

if __name__ == "__main__":
    main()