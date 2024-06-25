import csv

from youtubesearchpython import VideosSearch
from pytube import YouTube
import time, os, json, pygame, tkinter as tk, win32gui, win32con, win32api, keyboard, random, difflib, threading
from googlesearch import search
from bs4 import BeautifulSoup

from screeninfo import get_monitors
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

from content.python_projects import pyvidplayer


def download_video(name):
    path = os.getcwd()
    file_name = name.replace(' ', '-') + '.mp4'
    file_name = file_name.replace('/', '-').replace('?', '-').replace(':', '-')

    if not os.path.exists(path + '\\content\\' + file_name):

        # to search
        query = name + ' mal'
        j = None
        for ii in search(query, tld="co.in", num=1, stop=1, pause=1):
            j = ii

        service = Service(executable_path="C:\\Users\\tomas\\OneDrive\\Dokumenti\\chromedriver_win32\\chromedriver")

        op = webdriver.ChromeOptions()
        op.add_argument('headless')

        # initialize web driver
        with webdriver.Chrome(service=service, options=op) as driver:

            # navigate to the url
            driver.get(j)

            # find element by class name
            my_div = driver.find_element(By.CLASS_NAME, 'h1-title')
            soup = BeautifulSoup(my_div.get_attribute('outerHTML'), features='lxml')
            if soup.find('p', {'class': 'title-english title-inherit'}) is not None:
                english_name = [a for a in soup.find('p', {'class': 'title-english title-inherit'})]
            else:
                english_name = [name]
            if type(english_name) == list: english_name = english_name[0]

        videos_search = VideosSearch(english_name + ' opening', limit=1)

        csv_filename = 'music_quizes.csv'
        dct = videos_search.result()
        link = dct['result'][0]['link']
        video_name = dct['result'][0]['title']

        while True:

            time.sleep(1)

            try:
                print(link)
                yt = YouTube(link)
                video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                video.download('content', filename=file_name)

                value = yt.views

                with open(csv_filename, 'a', newline='', encoding='utf-8') as opa:
                    opa = csv.writer(opa, delimiter=',')

                    opa.writerow([name, english_name, file_name, value])
                break
            except KeyError:
                time.sleep(10); print('sleepmode time')

        print('downloaded: ', video_name, '----', english_name, '----', file_name, '----', name, value)
    else:
        print('file already exists')


def add_data():  # referencing this will download mal songs and add them to the csv
    with open('mal.json') as f:
        data = json.load(f)

    br = 0
    for i in data['myanimelist']['anime']:
        print('Downloading', i['series_title']['__cdata'])
        download_video(i['series_title']['__cdata'])
        br += 1


class Window:
    def __init__(self, screen, width, height, path):
        self.current_song_data = 0

        self.clip = None
        self.times = time.time(); self.max_time = 15
        self.song_count = 5; self.points = 0
        self.hide_window = True
        self.round_win = False

        self.data = []; self.average_views = 0; a = 0; self.current_count = 0
        with open(path+'\\content\\anime_quiz\\music_quizes.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                self.data.append(row)
                self.average_views += int(row[3]); a += 1
            self.average_views = self.average_views / a

        random.shuffle(self.data)

        self.terminal_font = "Roboto-Regular.ttf"
        self.font = pygame.font.Font(self.terminal_font, 70)
        self.font2 = pygame.font.Font(self.terminal_font, 30)

        self.absolute_data = self.data.copy()
        self.current_count = self.average_views

        self.screen = screen; self.width = width; self.height = height

        self.path = path

    def autocomplete_text(self, text):
        highest_score = 0; closest_text = ''
        for i in self.absolute_data:
            if difflib.SequenceMatcher(a=text.lower(), b=i[0].lower()).ratio() > highest_score and text.lower() in \
                    i[0].lower():
                closest_text = i[0]
                highest_score = difflib.SequenceMatcher(a=text.lower(), b=i[0].lower()).ratio()
            if difflib.SequenceMatcher(a=text.lower(), b=i[1].lower()).ratio() > highest_score and text.lower() in \
                    i[1].lower():
                closest_text = i[1]
                highest_score = difflib.SequenceMatcher(a=text.lower(), b=i[1].lower()).ratio()
        return closest_text

    def draw_window(self, text, typing):
        mid = (int(self.width / 2), int(self.height / 2))
        x, y = int(mid[0] / 2), int(mid[1] / 2)
        pygame.draw.rect(self.screen, (17, 11, 20), (mid[0] - x, mid[1] - y, x * 2, y * 2 + 100))

        if self.clip is not None:
            if not self.hide_window:
                self.clip.draw(self.screen, (mid[0] - x + 50, mid[1] - y))
                text_surf = self.font2.render(self.current_song_data[1], True, (220, 220, 220))
                text_rect = text_surf.get_rect(center=(mid[0], mid[1] + y - 80))

                self.screen.blit(text_surf, text_rect)
            else:
                pygame.draw.rect(self.screen, (120, 120, 120),
                                 (mid[0] - x + 50, mid[1] - y, x * 2 - 100, y * 2 - 100))
                text_surf = self.font.render(str(int(self.max_time - (time.time() - self.times))), True,
                                             (70, 70, 70))
                text_rect = text_surf.get_rect()
                text_rect.topleft = (mid[0], mid[1] - 100)

                self.screen.blit(text_surf, text_rect)

        if self.clip is not None:
            if self.hide_window:
                col = (70, 70, 70)
                if not typing: col = (230, 230, 230)
                text_surf = self.font2.render(text, True, col)
                text_rect = text_surf.get_rect(center=(mid[0], mid[1] + y))

                self.screen.blit(text_surf, text_rect)

                text_surf = self.font2.render(self.autocomplete_text(text), True, (70, 70, 70))
                text_rect = text_surf.get_rect(center=(mid[0], mid[1] + y + 50))
                self.screen.blit(text_surf, text_rect)
            else:
                col = (140, 40, 50)
                if self.round_win: col = (40, 140, 50)
                text_surf = self.font2.render(text, True, col)
                text_rect = text_surf.get_rect(center=(mid[0], mid[1] + y))
                self.screen.blit(text_surf, text_rect)

        pygame.draw.rect(self.screen, (153, 162, 152), (mid[0] - x + 50, mid[1] + y - 120,
                                                        ((x * 2 - 100) * abs(1 - ((self.max_time - (
                                                                time.time() - self.times)) / self.max_time))), 20))

        if self.clip is not None: self.clip._update()

        pygame.display.update(mid[0] - x, mid[1] - y - 200, x * 2, self.height)

    def step_event(self, stag, typing, text):
        if stag == 0:  # data getting stage
            if self.song_count > 0:
                self.song_count -= 1
                while self.current_count > 0:
                    self.current_count -= int(self.data[0][3])
                    self.current_song_data = self.data[0]
                    self.data.pop(0)

                self.times = time.time()
                print(
                    '##################################################################################################################################################################################################################################################################################',
                    self.current_song_data)
                self.clip = pyvidplayer.Video(self.path+'\\content\\anime_quiz\\songs\\' + self.current_song_data[2])
                # self.clip.seek(random.randint(0, 15))
                mid = (int(self.width / 2), int(self.height / 2))
                x, y = int(mid[0] / 2), int(mid[1] / 2)
                self.clip.set_size((x * 2 - 100, y * 2 - 100))
                self.hide_window = True

                typing = True; self.round_win = False

                stag = 1

            else:
                exit()
        if stag == 1:
            if time.time() - self.max_time < self.times:
                pass  # self.clip._update()
            else:
                if not self.hide_window:
                    if self.song_count > 0:
                        self.current_count = self.average_views; stag = 0
                    else:
                        if not self.clip.active: exit()
                else:
                    self.times = time.time(); self.hide_window = False; self.clip.restart()
                    if self.current_song_data[0].lower() == text.lower() or self.current_song_data[
                        1].lower() == text.lower(): self.round_win = True
        return stag, typing


class MainGame:
    def __init__(self):
        self.characters = 'abcdefghijklmnopqrstuvwxyz123456789!?./;:,- '

        self.text = ''; self.typing = True
        self.win = Window()
        self.stage = 0

        self.count = 0; self.times = time.time()

    def step_event(self):
        def process(key):
            if keyboard.is_pressed(key.name):
                if self.typing and self.win.hide_window:
                    if key.name == 'space': key.name = ' '
                    if key.name != 'backspace':
                        if str.lower(key.name) in self.characters: self.text += key.name
                        if key.name == 'enter': self.typing = False
                        if key.name == 'tab': self.text = self.win.autocomplete_text(self.text)
                    else:
                        self.text = self.text[:-1]
                print(key.name)

        def key_capturing():
            keyboard.hook(process)
            while True:
                keyboard.wait()

        threading.Thread(target=key_capturing, name='gather_keystrokes', daemon=True).start()

        while True:
            time.sleep(0.001)
            self.win.draw_window(self.text, self.typing)
            typ = self.typing
            self.stage, self.typing = self.win.step_event(self.stage, self.typing, self.text)
            if self.typing and typ != self.typing: text = ''
