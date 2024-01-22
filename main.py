from pynput import keyboard as kb


STOPPAGE_COMBINATIONS = [['alt_l', 'shift'], ['shift', 'alt_l'], ['ctrl_l', '1'], ['ctrl_l', '2']]
ACCENTED_SYMBOLS = {'a': ['ā', 'á', 'ǎ', 'à'],
                    'A': ['Ā', 'Á', 'Ǎ', 'À'],
                    'e': ['ē', 'é', 'ě', 'è'],
                    'E': ['Ē', 'É', 'Ě', 'È'],
                    'i': ['ī', 'í', 'ǐ', 'ì'],
                    'I': ['Ī', 'Í', 'Ǐ', 'Ì'],
                    'o': ['ō', 'ó', 'ǒ', 'ò'],
                    'O': ['Ō', 'Ó', 'Ǒ', 'Ò'],
                    'u': ['ū', 'ú', 'ǔ', 'ù', 'ü', 'ǖ', 'ǘ', 'ǚ', 'ǜ'],
                    'U': ['Ū', 'Ú', 'Ǔ', 'Ù', 'Ü', 'Ǖ', 'Ǘ', 'Ǚ', 'Ǜ']}


def get_keyboard_language():
    """
    0x804 - Chinese - People's Republic of China
    0x409 - English - United States
    0x419 - Russian
    """


def update_sequence(target_list: list[str, str], value: str) -> None:
    target_list[0] = target_list[1]
    target_list[1] = value


def on_press(key: kb.Key, keyboard: kb.Controller, filename:str, key_sequence: list[str, str]) -> (bool | None):
    if key == kb.Key.esc:
        return False
    elif hasattr(key, 'char'):
        print(key.vk)
        if hasattr(key, 'vk') and key.vk is not None and key.vk>=96 and key.vk<=105:  
            """For some reason, char attribute is None for NumPad numbers.
            This corrects it using their virutal key numbers."""
            key.char = str(key.vk-96)
        update_sequence(key_sequence, key.char)
        print(key_sequence)
    else: 
        update_sequence(key_sequence, key.name)
        print(key_sequence)
    if key_sequence in STOPPAGE_COMBINATIONS:
                key_sequence=[0, '', '']
                return(False) 
    else:
         if key_sequence[0] in ACCENTED_SYMBOLS and key_sequence[1].isnumeric():
              keyboard.press(kb.Key.backspace)
              keyboard.release(kb.Key.backspace)
              keyboard.press(kb.Key.backspace)
              keyboard.release(kb.Key.backspace)
              keyboard.press(ACCENTED_SYMBOLS[key_sequence[0]][int(key_sequence[1])-1])
              keyboard.release(ACCENTED_SYMBOLS[key_sequence[0]][int(key_sequence[1])-1])


def main() -> None:
    filename = "key_log.txt"  # The file to write characters to
    with open(filename, 'w') as _:
        pass
    keyboard = kb.Controller()
    key_sequence = ['', '']
    with kb.Listener(on_press=lambda event: on_press(event, keyboard=keyboard, filename=filename, key_sequence=key_sequence)) as listener:  # Setup the listener
        listener.join()  # Join the thread to the main thread


if __name__=='__main__':
    main()