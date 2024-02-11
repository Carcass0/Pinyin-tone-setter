from pynput.keyboard import Key, Controller, Listener

from constants import CHANGE_PROVOKING_KEYS, ACCENTED_SYMBOLS
from utils import update_sequence, update_state, current_keyboard_language


class ToneListener():

    def __init__(self, desired_keyboard: str, stop_hotkeys: list[str]) -> None:
        keyboard = Controller()
        key_sequence: list[str] = ["", ""]
        self.desired_keyboard = desired_keyboard
        self.stop_hotkeys = stop_hotkeys
        if current_keyboard_language() == self.desired_keyboard:
            processing_state = [True, 0]
        else:
            processing_state = [False, 0]
        on_press_action = lambda pressed: self.main_processor(
            key=pressed,
            keyboard=keyboard,
            key_sequence=key_sequence,
            processing_state=processing_state,
        )   
        self.listener = Listener(on_press=on_press_action)
    
    def main_processor(
    self, key: Key, keyboard: Controller, key_sequence: list[str], processing_state: list[int]
    ) -> None:
        update_sequence(key, key_sequence)
        if set(key_sequence).intersection(CHANGE_PROVOKING_KEYS):
            """Responding to potential change in keyboard language.
            Aims to only process events if desired language is being used."""
            if processing_state[1] < 0:
                pass
            elif (
                not processing_state[0] and current_keyboard_language() == self.desired_keyboard
            ):
                update_state(processing_state, 0, True)
            elif processing_state[0] and current_keyboard_language() != self.desired_keyboard:
                update_state(processing_state, 0, False)

        if len(set(key_sequence).intersection(self.stop_hotkeys)) == 2 or (
            len(set(key_sequence).intersection(self.stop_hotkeys)) == 1
            and self.stop_hotkeys.count("") == 1
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
        
    def update_settings(self, keyboard, hotkeys):
        self.desired_keyboard = keyboard
        self.stop_hotkeys = hotkeys
