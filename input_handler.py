import ctypes
from pynput.keyboard import Key, Controller, Listener


ACCENTED_SYMBOLS = {
    "a": ["ā", "á", "ǎ", "à"],
    "A": ["Ā", "Á", "Ǎ", "À"],
    "e": ["ē", "é", "ě", "è"],
    "E": ["Ē", "É", "Ě", "È"],
    "i": ["ī", "í", "ǐ", "ì"],
    "I": ["Ī", "Í", "Ǐ", "Ì"],
    "o": ["ō", "ó", "ǒ", "ò"],
    "O": ["Ō", "Ó", "Ǒ", "Ò"],
    "u": ["ū", "ú", "ǔ", "ù", "ü", "ǖ", "ǘ", "ǚ", "ǜ"],
    "U": ["Ū", "Ú", "Ǔ", "Ù", "Ü", "Ǖ", "Ǘ", "Ǚ", "Ǜ"],
}
CHANGE_PROVOKING_KEYS = {
    "alt",
    "alt_l",
    "alt_r",
    "alt_gr",
    "ctrl",
    "ctrl_l",
    "ctrl_r",
    "shift",
    "shift_l",
    "shift_r",
}
desired_keyboard = "0x804"
stoppage_hotkey = ["alt_l", "alt_gr"]


def current_keyboard_language() -> str:
    """Get current keyboard language.
    source:
    https://stackoverflow.com/questions/42047253/how-to-detect-current-keyboard-language-in-python
    """
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    handle = user32.GetForegroundWindow()
    threadid = user32.GetWindowThreadProcessId(handle, 0)
    layout_id = user32.GetKeyboardLayout(threadid)
    # Extracting the keyboard language id from the keyboard layout id
    language_id = layout_id & (2**16 - 1)
    return hex(language_id)


def update_sequence(key: Key, key_sequence: list[str]) -> None:
    """Listens to and records all button presses"""

    def replace_sequence(target_list: list[str], value: str) -> None:
        """Save 2 last pressed keys to provided list"""
        target_list[0] = target_list[1]
        target_list[1] = value

    if hasattr(key, "char"):
        if hasattr(key, "vk") and key.vk is not None and key.vk >= 96 and key.vk <= 105:  # type: ignore
            """For some reason, char attribute is None for NumPad numbers.
            This corrects it using their virutal key numbers."""
            key.char = str(key.vk - 96)  # type: ignore
        replace_sequence(key_sequence, key.char)  # type: ignore
    else:
        replace_sequence(key_sequence, key.name)


def update_state(
    state_list: list[int],
    skip_count: int,
    desired_state: bool = False,
    switch: bool = False,
) -> None:
    """Tells the on_press processor to skip
    the next skip_count presses.
    Used to ignore app-issued presses."""
    if switch:
        state_list[0] = not state_list[0]
    else:
        state_list[0] = desired_state
    if skip_count < 0 and skip_count == state_list[1]:
        state_list[1] = 0
    else:
        state_list[1] = skip_count


def main_processor(
    key: Key, keyboard: Controller, key_sequence: list[str], processing_state: list[int]
) -> None:
    update_sequence(key, key_sequence)
    if set(key_sequence).intersection(CHANGE_PROVOKING_KEYS):
        """Responding to potential change in keyboard language.
        Aims to only process events if desired language is being used."""
        if processing_state[1] < 0:
            pass
        elif (
            not processing_state[0] and current_keyboard_language() == desired_keyboard
        ):
            update_state(processing_state, 0, True)
        elif processing_state[0] and current_keyboard_language() != desired_keyboard:
            update_state(processing_state, 0, False)

    if len(set(key_sequence).intersection(stoppage_hotkey)) == 2 or (
        len(set(key_sequence).intersection(stoppage_hotkey)) == 1
        and stoppage_hotkey.count("") == 1
    ):
        """Handling turning the processing on and off with a hotkey.
        The app only supports stoppage hotkeys with length of 2.
        Therefore a intersection of length of 2 constitutes a match.
        -1 is only used here, therefore disallowing hotkey
        sleep mode from being overridden"""
        update_state(processing_state, -1, switch=True)

    if not processing_state[0]:
        """Handling early exit due to wrong keyboard being selected or a set skip counter"""
        if processing_state[1] > 0:
            if processing_state[1] == 1:
                update_state(
                    state_list=processing_state, skip_count=0, desired_state=True
                )
                return True  # type: ignore
            update_state(
                state_list=processing_state, skip_count=processing_state[1] - 1
            )
        return True  # type: ignore

    if (
        (key_sequence[1].isnumeric())
        and (
            key_sequence[0] in ["a", "A", "e", "E", "i", "I", "o", "O"]
            and int(key_sequence[1]) in range(1, 5)
        )
        or (key_sequence[0] in ["u", "U"] and int(key_sequence[1]) in range(1, 10))
    ):
        """Replace vowels with their required accented version"""
        update_state(processing_state, 3, False)
        keyboard.press(Key.backspace)
        keyboard.release(Key.backspace)
        keyboard.press(Key.backspace)
        keyboard.release(Key.backspace)
        keyboard.press(ACCENTED_SYMBOLS[key_sequence[0]][int(key_sequence[1]) - 1])
        keyboard.release(ACCENTED_SYMBOLS[key_sequence[0]][int(key_sequence[1]) - 1])


def setup_listener():
    keyboard = Controller()
    key_sequence: list[str] = ["", ""]
    if current_keyboard_language() == desired_keyboard:
        processing_state = [True, 0]
    else:
        processing_state = [False, 0]
    on_press_action = lambda pressed: main_processor(
        key=pressed,
        keyboard=keyboard,
        key_sequence=key_sequence,
        processing_state=processing_state,
    )
    listener = Listener(on_press=on_press_action)
    return listener


if __name__ == "__main__":
    lst = setup_listener()
    lst.start()
    lst.join()
