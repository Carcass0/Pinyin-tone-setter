from json import dump, load
from os import path

from pynput.keyboard import Listener
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QWidget,
    QSystemTrayIcon,
    QApplication,
    QMenu,
)

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

    def __init__(self):
        super(SettingsDialog, self).__init__()
        self.setWindowIcon(QIcon(resource_path("Icon.ico")))
        self.hotkey_recording_status = False
        self.hotkeys = main_listener.stop_hotkeys
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        for number, name in LANGUAGES.items():
            self.ui.language_box.addItem(name, number)
        self.ui.language_box.setCurrentIndex(list(LANGUAGES).index(main_listener.desired_keyboard))
        self.ui.language_box.setFocus()
        self.ui.shortcut_edit.setText(f"{self.hotkeys[0]}+{self.hotkeys[1]}")
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
        self.hotkeys = self.ui.shortcut_edit.text().split("+")

    def confirm_input(self) -> None:
        if self.ui.language_box.currentData():
            main_listener.update_settings(keyboard=self.ui.language_box.currentData(), hotkeys=self.hotkeys)
        else:
            main_listener.update_settings(keyboard=list(LANGUAGES.keys())[list(LANGUAGES.values()).index(self.ui.language_box.currentData())], hotkeys=self.hotkeys)
        new_settings = {"keyboard": self.ui.language_box.currentData(), "stoppage-hotkey": self.hotkeys}
        print(self.ui.language_box.currentText())
        with open("pinyin-settings.json", "w") as file:
            dump(new_settings, file)
        main_listener.listener.start()
        self.close()


class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon: QIcon, app: QApplication, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIcon(icon)
        self.show()
        menu = QMenu()
        self.quit = QAction("Quit")
        self.quit.triggered.connect(app.quit)
        menu.addAction(self.quit)
        self.setContextMenu(menu)


if __name__ == "__main__":
    if path.isfile("pinyin-settings.json"):
        with open("pinyin-settings.json", "r") as f:
            user_settings: dict[str, str] = load(f)
        if user_settings["keyboard"] is not None:   #likely unneeded as of 15.02.2024; kept for unforeseen circumstances
            desired_keyboard = user_settings["keyboard"]
        else:
            desired_keyboard = "0x804"    
        stop_hotkeys = user_settings["stoppage-hotkey"]
    else:
        desired_keyboard = "0x804"
        stop_hotkeys = ["alt_l", "alt_gr"]
    main_listener = ToneListener(desired_keyboard, stop_hotkeys)
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = SettingsDialog()
    window.show()
    tray_icon = SystemTrayIcon(QIcon(resource_path("Icon.ico")), app)
    app.exec()
