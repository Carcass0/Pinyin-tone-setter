from pynput import keyboard as kb
import ctypes


STOPPAGE_COMBINATIONS = {
    ("ctrl_l", "1"),
    ("ctrl_l", "2")
}
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
CHANGE_PROVOKING_KEYS = {'alt', 'alt_l', 'alt_r', 'alt_gr', 'ctrl', 'ctrl_l', 'ctrl_r', 'shift', 'shift_l', 'shift_r'}
desired_keyboards = ['0x804']
stoppage_hotkey = ['alt_l', 'alt_gr']


def current_keyboard_language() -> str:
    """
    0x804 - Chinese - People's Republic of China
    0x409 - English - United States
    0x419 - Russian
    """
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    # Get the current active window handle
    handle = user32.GetForegroundWindow()
    # Get the thread id from that window handle
    threadid = user32.GetWindowThreadProcessId(handle, 0)
    # Get the keyboard layout id from the threadid
    layout_id = user32.GetKeyboardLayout(threadid)
    # Extract the keyboard language id from the keyboard layout id
    language_id = layout_id & (2 ** 16 - 1)
    # Convert the keyboard language id from decimal to hexadecimal
    return hex(language_id)


def update_sequence(key: kb.Key, key_sequence: list[str, str]):
    """listens to and records all button presses"""

    def replace_sequence(target_list: list[str, str], value: str) -> None:
        """Save 2 last pressed keys to provided list"""
        target_list[0] = target_list[1]
        target_list[1] = value

    if hasattr(key, "char"):
        if hasattr(key, "vk") and key.vk is not None and key.vk >= 96 and key.vk <= 105:
            """For some reason, char attribute is None for NumPad numbers.
            This corrects it using their virutal key numbers."""
            key.char = str(key.vk - 96)
        replace_sequence(key_sequence, key.char)
    else:
        replace_sequence(key_sequence, key.name)


def update_state(state_list: list[bool, int], skip_count: int, desired_state: bool = False, switch: bool = False) -> None:
    """Tells the on_press processor to skip
    the next skip_count presses. 
    Used to ignore app-issued presses."""
    if switch:
        state_list[0] = not state_list[0]
    else:
        state_list[0] = desired_state
    if skip_count<0 and skip_count==state_list[1]:
        state_list[1] = 0
    else: 
        state_list[1]=skip_count


def on_press(
    key: kb.Key, keyboard: kb.Controller, key_sequence: list[str, str], processing_state: list[bool, int]
    ) -> bool | None:
    update_sequence(key, key_sequence) 
    if set(key_sequence).intersection(CHANGE_PROVOKING_KEYS):
        """Responding to potential change in keyboard language.
        Aims to only process events if desired language is being used."""
        if processing_state[1]<0:
            pass
        elif not processing_state[0] and current_keyboard_language() in desired_keyboards:
            update_state(processing_state, 0, True)
        elif processing_state[0] and current_keyboard_language() not in desired_keyboards:
            update_state(processing_state, 0, False)

    if len(set(key_sequence).intersection(stoppage_hotkey))==2:
        """Handling turning the processing on and off with a hotkey.
        The app only supports stoppage hotkeys with length of 2.
        Therefore a intersection of length of 2 constitutes a match.
        -1 is only used here, therefore disallowing hotkey
        sleep mode from being overridden"""
        print('tracker')
        update_state(processing_state, -1, switch=True)

    if not processing_state[0]:
        """Handling early exit due to wrong keyboard being selected or a set skip counter"""
        if processing_state[1]>0:
            if processing_state[1]==1:
                update_state(state_list=processing_state, skip_count=0, desired_state=True)
                return True
            update_state(state_list=processing_state, skip_count=processing_state[1]-1)
        return True
    
    if key_sequence[0] in ACCENTED_SYMBOLS and key_sequence[1].isnumeric():
        """Replace vowels with their required accented version"""
        update_state(processing_state, 3, False)   
        keyboard.press(kb.Key.backspace)     
        keyboard.release(kb.Key.backspace)
        keyboard.press(kb.Key.backspace)     
        keyboard.release(kb.Key.backspace)       
        keyboard.press(ACCENTED_SYMBOLS[key_sequence[0]][int(key_sequence[1]) - 1])
        keyboard.release(ACCENTED_SYMBOLS[key_sequence[0]][int(key_sequence[1]) - 1])


def main() -> None:
    keyboard = kb.Controller()
    key_sequence: list[str] = ["", ""]
    if current_keyboard_language() in desired_keyboards:
      processing_state = [True, 0]  
    else:
        processing_state = [False, 0]
    on_press_action = lambda pressed: on_press(key = pressed, keyboard=keyboard, key_sequence=key_sequence, processing_state=processing_state)
    with kb.Listener(
        on_press= on_press_action
    ) as listener:  # Setup the listener
        listener.join()  # Join the thread to the main thread


if __name__ == "__main__":
    main()
