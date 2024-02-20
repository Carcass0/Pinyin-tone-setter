from json import dump, load
from os import path

from psutil import process_iter
from pynput.keyboard import Listener
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QWidget,
    QSystemTrayIcon,
    QApplication,
    QMenu,
)

from alreadyRunning import Ui_ReplacementDialog
from input_handler import ToneListener
from dialog import Ui_Dialog
from utils import update_sequence
from constants import LANGUAGES


def resource_path(relative_path) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)


class SettingsDialog(QDialog):

    def __init__(self, desired_keyboard: str, stop_hotkeys: list[str]):
        super(SettingsDialog, self).__init__()
        self.main_listener: None|ToneListener = None
        self.desired_keyboard = desired_keyboard
        self.stop_hotkeys = stop_hotkeys
        self.setWindowIcon(QIcon(resource_path("Icon.ico")))
        self.hotkey_recording_status = False
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        for number, name in LANGUAGES.items():
            self.ui.language_box.addItem(name, number)
        self.ui.language_box.setCurrentIndex(list(LANGUAGES).index(self.desired_keyboard))
        self.ui.language_box.setFocus()
        self.ui.shortcut_edit.setText(f"{self.stop_hotkeys[0]}+{self.stop_hotkeys[1]}")
        self.ui.shortcut_edit.setReadOnly(True)
        self.ui.confirm_button.clicked.connect(lambda: self.confirm_input())
        self.ui.record_button.clicked.connect(
            lambda: self.start_stop_hotkey_recording()
        )
        self.resize(QWidget.minimumSizeHint(self))

    def start_stop_hotkey_recording(self) -> None:

        def record_keys(window: SettingsDialog, key, key_sequence) -> None:
            update_sequence(key, key_sequence)
            window.ui.shortcut_edit.setText("")
            window.ui.shortcut_edit.setText("+".join(x for x in key_sequence))

        def assign_hotkey_listener(window: SettingsDialog, key_sequence) -> Listener:
            listener = Listener(
                on_press=lambda pressed: record_keys(window, pressed, key_sequence)
            )
            listener.start()
            return listener

        if not self.hotkey_recording_status:
            self.ui.record_button.setText("Stop recording")
            self.ui.shortcut_edit.setFocus()
            self.hotkey_recording_status = not self.hotkey_recording_status
            key_sequence: list[str] = ["", ""]
            self.hotkey_listener = assign_hotkey_listener(self, key_sequence)
            return
        self.hotkey_listener.stop()
        self.ui.record_button.setText("Start recording")
        try:
            self.stop_hotkeys = self.ui.shortcut_edit.text().split("+")
        except:
            self.stop_hotkeys = ["alt_l", "alt_gr"]

    def confirm_input(self) -> None:
        if self.ui.language_box.currentData():
            self.main_listener = ToneListener(desired_keyboard=self.ui.language_box.currentData(), stop_hotkeys=self.stop_hotkeys)
            new_settings = {"keyboard": self.ui.language_box.currentData(), "stoppage-hotkey": self.stop_hotkeys}
        else:
            if self.ui.language_box.currentText() in LANGUAGES.values():
                kb = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(self.ui.language_box.currentText())]
                self.main_listener = ToneListener(desired_keyboard=kb, stop_hotkeys=self.stop_hotkeys)
                new_settings = {"keyboard": kb, "stoppage-hotkey": self.stop_hotkeys}
            else:
                self.main_listener = ToneListener(desired_keyboard="0x804", stop_hotkeys=self.stop_hotkeys)
                new_settings = {"keyboard": "0x804", "stoppage-hotkey": self.stop_hotkeys}
        with open("pinyin-settings.json", "w") as file:
            dump(new_settings, file)
        self.main_listener.listener.start()
        self.close()


class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon: QIcon, app: QApplication, window: SettingsDialog):
        super().__init__()
        self.window = window
        self.setIcon(icon)
        self.show()
        menu = QMenu()
        self.quit = QAction("Quit")
        self.quit.triggered.connect(app.quit)
        self.showMenu = QAction("Show menu")
        self.showMenu.triggered.connect(lambda: show_menu(self.window))
        menu.addAction(self.showMenu)
        menu.addAction(self.quit)
        self.setContextMenu(menu)


class AlreadyRunningDialog(QDialog):
    
    def __init__(self, icon):
        super(AlreadyRunningDialog, self).__init__()
        self.ui = Ui_ReplacementDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(icon)


def show_menu(window: SettingsDialog) -> None:
    if window.main_listener is not None:
        window.main_listener.listener.stop()
    window.show()


def startup_main_app() -> None:
    if path.isfile("pinyin-settings.json"):
        with open("pinyin-settings.json", "r") as f:
            user_settings: dict[str, str] = load(f)
        if user_settings["keyboard"] is None: #likely unneeded as of 15.02.2024; kept for unforeseen circumstances
            desired_keyboard = "0x804"   
        else:
            desired_keyboard = user_settings["keyboard"]   
        stop_hotkeys = list(user_settings["stoppage-hotkey"])
    else:
        desired_keyboard = "0x804"
        stop_hotkeys = ["alt_l", "alt_gr"]
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = SettingsDialog(desired_keyboard, stop_hotkeys)
    window.show()
    tray_icon = SystemTrayIcon(QIcon(resource_path("Icon.ico")), app, window)
    app.exec()


def show_replacement_dialog() -> None:
    app = QApplication([])
    dialog = AlreadyRunningDialog(QIcon(resource_path("Icon.ico")))
    dialog.show()
    app.exec()


if __name__ == "__main__":
    running = False
    counter = 0
    for process in process_iter(['name']):
        if process.name() == 'Pinyin tones.exe':
            if counter == 2:
                running = True
                show_replacement_dialog()
                break
            else:
                counter = counter + 1
    if not running:
        startup_main_app()
