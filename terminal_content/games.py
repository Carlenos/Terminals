import random as r, time
from content.python_projects import anime_music_quiz
all_keys = 'abcdefghijklmnopqrstuvwxyz '


class GameEnvironment:
    def __init__(self):
        self.game = 'pitou-type'

        #game variables
        self.game_text_contents = ''

        #pitou type variables
        self.pt_words = None
        self.pt_time = None

        #general game variables
        self.window = None
        self.path = ''

    def change_game_instance(self, game, path):
        self.game = game
        if self.game == 'anime-music-quiz': self.path = path

    def keyboard_event(self, key):
        key = key.replace('space', ' ')
        if all_keys.count(key) > 0:
            pass#print(key)

    def create_event(self, window):
        if self.game == 'pitou-type':
            pt_words = 'pitou the be of and a to in he have it that for they with as not on she at by this we you do but from or which one would all will there say who make when can more if no man out other so what time up go about than into could state only new year some take come these know see use get like then first any work now may such give over think most even find day also after way many must look before great back through long where much should well people down own just because good each those feel seem how high too place little world very still nation hand old life tell write become here show house both between need mean call develop under last right move thing general school never same another begin while number part turn real leave might want point form off child few small since against ask late home interest large person end open public follow during present without again hold govern around possible head consider word program problem however lead system set order eye plan run keep face fact group play stand increase early course change help line'
            self.pt_words = pt_words.split(' ')
            self.pt_time = time.time()

            text = ''; rs = 0
            for i in range(0, 200):
                text += self.pt_words[r.randint(0, len(self.pt_words)-1)]+' '; rs += 1
                if rs >= 10: text += '/n'; rs = 0

            window.game_text = text

            return text
        if self.game == 'anime-music-quiz':
            self.window = anime_music_quiz.Window(window, window.width, window.height, self.path)

    def step_event(self, window):
        if self.game == 'pitou-type':
            pass#print()
        if self.game == 'anime-music-quiz':
            print('0')
