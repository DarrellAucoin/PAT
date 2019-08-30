# !/usr/bin/env python3
# encoding: utf-8

#from snipsTools import SnipsConfigParser

from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import os
import subprocess
# import PIL
# from PIL import Image
import pygame
import time
import pandas as pd
import sys
# from numpy import random
# import matplotlib.pyplot as plt
# import matplotlib as mpl
# from pylab import imshow, show
# from imageio import imread
# import visvis as vv
# from pylab import imshow, show


def insert_image(image, delay=7):
    if type(image) == str:
        if os.path.isfile(image):
            # subprocess.Popen(['xdotool', 'key', "Escape"])
            subprocess.Popen(['pqiv', '--fullscreen', "--hide-info-box", "--scale-images-up", image])
        else:
            # subprocess.Popen(['xdotool', 'key', "Escape"])
            subprocess.Popen(['pqiv', '--fullscreen', "--hide-info-box", "--scale-images-up", BG_IMAGE])
    elif type(image) == list:
        images = [img for img in image if os.path.isfile(img)]
        subprocess.Popen(['pqiv', '--fullscreen', "--hide-info-box", "--scale-images-up",
                          "--slideshow", "-d", delay, *images])



CONFIG_INI = "config.ini"
ROOT_DIR = "/home/pi/PAT"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
screen_size = (1024, 600)
PAT_position = (-250, 100)
DEBUG = False
BG_IMAGE = "space.jpg"
'''
if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter
    tkinter = Tkinter #I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter
from PIL import Image, ImageTk
'''
'''
def showPIL(pilImage):
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    canvas = tkinter.Canvas(root,width=w,height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2,h/2,image=image)
    root.mainloop()
'''

def play_mp3(path):
    subprocess.Popen(['mpg123', '-q', path]).wait()
    # subprocess.Popen([f'ssh pi@localhost "mpg123 -q {path}']).wait()


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location



'''
class ScreenSingleTone(object):
    __instance = None


    def __new__(cls):
        if ScreenSingleTone.__instance is None:
            # ScreenSingleTone.__instance = object.__new__(cls)
            ScreenSingleTone.__instance = pygame.display.set_mode(screen_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
            pygame.display.set_caption('PAT')
        return ScreenSingleTone.__instance
'''



'''
class PAT_simple:

    def __init__(self, position, screen=None, mp3_only=False):
        # self.screen = None
        self.gamer_girl = None
        self.frames = None
        self.screen_on = pygame.get_init()
        self.screen = screen
        self.mp3_only = mp3_only
        self.position = position
        self.BG = None
        self.frame_i = 0
        self.start_time = time.time()
        # self.pygame_initalized = screen_on
        if pygame.get_init():
            self._initialize()

    def _initialize(self):
        # self.screen = ScreenSingleTone()
        self.gamer_girl = [
            pygame.image.load(os.path.join(ROOT_DIR, f'PAT/png/frame_{i}_delay-0.2s.png')).convert_alpha() for i in
            range(14)]
        self.frames = self.gamer_girl
        # self.position = position
        self.BG = Background(os.path.join(ROOT_DIR, BG_IMAGE), [0, 0])
        self.screen.fill(BLACK)
        self.screen.blit(self.BG.image, self.BG.rect)
        self.render_frame(0)

    def talk_animation(self, response, intent="explain"):
        # if not self.screen_on:
        #     return None
        print("inside talk_animation")
        # print("in talk_animation")
        # response = response[["response_text", "response_mp3", "animation", "image", "img_x", "img_y"]]
        response = response[["response_text", "response_mp3", "image", "img_x", "img_y"]]
        self.start_time = time.time()
        self.frame_i = 0
        self.gamer_girl = None
        self.frames = None
        for index, row in response.iterrows():
            file = os.path.join(ROOT_DIR, 'intents', intent.lower(), row["response_mp3"])
            if row["image"] is not None and type(row["image"]) == str:
                image = os.path.join(ROOT_DIR, "images", row["image"])
            else:
                image = None
            print("image:", image)
            if pygame.mixer.get_init():
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
            if pygame.get_init():
                self.screen.fill(BLACK)
                self.screen.blit(self.BG.image, self.BG.rect)
                if image is not None and type(image) == str:
                    try:
                        img_x = int(row["img_x"])
                        img_y = int(row["img_y"])
                    except:
                        img_x = 0
                        img_y = 300
                    self.insert_image(image=image, img_pos=(int(img_x), int(img_y)))
                print("finished inserting image")
                self.render_frame(self.frame_i)
                print("rendering the frame")
                while pygame.mixer.music.get_busy():
                    self._animate()
            elif self.mp3_only:
                if image is not None and type(image) == str:
                    try:
                        img = Image.open(image)
                        img.show()
                        # showPIL(img)
                    except:
                        print("image file not found:", image)
                try:
                    play_mp3(file)
                except:
                    print("mp3 file not found:", file)
                if image is not None and type(image) == str:
                    img.close()
                # time.sleep(3.0)

        if pygame.get_init():
            self.screen.fill(BLACK)
            self.screen.blit(self.BG.image, self.BG.rect)
            self.render_frame(0)
            self.start_time = time.time()


    def _pygame_initialize(self):
        self.screen = pygame.display.set_mode(screen_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption('PAT')
        self.gamer_girl = [
            pygame.image.load(os.path.join(ROOT_DIR, f'PAT/png/frame_{i}_delay-0.2s.png')).convert_alpha() for i in
            range(14)]
        self.BG = Background(os.path.join(ROOT_DIR, BG_IMAGE), [0, 0])
        self.frames = self.gamer_girl


        self.screen.fill(BLACK)
        self.screen.blit(self.BG.image, self.BG.rect)
        self.render_frame(0)
        self.start_time = time.time()

    def render_frame(self, i):
        self.screen.blit(self.frames[i], self.position)
        pygame.display.update()

    def _animate(self):
        if time.time() - self.start_time >= 0.2:
            self.start_time = time.time()
            self.frame_i = (self.frame_i + 1) % len(self.frames)
            self.render_frame(self.frame_i)

    def insert_image(self, image, img_pos):
        img = pygame.image.load(image)
        self.screen.blit(img, img_pos)
'''

class FAQ_PAT(object):
    """Class used to wrap action code with mqtt connection

        Please change the name refering to your application
    """

    def __init__(self, pygame_on=False, mixer_mp3_only=False, mp3_only=False):
        # get the configuration if needed
        '''
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None
        '''
        print("In __init__ of Template")

        self.config = None
        self.PAT = None
        self.frame_i = 0
        self.tables = {}
        self.screen = None
        self.BG = None
        self.gamer_girl = None
        self.frames = None
        self.pygame_on = pygame_on
        self.mixer_mp3_only = mixer_mp3_only
        self.mp3_only = mp3_only
        self.start_time = time.time()
        self.PAT_position = PAT_position

        self.intents = ["Explain", "Purpose", "Availability", "hello", "Show_Menu"]
        self._running = True
        # start listening to MQTT
        self._get_tables()
        # if pygame.get_init():
        #     self._initialize()
            # self._display_surf = ScreenSingleTone()
            # self.PAT = PAT_simple(self.PAT_position, screen_on=True, screen=self._display_surf)
        # else:
        #     self.PAT = PAT_simple(self.PAT_position, screen_on=False, mp3_only=self.mp3_only)


        # print("end of __init__ of Template")


    def _initialize(self):
        pygame.init()
        # pygame.mixer.init()
        self.screen = pygame.display.set_mode(screen_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption('PAT')
        self.BG = Background(os.path.join(ROOT_DIR, BG_IMAGE), [0, 0])

        self.gamer_girl = [
            pygame.image.load(os.path.join(ROOT_DIR, f'PAT/png/frame_{i}_delay-0.2s.png')).convert_alpha() for i in
            range(14)]
        self.frames = self.gamer_girl
        self._reset_animation()

    @staticmethod
    def _shutdown_pygame():
        pygame.mixer.quit()
        pygame.quit()

    def _render_frame(self, i):
        self.screen.blit(self.frames[i], self.PAT_position)
        pygame.display.update()

    def _reset_animation(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.BG.image, self.BG.rect)
        self.frame_i = 0
        self._render_frame(self.frame_i)
        self.start_time = time.time()

    def _animate(self):
        if time.time() - self.start_time >= 0.2:
            self.start_time = time.time()
            self.frame_i = (self.frame_i + 1) % len(self.frames)
            self._render_frame(self.frame_i)

    # def insert_image(self, image, img_pos):
    #     self.screen.fill(BLACK)
    #     self.screen.blit(self.BG.image, self.BG.rect)
    #     img = pygame.image.load(image)
    #     self.screen.blit(img, img_pos)
    #     self._render_frame(self.frame_i)

    def show_image(self, image, img_x=300, img_y=0):
        if image is None or type(image) not in [str, list]:
            return None
        elif pygame.get_init():
            try:
                img_x = int(img_x)
                img_y = int(img_y)
            except ValueError:
                img_x = 300
                img_y = 0
            self.screen.fill(BLACK)
            self.screen.blit(self.BG.image, self.BG.rect)
            image = image if type(image) is str else image[0]
            img = pygame.image.load(image)
            self.screen.blit(img, (img_x, img_y))
            self._render_frame(self.frame_i)
        elif self.mp3_only or self.mixer_mp3_only:
            try:
                insert_image(image)
                # img = Image.open(image)
                # img.show()
                # showPIL(img)
            except:
                print("image file not found:", image)

    def _play_mp3(self, file):
        if pygame.mixer.get_init():
            print("inside mixer")
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            print("mixer still working")
        elif self.mp3_only:
            print("inside mp3only")
            subprocess.Popen(['mpg123', '-q', file])#.wait()
            print("should be playing mp3 now")
        # else:
        #     time.sleep(60)

    def talk_animation(self, response, intent="explain"):
        if not self.pygame_on and not self.mp3_only and not self.mixer_mp3_only:
            return None
        print("inside talk_animation")
        # print("in talk_animation")
        # response = response[["response_text", "response_mp3", "animation", "image", "img_x", "img_y"]]
        response = response[["response_text", "response_mp3", "image", "img_x", "img_y"]]
        self.start_time = time.time()
        self.frame_i = 0
        for index, row in response.iterrows():
            file = os.path.join(ROOT_DIR, 'intents', intent.lower(), row["response_mp3"])
            if row["image"] is not None and type(row["image"]) == str:
                if ";" in row["image"]:
                    images = [os.path.join(ROOT_DIR, "images", img) for img in row["image"]]
                    image = [img for img in images if os.path.isfile(os.path.join(ROOT_DIR, "images", img))]
                else:
                    image = os.path.join(ROOT_DIR, "images", row["image"])
            else:
                image = os.path.join(ROOT_DIR, "images", BG_IMAGE)
            print("image:", image)
            self.show_image(image, img_x=row["img_x"], img_y=row["img_y"])
            self._play_mp3(file=file)
            if pygame.get_init() and pygame.mixer.get_init():
                while pygame.mixer.music.get_busy():
                    self._animate()
        if pygame.get_init():
            self._reset_animation()

    @staticmethod
    def _get_slots(intent_message, slot_names=[]):
        slots = {}
        for slot_name, v in intent_message.slots.items():
            # Attributes of slot_value: from_c_repr, value, value_type
            slots[slot_name] = v[-1].slot_value.value.value
            # also has attributes confidence_score, entity, from_c_repr, range_end, range_start, raw_value, slot_name
            # slot_value
        for slot_name in slot_names:
            if slot_name not in slots.keys():
                slots[slot_name] = "default"
        return slots

    def _get_tables(self):
        print("in _get_tables()")
        for intent in self.intents:
            self.tables[intent] = pd.read_csv(os.path.join(ROOT_DIR, "intents", f"{intent.lower()}.csv"))
            print(self.tables[intent].columns)
        print("got all tables")

    def intent_explain(self, hermes, intent_message):
        hermes.publish_end_session(intent_message.session_id, "")
        slots = self._get_slots(intent_message, slot_names=["Components"])
        # print("slots:", slots)
        self.play_explain(slots["Components"])
        # hermes.publish_start_session_notification(intent_message.site_id, "", "")

    def play_explain(self, component):
        print("inside play_explain")
        response = self.tables["Explain"][self.tables["Explain"]["component"] == component]#.sort_values(by=["play_order"])

        self.talk_animation(response, intent="explain")

    def intent_purpose(self, hermes, intent_message):
        hermes.publish_end_session(intent_message.session_id, "")
        slots = self._get_slots(intent_message, slot_names=["Components", "People"])
        self.play_purpose(slots["Components"], slots["People"])
        hermes.publish_start_session_notification(intent_message.site_id, "", "")


    def play_purpose(self, component, people):
        response = self.tables["Purpose"][self.tables["Purpose"]["component"] == component and
                                          self.tables["Purpose"]["people"] == people]#.sort_values(by=["play_order"])
        self.talk_animation(response, intent="purpose")

    def intent_availability(self, hermes, intent_message):
        hermes.publish_end_session(intent_message.session_id, "")
        if len(intent_message.slots.Location) > 0:
            location = intent_message.slots.Location.first().value
        else:
            location = "default"
        self.play_availability(location)
        hermes.publish_start_session_notification(intent_message.site_id, "", "")

    def play_availability(self, location):
        response = self.tables["Availability"][self.tables["Availability"]["location"] \
                                               == location]#.sort_values(by=["play_order"])
        self.talk_animation(response, intent="Availability")

    def intent_bye(self, hermes, intent_message):
        hermes.publish_end_session(intent_message.session_id, "")
        self.play_bye()
        hermes.publish_start_session_notification(intent_message.site_id, "", "")
        # if need to speak the execution result by tts
        # Hermes.publish_start_session_notification(intent_message.site_id,
        #                                             "bye has been done")

    def play_bye(self):
        pass
        # self.PAT.talk_animation(response, intent="bye")

    def intent_hello(self, hermes, intent_message):
        hermes.publish_end_session(intent_message.session_id, "")
        self.play_hello()
        hermes.publish_start_session_notification(intent_message.site_id, "", "")

    def play_hello(self):
        pass
        # self.PAT.talk_animation(response, intent="hello")

    def intent_show_menu(self, hermes, intent_message):
        hermes.publish_end_session(intent_message.session_id, "")

        '''
        Not sure what to do here
        '''
        hermes.publish_start_session_notification(intent_message.site_id, "", "")
        pass


    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self, hermes, intent_message):
        if not pygame.get_init() and self.pygame_on:
            print("before initialization of pygame")
            self._initialize()
            print("after initialization of pygame")
        if (self.pygame_on or self.mixer_mp3_only) and not pygame.mixer.get_init():
            pygame.mixer.init()
        try:

            # if True:
            #     self._initialize()

            coming_intent = intent_message.intent.intent_name
            if ':' in coming_intent:
                coming_intent = coming_intent.split(":")[1]
            print("coming_intent:", coming_intent)
            if coming_intent == 'Explain':
                self.intent_explain(hermes, intent_message)
            elif coming_intent == 'Purpose':
                self.intent_purpose(hermes, intent_message)
            elif coming_intent == 'Availability':
                self.intent_availability(hermes, intent_message)
            elif coming_intent == 'hello':
                self.intent_hello(hermes, intent_message)
            elif coming_intent == 'bye':
                self.intent_bye(hermes, intent_message)
            elif coming_intent == 'Show_Menu':
                self.intent_show_menu(hermes, intent_message)

            # if pygame.get_init() and self.pygame_initalized:
            #     pygame.mixer.quit()
            #     pygame.quit()
        except Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)  # __str__ allows args to be printed directly,
            print("something got caught somewhere")
            if pygame.get_init():
                self._shutdown_pygame()
            sys.exit()
        finally:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        print(f'[Received] intent: {intent_message.intent.intent_name}')
        if DEBUG and pygame.get_init():
            self._shutdown_pygame()
        # terminate the session first if not continue
        # hermes.publish_start_session_notification(intent_message.site_id, "", "")
        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()


if __name__ == "__main__":
    pygame_on = False
    mixer_mp3_only = False
    mp3_only = False
    if "pygame" in sys.argv:
        pygame_on = True
    elif "mixer_mp3_only" in sys.argv:
        mp3_only = True
    elif "mp3_only" in sys.argv:
        mp3_only = True
    if "DEBUG" in sys.argv:
        DEBUG = True
    PAT_avatar = FAQ_PAT(pygame_on=pygame_on, mixer_mp3_only=mixer_mp3_only, mp3_only=mp3_only)
    PAT_avatar.start_blocking()
