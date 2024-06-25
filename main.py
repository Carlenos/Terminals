import gc, sys

import keyboard
import pygame, os, math, time, ctypes
from window_stuff import window
from sys import exit
import threading
from win32gui import GetWindowText, GetForegroundWindow

from terminal_content import terminal_commands
from terminal_content import games
from window_stuff.colors import *
from content.python_projects import environment
from content.python_projects import japanese

from content.python_projects.scada_attacks import main as scada_attacks


window = window.Window()
screen, transparent_color, width, height = window.get_basic_values()
text_contents = window.text_contents; force_quit = 0; change_level = 0; change_val = 0
text_content_add = ''; text_submit = ''; sleep_mode = 0; sleep_mode_key = ''; clip = None

'''
from tkinter import *s
import winsound
root = Tk()
e = Entry(root)
e.pack()
def key_pressed(event):
    print("doing")
    winsound.Beep(1000, 100)

e.bind_all("<Key>", key_pressed)

root.mainloop()
'''

resizing = (0, 0)

arrow_copy = 0; arrow_copy_active = 0; arrow_remember = ''

# game section
disable_typing = 0; game = 0; game_environment = games.GameEnvironment()

chars = '''abcdefghijklmnopqrstuvwxyz /n_-()=[]".,0123456789+*'''

user32 = ctypes.WinDLL('user32')
path = os.getcwd()

command_manager = terminal_commands.Commands(window)

pygame.mixer.init()


def process(key):
    key = key.name

    global text_content_add, sleep_mode_key, sleep_mode, text_submit, text_contents
    global arrow_copy, arrow_copy_active, arrow_remember
    if sleep_mode:
        if key.replace('left ', '').replace('right ', '') + sleep_mode_key.replace('left ', '').replace('right ', '') == 'shiftalt':
            sleep_mode = 0; window.read_json(); window.draw_text_contents()
        sleep_mode_key = key
        time.sleep(0.1); print(key + sleep_mode_key)
        return 1
    if keyboard.is_pressed(key) and GetWindowText(GetForegroundWindow()) == window.window_name and not sleep_mode and not disable_typing:

        window.flashing_line_tick = -0.001

        #tx, ty, ti = window.terminal_location[0], window.terminal_location[1], window.terminal_size; brd_size = window.terminal_boarder_size
        #window.draw_flashing_line(tx, ty, ti, brd_size)

        if key == 'space': key = ' '
        if chars.count(str.lower(key)) >= 1:
            text_content_add += key; return 'break'

        if key == 'backspace':
            text_content_add = '/r'; return 'break'

        if key == 'tab':
            text_content_add = window.autocomplete_text

        if key == 'right' or key == 'left':
            if clip is not None:
                print('POS', clip.get_pos())
                if key == 'right': clip.seek(0.1)
                else: clip.seek(-3)

        movement_keys = ['right', 'left', 'up', 'down']; move = False; i = 20
        movement_changes = [(i, 0), (-i, 0), (0, -i), (0, i)]
        if keyboard.get_hotkey_name().count('shift') >= 1:
            for i in movement_keys:
                if keyboard.get_hotkey_name().replace('shift+', '') == i:
                    move = i; break

        if move:
            window.terminal_location = tuple(map(sum, zip(movement_changes[movement_keys.index(move)], window.terminal_location)))
            window.clear = 1; window.draw_text_contents()

        if not arrow_copy_active and not move:
            if key == 'up':
                arrow_copy_active = True
        if arrow_copy_active and not move:
            arrow_copy_prev = arrow_copy
            if key == 'up' and arrow_copy < window.text_contents.count('/n'):
                if arrow_copy == 0: arrow_remember = window.text_contents.split('/n')[window.text_contents.count('/n')]
                arrow_copy += 1
            if key == 'down' and arrow_copy > 0:
                arrow_copy -= 1
            while window.text_contents.split('/n')[window.text_contents.count('/n') - arrow_copy].count('—') > 0:
                if key == 'down':
                    arrow_copy -= 1
                if key == 'up':
                    arrow_copy += 1
                    if arrow_copy > window.text_contents.count('/n'): key = 'down'
            if key != 'down' and key != 'up':
                arrow_copy_active = False; arrow_copy = 0; arrow_remember = ''
            else:
                if arrow_copy_prev != arrow_copy:
                    temp = window.text_contents.split('/n')
                    temp[window.text_contents.count('/n')] = ''
                    window.text_contents = '/n'.join(temp)

                    copied_text = temp[window.text_contents.count('/n') - arrow_copy].replace('—', '~')
                    if arrow_copy == 0: copied_text = arrow_remember

                    temp[window.text_contents.count('/n') - arrow_copy] = copied_text
                    text_content_add = temp[window.text_contents.count('/n') - arrow_copy]
                    text_contents = window.text_contents
                    text_submit = ''

        if key == 'enter':
            if window.autocomplete_text != '':
                window.text_contents = window.text_contents + window.autocomplete_text
                text_contents = text_contents + window.autocomplete_text
                text_submit = text_submit + window.autocomplete_text
            commands()
    if keyboard.is_pressed(key) and disable_typing:
        if game: game_environment.keyboard_event(key)


def key_capturing():
    keyboard.hook(process)

    count = 0; times = time.time()

    while True:
        #keyboard.wait()
        time.sleep(0.0001)  # also scuffed af...
        count += 1
        if time.time() - times >= 1:
            times = time.time()
            #print('thread 2 fps: ', count)
            count = 0


def fire_and_forget():
    environment.start()


def save_text():
    global text_contents, text_content_add, text_submit
    if text_content_add.count('/r') == 0: window.text_contents = text_contents + text_content_add; text_submit += text_content_add
    else:
        b = ''
        for a in text_content_add:
            if a == 'r' and b == '/':
                if text_contents[len(text_contents) - 2: len(text_contents)] != '/n':
                    text_contents = text_contents[:-1]
                    text_submit = text_submit[:-1]
                b = ''
            else:
                if a != '/' or a + b == '//': text_contents += b + a; text_submit += b + a
            if a == '/': b = '/'
        window.text_contents = text_contents
    text_content_add = ''


def scroll(event_list):
    for event in event_list:
        if event.type == pygame.MOUSEWHEEL:
            max_lines = math.floor((window.terminal_size[1]*2 - window.terminal_boarder_size*2) / (window.text_size + window.text_spacing)) - 1
            if window.text_contents.count('/n') >= max_lines:
                y = event.y
                #y = math.copysign(1, y)
                prev = window.terminal_text_order
                window.terminal_text_order -= y

                if window.terminal_text_order >= 0: window.terminal_text_order = 0
                if window.terminal_text_order <= max_lines - window.text_contents.count('/n'): window.terminal_text_order = max_lines - window.text_contents.count('/n')

                if prev != window.terminal_text_order:
                    tx, ty, ti = window.terminal_location[0], window.terminal_location[1], window.terminal_size
                    window.draw_text_contents(tx - ti[0], ty - ti[1], tx + ti[0], ty + ti[1])

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not window.mouse_hold:
                window.mouse_click_location = list(pygame.mouse.get_pos())
                window.mouse_click_location_realtime = list(pygame.mouse.get_pos())
            window.mouse_hold = True; window.mouse_draw_stay = 0
        if event.type == pygame.MOUSEMOTION:
            if window.mouse_hold:
                window.mouse_click_location_realtime = list(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONUP:
            window.mouse_hold = False; window.mouse_draw_stay = 1


def commands_ch_special_cases(directory):
    if directory == 'img': pass


def commands():
    global text_content_add, text_submit, text_contents, force_quit, change_level, change_val, sleep_mode
    global disable_typing, game, game_environment, clip

    result, res = command_manager.fix_result(text_submit)

    if result == 'start py':
        threading.Thread(target=fire_and_forget(), name='game_thread').start()

    if res[0] == 'game' or result == 'game':
        if command_manager.start_game():
            disable_typing = True; game_environment = games.GameEnvironment(); game = True
            window.text_contents = ''; window.terminal_text_order = 0; text_submit = ''
            window.terminal_text_order_colors.clear(); window.clear = 1; window.game = game; text_contents = ''
            window.draw_text_contents()  # to release the text / draw empty

            game_environment.change_game_instance(res[1], path)

            text_content_add = game_environment.create_event(window)

            return 'uwu'

    if res[0] == 'play':
        pygame.mixer.stop()
        if clip is not None: clip.stop()
        clip = command_manager.play()
    if result == 'stop':
        pygame.mixer.stop()
        if clip is not None: clip.stop()
        clip = command_manager.stop(); window.read_json()

    if result == 'help': command_manager.help()
    if res[0] == 'calc': command_manager.calculate()
    if res[0] == 'image': command_manager.show_image()

    if result == 'run_program': command_manager.run_program()

    if result == 'full' or result == 'mid': command_manager.full_or_mid()

    if result[0:15] == 'recompile image':
        window.text_contents += '/nProcessing image...'; text_contents += '/nProcessing image...'
        window.terminal_text_order_colors[window.text_contents.count('/n')] = OLIVINE
        threading.Thread(target=command_manager.recompile_image()).start()

    if res[0] == 'scada':
        threading.Thread(target=command_manager.scada_attacks()).start()

    if result == 'art': command_manager.art()

    if result == 'sleep':
        text_content_add = '/n'; sleep_mode = 1; text_submit = ''; return 'uwu'
    if result == 'clear':
        window.text_contents = ''; text_content_add = ''; text_contents = ''; window.terminal_text_order = 0; text_submit = ''
        window.terminal_text_order_colors.clear(); window.clear = 1
        return 'uwu'
    if result == 'exit' or result == 'quit':
        pygame.mixer.stop()
        if clip is not None: clip.stop()
        time.sleep(0.1)  # this is so audio doesnt stay in the window
        force_quit = 1
        exit()

    if res[0] == 'set': command_manager.set()
    if res[0] == 'get': command_manager.get()

    text_content_add = command_manager.end_sequence()
    i = text_content_add
    print("####################", i, japanese.romajiToJapanese(i))

    text_submit = ''


def start():
    global text_contents, text_content_add, force_quit, sleep_mode, resizing, window_animation, clip
    times = time.time(); count = 0
    while True:
        if not sleep_mode:
            if force_quit: exit()
            time.sleep(0.0001)  # scuffed af, might fix it later
            event_list = pygame.event.get()

            save_text()
            scroll(event_list)

            # resize image instantly
            if resizing != window.terminal_size:
                window.terminal_img_background_package = window.calculate_img_background()
                resizing = window.terminal_size

            # terminal games :o
            if game: game_environment.step_event(window)

            # random terminal things
            window.video_clip = clip

            # main terminal window
            try:
                window.draw_window()
            except:
                pass
            text_contents = window.text_contents  # needed / associated with the save_text() function [needs to be AFTER window.draw_window()]

            # random terminal things flipped
            if window.video_clip is None and clip is not None:
                try:
                    clip.stop(); clip = None
                except AttributeError: pass

            # window.screen.
            window.root.update()

            # pygame.display.flip(); window.flip = 0
            if time.time() - times < 1: count += 1
            else:
                # print(count); times = time.time()
                count = 0

        else:
            screen.fill(transparent_color)

            # some random terminal things have to update
            #if clip is not None:
            #    clip.update()

            pygame.display.update(); window.root.update()
            time.sleep(1)


if __name__ == '__main__':
    threading.Thread(target=key_capturing, name='gather_keystrokes', daemon=True).start()
    start()
