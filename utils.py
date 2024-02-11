from ctypes import WinDLL
from os import path

from pynput.keyboard import Key

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


def current_keyboard_language() -> str:
    """Get current keyboard language.
    source:
    https://stackoverflow.com/questions/42047253/how-to-detect-current-keyboard-language-in-python
    """
    user32 = WinDLL("user32", use_last_error=True)
    handle = user32.GetForegroundWindow()
    threadid = user32.GetWindowThreadProcessId(handle, 0)
    layout_id = user32.GetKeyboardLayout(threadid)
    # Extracting the keyboard language id from the keyboard layout id
    language_id = layout_id & (2**16 - 1)
    return hex(language_id)
