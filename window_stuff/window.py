import gc
from sys import getsizeof
import psutil

import pygame, tkinter as tk, math, time, os
from screeninfo import get_monitors
import win32gui, win32con, win32api, glob, json, difflib

from fontTools.ttLib import TTFont

from PIL import Image

from window_stuff import hide_window
from window_stuff.colors import *


class Window:

    def _getr(self, slist, olist, seen):
        for e in slist:
            if id(e) in seen:
                continue
            seen[id(e)] = None
            olist.append(e)
            tl = gc.get_referents(e)
            if tl:
                self._getr(tl, olist, seen)

    # The public function.
    def get_all_objects(self):
        """Return a list of all live Python
        objects, not including the list itself."""
        gcl = gc.get_objects()
        olist = []
        seen = {}
        # Just in case:
        seen[id(gcl)] = None
        seen[id(olist)] = None
        seen[id(seen)] = None
        # _getr does the real work.
        self._getr(gcl, olist, seen)
        return olist

    def __init__(self):
        self.width, self.height = 250, 250
        for m in get_monitors():
            self.width, self.height = m.width, m.height
        print(self.width, self.height)
        #self.width=2560
        #self.height=1600
        self.root = tk.Tk()
        self.root.withdraw()

        pygame.init()

        self.window_name = 'poly-terminal'

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME | pygame.HWACCEL)
        win32gui.SetWindowPos(pygame.display.get_wm_info()['window'], -1, 0, 0, 0, 0, 1)
        pygame.display.set_caption(self.window_name)

        self.transparent_color = (10, 6, 2)

        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)

        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.transparent_color), 0, win32con.LWA_COLORKEY)
        win32gui.SetWindowPos(pygame.display.get_wm_info()['window'], -1, 0, 0, 0, 0, 1)

        handler = hide_window.find_window(self.window_name)
        hide_window.hide_from_taskbar(handler)
        hide_window.set_topmost(handler)

        self.hwnd = win32gui.GetForegroundWindow()
        self.path = os.getcwd()

        pygame.font.init()

        ii = 0; j = 0
        for i in self.get_all_objects():
            if getsizeof(i) > ii:
                ii = getsizeof(i)
                print(getsizeof(i))
            j += getsizeof(i)
        print('all sizes are: ', j / 1000000, ' mb')
        print('memory allocated: ', psutil.Process().memory_info().rss / 1000000, ' mb')

        ###############[  initialize values  ]###############

        self.text_contents = '————————————————————————/nWelcome to the poly terminal!/nType help for a list of commands/n————————————————————————/n'  # the text upon initialization
        self.text_contents_update = ''

        self.text_color = (0, 0, 0)

        self.read_json()

    def get_basic_values(self):
        return self.screen, self.transparent_color, self.width, self.height

    def draw_window(self):
        # main terminal window
        tx, ty, ti = self.terminal_location[0], self.terminal_location[1], self.terminal_size
        x1, y1, x2, y2 = tx - ti[0], ty - ti[1], tx + ti[0], ty + ti[1]
        brd_size = self.terminal_boarder_size

        # video file
        self.draw_video()

        if self.text_contents != self.text_contents_update:
            # text part
            self.draw_text_contents(x1, y1, x2, y2)
            self.text_contents_update = self.text_contents

        # flashing line...? in terminal window
        self.draw_flashing_line(tx, ty, ti, brd_size)

        # somethin else perhaps
        self.clock += (time.time() - self.clock_time) * 60
        self.clock_time = time.time()
        if self.clock > 60: self.clock = self.clock - 60

    def package_scroll_bar(self):
        tx, ty, ti = self.terminal_location[0], self.terminal_location[1], self.terminal_size
        x1, y1, x2, y2 = tx - ti[0], ty - ti[1], tx + ti[0], ty + ti[1]
        brd_size = self.terminal_boarder_size

        # main terminal window outer part overlay
        self.draw_rect_outer_line(x1, y1, x2, y2, brd_size, color_bg=self.terminal_color)

        # scroll wheel
        self.draw_scroll_wheel()

    def draw_text_contents(self, x1=None, y1=None, x2=None, y2=None):
        if x1 is None:
            tx, ty, ti = self.terminal_location[0], self.terminal_location[1], self.terminal_size
            x1, y1, x2, y2 = tx - ti[0], ty - ti[1], tx + ti[0], ty + ti[1]
        current_spacing = 0; increments = self.text_size + self.text_spacing; brd_size = self.terminal_boarder_size
        max_lines = math.floor((self.terminal_size[1]*2 - self.terminal_boarder_size*2) / (self.text_size + self.text_spacing)) - 1; max_line_cap = 0
        current_line_count = self.text_contents.count('/n')
        current_line_count -= max_lines - self.terminal_text_order; b = 0; c = 0; save = self.text_contents.count('/n')
        current_font = self.get_current_font('')

        if self.clear:
            self.screen.fill(self.transparent_color)
            tx, ty, ti = self.terminal_location[0], self.terminal_location[1], self.terminal_size
            x1, y1, x2, y2 = tx - ti[0], ty - ti[1], tx + ti[0], ty + ti[1]
            self.draw_rect_ext(x1, y1, x2, y2, self.terminal_color, self.terminal_back_boarder_size,
                               self.terminal_back_boarder_color)

            self.draw_background_image()
            pygame.display.flip(); self.clear = 0

        for index, a in enumerate(self.text_contents.split('/n')):
            c += len(a) + 2

            text_size = self.text_size
            extra_lines = 1
            if current_line_count <= 0 and max_line_cap <= max_lines:
                if "———image " in a:
                    a = a.replace('———image ', '').replace(" ——", '')
                    img_name = a; a = "亂數假文"; extra_lines = 1

            for i in range(0, extra_lines):
                if current_line_count <= 0 and max_line_cap <= max_lines:
                    col = self.text_color
                    if b in self.terminal_text_order_colors:
                        col = self.terminal_text_order_colors.get(b)

                    a = self.text_contents_special_cases(a, b)
                    current_font = self.get_current_font(a)

                    if a != '亂數假文':
                        self.draw_text(self.screen, a, text_size, col, x1 + brd_size, y1 + brd_size + current_spacing, current_font)

                    if not self.game:
                        if b == self.text_contents.count('/n') and a != '': self.draw_text_prediction(a, x1, brd_size, y1, current_spacing, current_font)
                    else:
                        self.draw_text_prediction(a, x1, brd_size, y1, current_spacing, current_font, game=True, game_text=self.game_text)

                    #if b == self.text_contents.count('/n'):
                        #pygame.display.update((x1 + brd_size, y1, x1 + brd_size + self.terminal_size[0], y1 + self.text_size))

                    self.y_spacing = current_spacing; current_spacing += increments + (text_size - self.text_size); max_line_cap += 1

            current_line_count -= 1; b += 1

        self.x_spacing = current_font.size(a)[0]
        if self.x_spacing >= self.terminal_size[0] * 2 - self.terminal_boarder_size * 2 - self.text_size:
            self.text_contents = self.text_contents[0: len(self.text_contents)-1]+'/n'+self.text_contents[len(self.text_contents)-1: len(self.text_contents)]
        if self.mouse_hold or self.mouse_draw_stay: self.mouse_draw = 0

        self.package_scroll_bar()

    def draw_text_prediction(self, a, x1, brd_size, y1, current_spacing, current_font, game=False, game_text=''):
        boom = a.split(' '); part = ''
        try:
            if 1 <= len(boom) <= 6 and not game:
                sim = '';
                score = 0
                if len(boom) == 1:
                    system = self.autocomplete['main_command']; s = 0
                else:
                    system = self.autocomplete['--main_argument']; s = 1
                    sect = len(boom) - 2
                    if self.autocomplete.get('--' + boom[0]):
                        system = self.autocomplete['--' + boom[0]]
                    if len(boom) > 3:
                        golg = self.autocomplete['--' + boom[0]]; found = 0
                        for i in golg:
                            if i.count('—'+str(sect)+'—'+boom[1]) > 0: found = 1
                        if found:
                            boom_1 = '—'.join(boom[s:len(boom) - 1])
                        else:
                            boom_1 = boom[1]; boom[s] = ' '.join(boom[s:len(boom)])
                    else:
                        boom_1 = boom[1]; boom[s] = ' '.join(boom[s:len(boom)])
                for i in system:
                    lun = len(boom[s])
                    if s > 0:
                        if i.count('—' + boom_1 + '—') > 0 and i[0:3] == '—' + str(sect) + '—':
                            i = i.replace(i[0:3] + boom_1 + '—', '');
                            boom[s] = boom[s].replace(boom_1 + ' ', '')
                            i = i.replace('—' + str(sect) + '——' + boom_1 + '—', '')
                            lun = len(boom[s])
                            if len(boom) > 3:
                                boom[s] = boom[3]
                                lun = len(boom[s])
                        else:
                            if sect > 1 and boom_1.count('—') > 0: i = ''
                    if difflib.SequenceMatcher(a=boom[s].lower(), b=i.lower()).ratio() > score and i[0:lun].lower() == boom[s].lower():
                        sim = i; score = difflib.SequenceMatcher(a=boom[s].lower(), b=i.lower()).ratio()
                part = sim[lun:]
                if part != '':
                    self.draw_text(self.screen, part, self.text_size, OLIVINE, x1 + brd_size + current_font.size(a)[0],
                                   y1 + brd_size + current_spacing, current_font)
        except KeyError: pass
        self.autocomplete_text = part

    def text_contents_special_cases(self, text, current_space):
        # Image processing loading
        if self.terminal_img_background_loading:
            if self.text_contents.count('/n') <= current_space:
                text = text.replace('.', '')
                for b in range(0, math.ceil(self.clock / 20)):
                    text = text + '.'
                self.text_contents_update = text
        return text

    def draw_text_drag(self, text, pixel_size, y_spacing, font):
        mos, mos_real = self.mouse_click_location, self.mouse_click_location_realtime
        start_mos = mos; end_mos = mos_real; check_mos = mos_real
        one_space = self.text_spacing + self.text_size + 2
        if mos_real[1] < mos[1]: start_mos = mos_real
        if mos_real[1] == mos[1] and mos_real[0] < mos[0]: start_mos = mos_real
        if start_mos == mos_real:
            end_mos = mos; check_mos = mos_real

        a = self.terminal_location[0] - self.terminal_size[0] + self.terminal_boarder_size
        c = pixel_size

        if y_spacing < check_mos[1] < y_spacing + one_space:
            if check_mos[0] < a:
                c = 0
            if check_mos[0] > a and check_mos[0] < a + pixel_size:
                c = check_mos[0] - a
                size = 0
                for i in text:
                    size += font.size(i)[0]
                    if size > c:
                        c = size; break

        pygame.draw.rect(self.screen, self.mouse_text_background_color, (a, y_spacing, c, self.text_size))
        pygame.display.update(a, y_spacing, c, self.text_size)

    def get_text_drag(self, current_line, text, pixel_size, y_spacing, font):
        mos, mos_real = self.mouse_click_location, self.mouse_click_location_realtime
        one_space = self.text_spacing + self.text_size + 2
        start_mos = mos; end_mos = mos_real
        if mos_real[1] < mos[1]: start_mos = mos_real
        if mos_real[1] == mos[1] and mos_real[0] < mos[0]: start_mos = mos_real
        if start_mos == mos_real: end_mos = mos

        if start_mos[1] < self.terminal_location[1] - self.terminal_size[1] + self.terminal_boarder_size:
            self.mouse_draw = 1
        if y_spacing < start_mos[1] < y_spacing + one_space:
            self.mouse_draw = 1
        if self.mouse_draw:
            if end_mos[1] < y_spacing:
                self.mouse_draw = 0

    def get_current_font(self, text):
        def has_glyph(font, glyph):
            for table in font['cmap'].tables:
                if ord(glyph) in table.cmap.keys():
                    return True
            return False
        if len(text) >= 1:
            if has_glyph(self.ttfont, text[0]):
                return self.font
            return self.fallback_font
        return self.font

    # IMAGE
    def draw_image(self, surface, image_path, size, x, y, index):
        try:
            if str(image_path)+str(index) in self.cached_images:
                img = self.cached_images.get(str(image_path)+str(index))
                img_size = self.cached_images.get(str(image_path)+str(index)+" size")
                img_fit = self.cached_images.get(str(image_path)+str(index)+" fit")
            else:
                img = pygame.image.load(image_path)
                img_size = img.get_size()
                img_fit = img_size[1] / size
                img_size = [img_size[0]/img_fit, img_size[1]/img_fit]
                img = pygame.transform.rotozoom(img, 0, 1/img_fit)

                self.cached_images[str(image_path)+str(index)] = img
                self.cached_images[str(image_path)+str(index)+" size"] = img_size
                self.cached_images[str(image_path)+str(index)+" fit"] = img_fit

            bottom_y = self.terminal_location[1] + (self.terminal_size[1]*2)
            if (bottom_y - y)/img_fit < img_size[1]:
                img_size[1] = (bottom_y - y)/img_fit
            if y < bottom_y:
                img = img.subsurface((0, 0, img_size[0], img_size[1]))
                surface.blit(img, (x, y), (0, 0, img_size[0], img_size[1]))
                pygame.display.update(x, y, x + img_size[0], y + img_size[1])
        except Exception as msg:
            print(msg)

    def draw_text(self, surface, text, size, color, x, y, font):

        def draw_text_real(surface, font, text, color, x, y):
            text_surf = font.render(str(text), True, color)
            text_rect = text_surf.get_rect()
            text_rect.topleft = (x, y)

            a1, a2 = text_rect[0], text_rect[1]
            a3, a4 = text_rect[2], text_rect[3]
            cords = text_rect.topleft
            side_step = self.terminal_size[0]*2 - self.scroll_wheel_size - self.terminal_back_boarder_size - self.terminal_boarder_size - a3 - (a1-(self.terminal_location[0] - self.terminal_size[0]))

            surface.blit(self.subsurface, text_rect.topleft, (a1 - (self.terminal_location[0] - self.terminal_size[0]), a2 - (self.terminal_location[1] - self.terminal_size[1]), a3+side_step, a4+2))
            surface.blit(text_surf, (a1, a2, a3, a4))

            pygame.display.update(a1, a2, a3+side_step, a4+2)

        if '—' not in text:
            draw_text_real(surface, font, text, color, x, y)
        else:
            scuffed_text = text.split('—')
            box = []; box_content = ''; counter = 0

            for a in scuffed_text:
                counter += 1
                if a == '':
                    box_content = box_content + '—'
                else:
                    if box_content.count('—') > 0:
                        box.append(box_content); box_content = ''
                    box.append(a)
                if counter == len(scuffed_text) and box_content != '':
                    box.append(box_content)

            xx = x
            for a in box:
                col = color
                if a.count('—') > 0: col = LIGHT_CORAL
                draw_text_real(surface, font, a, col, xx, y)
                xx += font.size(a)[0]

    def draw_video(self):
        if self.video_show:
            if self.video_clip is not None:
                cords = self.terminal_location; a = self.terminal_size
                b = self.video_size; c = (int(a[0]*2/100*b), int(a[1]*2/100*b))
                self.video_clip.resize(c)

                if self.video_show:
                    self.video_clip.draw(self.screen, (int(cords[0] - (c[0]-a[0])), int(cords[1] - (c[1]-a[1]))))
                    pygame.display.update((cords[0] - (c[0]-a[0]), cords[1] - (c[1]-a[1]), a[0]*2/100*b, a[1]*2/100*b))

                if self.video_clip is not None and not self.video_clip.active or self.video_clip is None:
                    self.video_clip = None; self.clear = True; self.text_contents_update = "";

    def draw_rect_ext(self, x1, y1, x2, y2, color_bg=BLACK, outline=0, color_outline=BLACK, alpha=1):
        if outline != 0:
            pygame.draw.rect(self.screen, color_outline, (x1 - outline/2, y1 - outline/2, x2 - x1 + outline, y2 - y1 + outline))
        pygame.draw.rect(self.screen, color_bg, (x1, y1, x2 - x1, y2 - y1))

    def draw_rect_outer_line(self, x1, y1, x2, y2, width, color_bg=BLACK):
        pygame.draw.rect(self.screen, color_bg, (x1, y1, x2 - x1, width))
        pygame.draw.rect(self.screen, color_bg, (x1, y2 - width, x2 - x1, width))
        pygame.draw.rect(self.screen, color_bg, (x1, y1, width, y2 - y1))
        pygame.draw.rect(self.screen, color_bg, (x2 - width, y1, width, y2 - y1))

    def draw_flashing_line(self, tx, ty, ti, brd_size):
        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.window_name and self.terminal_text_order >= 0:
            a = self.terminal_text_position
            rect = (
                tx + brd_size + a[0] - ti[0] + self.x_spacing, ty + brd_size + a[1] - ti[1] + self.y_spacing,
                self.flashing_line_width, self.pixel_text_size
            )
            if self.flashing_line_tick < 0.5:
                pygame.draw.rect(self.screen, self.flashing_line_color, rect)
                if self.flashing_line_tick < 0: pygame.display.update(rect)
                self.flashing_line_tick += self.flashing_line_tick_spd * (time.time() - self.flashing_line_time)
                if self.flashing_line_tick >= 0.5: pygame.display.update(rect)
            else:
                self.flashing_line_tick += self.flashing_line_tick_spd * (time.time() - self.flashing_line_time)
                pygame.draw.rect(self.screen, self.terminal_color, rect)
                if self.flashing_line_tick >= 1: pygame.display.update(rect)
            if self.flashing_line_tick > 1:
                self.flashing_line_tick = 0
            self.flashing_line_time = time.time()

    def draw_scroll_wheel(self):
        p1, p2 = self.terminal_location
        x1, y1, y2 = self.scroll_wheel_position  # relative to terminal
        max_lines = math.floor((self.terminal_size[1] * 2 - self.terminal_boarder_size * 2) / (self.text_size + self.text_spacing)) - 1
        line_count = self.text_contents.count('/n'); length = 1

        pygame.draw.rect(self.screen, self.scroll_wheel_color_bg, (p1 + x1 - self.scroll_wheel_size, p2 - y1, self.scroll_wheel_size, y2))

        if line_count > max_lines:
            length = 1 - ((1-self.scroll_wheel_min_box_size) * ((line_count - max_lines) / self.scroll_wheel_lines_before_min_box))
            if length < self.scroll_wheel_min_box_size: length = self.scroll_wheel_min_box_size

        def relativity():
            if self.terminal_text_order != 0:
                return math.floor(y2/(line_count-max_lines)*abs(self.terminal_text_order))
            else: return 0

        relative_text = relativity()

        pos1, pos2, wid, height = p1 + x1 - self.scroll_wheel_size, p2 - y1 + (1 - length) * y2 - (
                    relative_text * (1 - length)), self.scroll_wheel_size, length * y2

        if line_count > max_lines:
            if pygame.mouse.get_pressed()[0]:
                pass
            else: self.scroll_wheel_hook = False

        pygame.draw.rect(self.screen, self.scroll_wheel_color, (pos1, pos2, wid, height))
        pygame.display.update((p1 + x1 - self.scroll_wheel_size, p2 - y1, self.scroll_wheel_size, y2))

    def create_background_image(self):
        red, g, blue = self.terminal_img_background_overlay_color; name = self.terminal_img_background_name

        self.terminal_img_backgroundz_loading = 1

        temp_location = self.path+'\\content\\temporary_content\\'

        # cutoff
        main_img = Image.open(self.terminal_img_background_location + self.terminal_img_background_name + '.png')
        xx, yy = main_img.width, main_img.height
        new_im = Image.new('RGBA', (int(xx/100*(100-self.terminal_img_background_side_cutoff)), yy), (red, g, blue, 255))
        throw = main_img.crop((0, 0, int(xx/100*(100-self.terminal_img_background_side_cutoff)), yy))
        new_im.paste(main_img)

        try: os.remove(self.terminal_img_background_saved_location + name.replace('.png', '') + '_FINISHED.png')
        except FileNotFoundError: pass

        new_im.save(self.terminal_img_background_saved_location + name.replace('.png', '') + '_FINISHED.png', 'PNG')

        main_img = Image.open(self.terminal_img_background_saved_location + name.replace('.png', '') + '_FINISHED.png')

        self.terminal_img_background_scale = main_img.size
        w, h = main_img.size

        increments = self.terminal_img_background_increments; refinement = self.terminal_img_background_refinement
        a = math.floor(255 * self.terminal_img_background_overlay)
        def create_strip(a1, a2, a3, a4, unique_numb='x', reverse=False):
            if reverse: aa = refinement-b
            else: aa = b
            z = 1 - ((1-self.terminal_img_background_overlay) / refinement * aa)
            img = Image.new('RGBA', (w, h), (red, g, blue, int(z * 255))).crop((a1, a2, a3, a4))
            throw = main_img.crop((a1, a2, a3, a4))
            throw.paste(img, (0, 0), img)
            throw.save(temp_location+name+'(UWU)['+str(b)+unique_numb+'].png', 'PNG')

        for b in range(0, refinement):  # create single blur strips in seperate files
            create_strip(int(w / increments / refinement * b), 0, int(w / increments / refinement * (b+1)), h)

        # general / whole picture blur part...
        img = Image.new('RGBA', (w, h), (red, g, blue, a))
        throw = main_img.crop((int(w / increments), 0, int(w), h))
        throw.paste(img, (0, 0), img)
        throw.save(temp_location+name+'(UWU)['+str(refinement)+'x].png', 'PNG')

        image_names = ["" for x in range(refinement + 1)]
        for b in range(0, refinement + 1): image_names[b] = temp_location + name + '(UWU)[' + str(b) +'x'+ '].png'
        print(image_names[:])
        images = [Image.open(x) for x in image_names]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGBA', (total_width, max_height), (red, g, blue, 255))

        self.terminal_img_background_loading = 0

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        for b in image_names:
            os.remove(b)

        new_im.save(self.terminal_img_background_saved_location+name.replace('.png', '')+'_FINISHED.png', 'PNG')

        images.clear()
        main_img.close()

        gc.collect()

    def calculate_img_background(self):
        w, h = self.terminal_img_background_scale
        w_relative, h_relative = (self.terminal_size[0]-self.scroll_wheel_size-self.terminal_boarder_size) / w, self.terminal_size[1] / h
        if abs(1 - w_relative) > abs(1 - h_relative):
            scale = w_relative
        else: scale = h_relative
        scale = h_relative
        if self.width != self.terminal_size[0]*2 or self.height != self.terminal_size[1]*2:
            while w * scale + self.scroll_wheel_size > self.terminal_size[0]: scale -= 0.01

        image = pygame.transform.scale(self.image, (w * scale * 2, h * scale * 2))

        return image, w, h, scale

    def draw_background_image(self):
        image, w, h, scale = self.terminal_img_background_package
        x, y = self.terminal_location[0] + (self.terminal_size[0] - (w*scale*2)), \
            self.terminal_location[1] - self.terminal_size[1] + ((self.terminal_size[1]*2 - (h*scale*2))/2)
        self.screen.blit(image, (x, y))

    def setup_autocomplete(self):
        for k in self.autocomplete:
            if k[:-(len(k)-2)] == '--':
                autocomplete_tmp = []

                numb = ''; name = ''
                if k.count('â€”') > 0:
                    splits = k.split('â€”')
                    numb = '—' + splits[1] + '—';
                    name = splits[2] + '—' + splits[3] + '—'

                for i in self.autocomplete[k]:
                    if i[len(i)-5:] != '.json':
                        if os.path.exists(self.path+i):
                            autocomplete_tmp.append(os.listdir(self.path+i))
                        else: autocomplete_tmp.append([i])
                    else:
                        with open(self.path+i) as json_file:
                            tmp = json.load(json_file)
                        for ii in tmp.keys():
                            autocomplete_tmp.append([ii])
                            for jj in tmp[ii].keys():
                                autocomplete_tmp.append(['—1—'+'—'+ii+'—'+jj])
                flattened = [j for sub in autocomplete_tmp for j in sub]; finished = []
                for q in flattened: finished.append(numb+name+q.replace('.mp4', '').replace('.png', ''))
                if numb + name == '': self.autocomplete[k] = finished
                else:
                    k = splits[0]
                    self.autocomplete[k] = self.autocomplete[k] + finished

    def read_json(self):
        with open(self.path+'\\content\\json_data\\data.json') as json_file:
            data = json.load(json_file)
        with open(self.path+'\\content\\json_data\\autocomplete.json') as json_file:
            self.autocomplete = json.load(json_file)

        self.setup_autocomplete()
        self.autocomplete_text = ''

        self.terminal_location = data['win']['position']
        self.terminal_size = data['win']['size']
        self.terminal_size[0] = self.terminal_size[0] / 2
        self.terminal_size[1] = self.terminal_size[1] / 2
        self.terminal_boarder_size = int(data['win']['border-size'])
        self.terminal_color = data['win']['color']

        self.terminal_back_boarder_size = 6
        self.terminal_back_boarder_color = RICH_BLACK

        self.terminal_font = self.path+"\\content\\fonts\\Roboto-Regular.ttf"
        self.terminal_fallback_font = self.path+"\\content\\fonts\\NotoSansSymbols-Regular-Subsetted.ttf"
        self.terminal_text_position = (0, 0)
        self.terminal_text_order = 0
        if self.text_color != data['win']['text-color']:
            self.terminal_text_order_colors = {
                0: SANDY_BROWN,
                1: YELLOW,
                2: YELLOW,
                3: SANDY_BROWN
            }

        # main terminal text information
        self.text_size = int(data['win']['text-size'])
        self.text_color = data['win']['text-color']
        self.pixel_text_size = self.text_size  # the y direction
        self.text_spacing = int(data['win']['text-spacing'])

        self.font = pygame.font.Font(self.terminal_font, self.text_size)
        self.ttfont = TTFont(self.terminal_font)
        self.fallback_font = pygame.font.Font(self.terminal_fallback_font, self.text_size)

        self.mouse_text_background_color = CHARCOAL
        self.mouse_click_location = [0, 0]
        self.mouse_click_location_realtime = [0, 0]
        self.mouse_hold = 0
        self.mouse_draw = 0; self.mouse_draw_stay = 0

        # flashing line
        self.flashing_line_width = 3
        self.flashing_line_tick = 0
        self.flashing_line_tick_spd = 1
        self.flashing_line_time = time.time()
        self.flashing_line_color = data['win']['cursor-color']
        self.y_spacing = 0; self.x_spacing = 0

        # scroll wheel (currently the position is relative to the terminal window (furthest right))
        self.scroll_wheel_color = ANTIQUE_WHITE
        self.scroll_wheel_color_bg = CHARCOAL
        self.scroll_wheel_position = (
        self.terminal_size[0], self.terminal_size[1], self.terminal_size[1] * 2)  # x, y, y2
        self.scroll_wheel_size = 10
        self.scroll_wheel_lines_before_min_box = 50  # how many lines before box gets to the smallest size
        self.scroll_wheel_min_box_size = 0.1  # 0 - 1 is essentially 0-100% y size
        self.scroll_wheel_box_location = 0
        self.scroll_wheel_hold_y = 0; self.scroll_wheel_y_past = 0
        self.scroll_wheel_hook = False
        self.scroll_wheel_sensitivity = 4

        # terminal image background
        self.terminal_img_background_location = self.path+'\\content\\images\\'
        self.terminal_img_background_saved_location = self.path+'\\content\\saved_content\\'
        self.terminal_img_background_name = data['img']['name']
        self.terminal_img_background_size = 1  # 1 = scales until width or height == terminal
        self.terminal_img_background_overlay = float(data['img']['overlay'])  # 1 = fully covered, 0 = fully visible
        self.terminal_img_background_overlay_color = self.terminal_color

        self.terminal_img_background_loading = 0

        self.terminal_img_background_increments = float(data['img']['increments'])  # what % of the image will have a gradient ( 2 = 50%, 1 = 100%, 5 = 20% )

        self.terminal_img_background_side_cutoff = float(data['img']['side-cutoff'])   # what % of the image right side will be cutoff

        self.terminal_img_background_refinement = int(data['img']['refinement'])  # gradient refinement level ( bigger number == more refined )

        if len(glob.glob(
                self.terminal_img_background_saved_location + self.terminal_img_background_name + '_FINISHED.png')) <= 0:
            self.create_background_image()

        with Image.open(self.terminal_img_background_saved_location + self.terminal_img_background_name + '_FINISHED.png') as img:
            self.terminal_img_background_scale = img.size

        self.image = pygame.image.load(
            self.terminal_img_background_saved_location + self.terminal_img_background_name + '_FINISHED.png').convert()

        self.terminal_img_background_package = self.calculate_img_background()

        # songs / memes / video showcase
        if hasattr(self, 'video_clip'):
            print("oppai")
            if self.video_clip is not None: self.video_clip = None
        self.video_clip = None
        self.video_show = int(data['sound']['video'])
        self.video_size = int(data['sound']['size'])  # 1 - 100 %

        # misc
        self.cooldown = 0
        self.clock_time = time.time()
        self.clock = 0  # 60 frame variable
        self.get_amount = int(data['win']['get-amount'])  # how many get elements per line break
        self.clear = 0
        self.game = False  # is a game currently on
        self.game_text = ''

        # background block ¯\_(ツ)_/¯
        self.screen.fill(self.transparent_color)
        tx, ty, ti = self.terminal_location[0], self.terminal_location[1], self.terminal_size
        x1, y1, x2, y2 = tx - ti[0], ty - ti[1], tx + ti[0], ty + ti[1]
        self.draw_rect_ext(x1, y1, x2, y2, self.terminal_color, self.terminal_back_boarder_size,
                           self.terminal_back_boarder_color)

        # background image
        self.draw_background_image()
        self.subsurface = self.screen.subsurface(pygame.Rect(x1, y1, x2, y2)).copy()

        # printing images ( cached images )
        self.cached_images = {}

        pygame.display.flip()

        print('window variable initialization finished')

