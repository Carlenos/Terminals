import json, math, pygame, pathlib, pprint, subprocess, time
from moviepy.editor import *
from terminal_content import ascii_art
from window_stuff.colors import *
from screeninfo import get_monitors

# from content.python_projects import pyvidplayer
from pyvidplayer2 import Video

from content.python_projects.scada_attacks import main as scada_attacks


class Commands:
    def __init__(self, window):
        # Non changeable variables
        self.path = os.getcwd()
        self.window = window

        self.width, self.height = 250, 250
        for m in get_monitors():
            self.width, self.height = m.width, m.height
        self.not_found_text = ' Sorry, command not found '
        self.text_addon = ['/n———— ', ' ————/n']

        with open(self.path + '/content/json_data/data.json') as json_file:
            self.data = json.load(json_file)
        with open(self.path + '/content/json_data/colors.json') as json_file:
            self.all_colors = json.load(json_file)

        pygame.mixer.init()

        # Changeable variables
        self.action = 0; self.text_content_add = ''
        self.result = ''; self.res = ''

        # change command specific variables
        self.change_val = ''; self.change_thing = ''; self.change_level = 0

    ########################################[ change given command ( to be readable ) and restart some variables ]###############################################
    def fix_result(self, result):
        result = result.replace('/n', '').replace('/r', '')
        result = result.replace(ascii_art.neferpitou().replace('/n', ''), '')

        if result.count('—') > 0:
            result = result.split('—')[result.count('—')]

        self.res = result.split(' '); self.action = 0; self.result = result; self.change_thing = ''

        return self.result, self.res

    #####################################[ start video game ]##################################
    def start_game(self):
        if len(self.res) > 1:
            if self.res[1] == 'pitou-type' or self.res[1] == 'anime-music-quiz':
                self.text_content_add = ''
                #self.txt_col(SANDY_BROWN); self.action = 1
                self.action = 1
                return True
            else:
                self.text_content_add = self.text_addon[0] + " game '"+str(self.res[1])+"' does not exit " + self.text_addon[1]
                self.txt_col(SANDY_BROWN); self.action = 1
        else:
            self.text_content_add = self.text_addon[0] + " Enter the game's name " + self.text_addon[1]
            self.txt_col(LIGHT_CORAL); self.action = 1
        return False

    ############################[ help ( get information on functions ]###############################
    def help(self):
        self.text_content_add = self.text_addon[0] + 'get, set, sleep, exit, calc, play, art, full, mid, recompile, game, scada' + self.text_addon[1]
        self.window.terminal_text_order_colors[self.window.text_contents.count('/n') + 1] = OLIVINE; self.action = 1

    ####################################[ CALCULATOR ]########################################
    def calculate(self):
        try:
            self.res[1] = self.res[1].replace("pi", str(math.pi))
            self.res[1] = self.res[1].replace("E", str(math.e))
            temp = str(eval(self.res[1]))
            if len(temp) > 2 and temp[len(temp)-2:len(temp)] == '.0': temp = temp[:len(temp)-2]
            self.text_content_add = self.text_addon[0] + temp + self.text_addon[1]
            self.txt_col(OLIVINE); self.action = 1
        except NameError: print("L")

    ####################################[ CALCULATOR ]########################################
    def show_image(self):
        try:
            # check if the right extension
            if self.res[1].lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.avif', 'webp')):
                self.text_content_add = "/n———" + "image "+self.res[1] + " ——/n"
                self.txt_col(OLIVINE); self.action = 1
            else:
                # check if its in the images folder
                if pathlib.Path(self.path + '\\content\\images\\' + self.res[1] + '.png').is_file():
                    self.text_content_add = "/n———" + "image " + self.path + '\\content\\images\\' + self.res[1]+".png" + " ——/n"

                    for a in range(0, 12):
                        self.text_content_add += "——/n"

                    self.txt_col(OLIVINE); self.action = 1
                else:
                    self.text_content_add = self.text_addon[0] + "invalid image" + self.text_addon[1]
                    self.txt_col(OLIVINE); self.action = 1
        except NameError: print("L")

    #############################################[ play video / soundtrack ]#####################################################
    def play(self):
        if len(self.res) > 1:
            a = self.res; a[0] = a[0].replace(a[0], ''); son = ' '.join(a); son = son[1:]
            if pathlib.Path(self.path + '\\content\\songs\\'+son+'.mp4').is_file():
                self.stop()  # first stop any existing songs
                clip = Video(self.path + '\\content\\songs\\'+son+'.mp4')

                self.text_content_add = '/n————  Playing ' + son + '  ————/n'
                self.txt_col(OLIVINE); self.action = 1

                return clip
            else: self.text_content_add = "/n————  mp4 file '"+son+"' doesnt exist  ————/n"; self.txt_col(LIGHT_CORAL); self.action = 1
        else: self.text_content_add = "/n————  Add a song after 'play'  ————/n"; self.txt_col(LIGHT_CORAL); self.action = 1
        return None

    #######################################[ stop soundtrack ]#######################################
    def stop(self):
        pygame.mixer.music.stop()
        self.text_content_add = self.text_addon[0]+' Stopping all sfx '+self.text_addon[1]
        self.txt_col(OLIVINE); self.action = 1
        return None

    ########################################[ fullscreen or mid-screen ]########################################
    def full_or_mid(self):
        text = ''
        if self.result == 'mid': self.data['win']['size'] = [self.width / 2, self.height / 2]; text = 'minimization'
        if self.result == 'full': self.data['win']['size'] = [self.width, self.height]; text = 'maximization'

        with open(self.path + "/content/json_data/data.json", "w") as jsonFile:
            json.dump(self.data, jsonFile)

        self.text_content_add = self.text_addon[0]+'  ' + text + ' successful ' + '  '+self.text_addon[1]
        self.txt_col(OLIVINE)

        self.window.read_json(); self.action = 1

    ####################################[ delete current or all images ]#########################################
    def recompile_image(self):
        if len(self.res) > 2:
            if self.res[2] == 'all':
                image_list = os.listdir(self.window.terminal_img_background_saved_location)
                for i in image_list:
                    if i.endswith('FINISHED.png'):
                        os.remove(os.path.join(self.window.terminal_img_background_saved_location, i))
        else: os.remove(self.window.terminal_img_background_saved_location + self.window.terminal_img_background_name + '_FINISHED.png')

        self.text_content_add = '/n————  ' + ' image recompilation successful ' + '  ————/n'
        self.txt_col(OLIVINE)

        self.window.read_json(); self.action = 1

    ###############################################[ SCADA attacks ]#####################################################
    def scada_attacks(self):
        attacks_protocols = ['modbus', 'iec104', 's7comm']

        attack_numbers = {
            'modbus': ['all'],
            'iec104': ['5.2', '5.4'],
            's7comm': ['work in progress']
        }

        if len(self.res) < 2 or (len(self.res) >= 2 and self.res[1] not in attacks_protocols):
            self.text_content_add = f'/n— pick one of the following protocols: {", ".join([str(x) for x in attacks_protocols])} —/n'
            self.txt_col()
        else:
            if len(self.res) >= 3:
                try:
                    if self.res[2] in attack_numbers[self.res[1]]:
                        scada_attacks.main_function(self.res[1], self.res[2])

                        self.text_content_add = f'/n———— commencing {self.res[1]} attack number {self.res[2]} ————/n'; self.txt_col(OLIVINE)
                    else: raise ValueError
                except ValueError:
                    self.text_content_add = f'/n——— choose one from these: {", ".join([str(x) for x in attack_numbers[self.res[1]]])} ———/n'
                    self.txt_col()
            else: self.text_content_add = '/n——— pick an attack number ———/n'; self.txt_col()

        self.action = 1

    ######################################[ ascii art uwu ]##########################################
    def art(self):
        self.text_content_add = ascii_art.neferpitou(); self.action = 1
        print(ascii_art.neferpitou())

    #########################################[ run program ]##############################################
    def run_program(self):  # NOT FINISHED
        data = subprocess.check_output(['wmic', 'product', 'get', 'name'])
        a = str(data)
        print(a)
        proc = subprocess.Popen(['python', 'printbob.py', 'arg1 arg2 arg3 arg4'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(proc.communicate()[0])

    #######################################[ 'change' command ( change any json value ) ]#############################################
    def set(self):
        result = self.result.replace(' = ', '='); change_val = ''
        if result.count('(') < 1 and result.count('[') < 1:
            result = result.replace('=', ' —')
        else: result = result.replace('=', ' ')
        change_thing = result.replace('set ', ''); self.change_level = 1
        omae = change_thing.split(' ')[0]
        if omae in self.data:
            self.change_level = 2
            if change_thing.count(' ') < 2: change_thing = change_thing+' '
            if change_thing.split(' ')[1] in self.data[omae]:
                self.change_level = 3
                try:
                    result = result.replace('(', '[').replace(')', ']'); result = result.replace(', ', ',')
                    if result.count(',') > 0: result = result.replace('—', '['); change_thing = change_thing.replace('—', '')
                    else: result = result.replace('—', ''); change_thing = change_thing.replace('—', '')
                    if result.count('[') > 0 or result.count(']') > 0:
                        change_val = result.split('[')[1].replace(']', '').replace(' ', '')
                        change_val = list(map(int, change_val.split(',')))
                    else: change_val = change_thing.split(' ')[2]
                    if type(change_val) == int or type(change_val) == float: change_val = str(change_val)

                    if change_val == 'full': change_val = [self.width, self.height]
                    if change_val == 'mid': change_val = [self.width/2, self.height/2]

                    self.data[omae][change_thing.split(' ')[1]] = change_val
                    if type(change_val) == str:
                        if change_val.upper() in self.all_colors: self.data[omae][change_thing.split(' ')[1]] = self.all_colors[change_val.upper()]

                    pretty_dump = pprint.pformat(self.data)
                    with open(self.path+"/content/json_data/data.json", "w") as jsonFile:
                        jsonFile.write(pretty_dump.replace("'", '"'))
                        #json.dump(pretty_dump, jsonFile)

                    self.window.read_json()

                    # commands_ch_special_cases('omae wa, shinjetsu')

                    self.change_level = 4
                except IndexError: print('whoopsies, might add custom message here later')
        self.change_thing = change_thing; self.change_val = change_val

    #######################################[ 'get' command ( read files and json value ) ]######################################
    def get(self):
        self.txt_col(); get_amount = self.window.get_amount
        if len(self.res) > 1:
            if self.res[1] in self.data:
                self.txt_col(SANDY_BROWN)
                t = '/n———'; self.action = 1; b = 1; release = get_amount; d = ''
                for a in self.data[self.result.split(' ')[1]]:
                    c = self.data[self.result.split(' ')[1]][a]
                    if type(c) == list: c = '(' + ','.join(str(x) for x in c) + ')'
                    if type(c) == int or type(c) == float: c = str(c)
                    if release < get_amount: release += 1; d = '   ——   '
                    else: release = 1; d = '/n'
                    t += d + a + ': ' + c; b += 1
                    if get_amount == 1: t += '   ——   '; d = '1'
                    self.window.terminal_text_order_colors[self.window.text_contents.count('/n') + math.ceil((b + 1) / get_amount)] = OLIVINE
                self.window.terminal_text_order_colors[self.window.text_contents.count('/n') + math.ceil((b + 1) / get_amount) + 1] = SANDY_BROWN
                if d == '/n': t += '   ——   ';self.window.terminal_text_order_colors[self.window.text_contents.count('/n') + math.ceil((b + 1) / get_amount) + 1] = OLIVINE
                if t == '': t = self.text_addon[0]+'Whoopsies, something went wrong'+self.text_addon[1]
                self.text_content_add = t + '/n———/n'
            else:
                try:
                    try: image_list = os.listdir(self.res[1])
                    except FileNotFoundError: image_list = []
                    self.txt_col(SANDY_BROWN); b = 1; t = '/n————'; self.action = 1
                    if image_list:
                        release = get_amount; d = ''
                        for i in image_list:
                            if release < get_amount: release += 1; d = '   ——   '
                            else: release = 1; d = '/n'
                            t += d + i; b += 1; self.txt_col(OLIVINE, math.ceil((b-1) / get_amount))
                            if get_amount == 1: t += '   ——   '; d = 'uwu'
                        if d == '/n': t += '   ——   '  # last thingy is alone
                    else:
                        image_list = os.listdir(self.path + '\\content\\' + self.res[1]); release = get_amount; d = "";
                        for i in image_list:
                            if release < get_amount: release += 1; d = '   ——   '
                            else: release = 1; d = '/n'
                            t += d + i; b += 1; self.txt_col(OLIVINE, math.ceil((b-1) / get_amount))
                            if get_amount == 1: t += '   ——   '; d = 'hya'
                        if d == '/n': t += '   ——   '
                    self.text_content_add = t + '/n————/n'
                except FileNotFoundError:
                    self.action = 1; self.text_content_add = "/n———— Directory doesn't exist ————/n"; self.txt_col()
        else: self.text_content_add = '/n———— Add the directory you wish to see the values of ————/n'

    ###################################[ final cleanup text addons and text returning to main.py ]#########################################
    def end_sequence(self):
        et1, et2 = self.text_addon
        if self.action == 0:
            if self.change_level == 0:
                self.text_content_add = self.text_addon[0]+self.not_found_text+self.text_addon[1]; self.txt_col()
            else:
                if self.change_level == 1:
                    if self.result.count(' ') > 0:
                        self.text_content_add = et1+"'" + self.res[1]+"' isn't a valid directory" + ''+et2
                    else: self.text_content_add = '/n———— ' + "Enter a directory after 'ch'" + ' ————/n'
                if self.change_level == 2:
                    if self.result.count(' ') > 1:
                        self.text_content_add = "/n———— '" + self.res[2]+"' isn't a valid sub-directory" + ' ————/n'
                    else: self.text_content_add = '/n———— ' + "Enter a sub-directory after '"+self.res[1]+"'" + ' ————/n'
                if self.change_level == 3:
                    self.text_content_add = "/n———— " + "Whoopsies... something went wrong" + ' ————/n'
                if self.change_level == 4:
                    b = self.change_val
                    if type(self.change_val) == list: b = ', '.join(str(x) for x in self.change_val)
                    a = str(self.change_thing.split(' ')[1])
                    self.text_content_add = "/n———— " + "value "+"("+b+") "+"successfully added in sub directory "+"'"+a+"'"+' ————/n'
                    self.txt_col(OLIVINE)
                if self.change_level < 4: self.txt_col()
                self.change_level = 0
        return self.text_content_add

    # misc functions
    def txt_col(self, color=LIGHT_CORAL, extra=0):
        self.window.terminal_text_order_colors[self.window.text_contents.count('/n') + 1 + extra] = color
