# !/usr/bin/env python3
# encoding: utf-8

#from snipsTools import SnipsConfigParser

from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import os
import subprocess
# import PIL
from PIL import Image
import pygame
import time
import pandas as pd
import sys

CONFIG_INI = "config.ini"
ROOT_DIR = "/home/pi/PAT"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
screen_size = (1024, 600)
DEBUG = False

if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter
    tkinter = Tkinter #I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter
from PIL import Image, ImageTk


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


def play_mp3(path):
    subprocess.Popen(['mpg123', '-q', path]).wait()
    # subprocess.Popen([f'ssh pi@localhost "mpg123 -q {path}']).wait()


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

class ScreenSingleTone(object):
    __instance = None

    def __new__(cls):
        if ScreenSingleTone.__instance is None:
            ScreenSingleTone.__instance = object.__new__(cls)
            ScreenSingleTone.__instance = pygame.display.set_mode(screen_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
            pygame.display.set_caption('PAT')
        return ScreenSingleTone.__instance


def insert_image(screen, image, img_pos):
    img = pygame.image.load(image)
    screen.blit(img, img_pos)


class PAT_simple:

    def __init__(self, position, screen_on=False):
        self.screen = None
        self.gamer_girl = None
        self.frames = None
        self.screen_on = screen_on
        self.position = position
        self.BG = None
        self.frame_i = 0
        self.start_time = time.time()
        self.pygame_initalized = screen_on
        if screen_on:
            self._initialize()

    def _initialize(self):
        self.screen = ScreenSingleTone()
        self.gamer_girl = [
            pygame.image.load(os.path.join(ROOT_DIR, f'PAT/png/frame_{i}_delay-0.2s.png')).convert_alpha() for i in
            range(14)]
        self.frames = self.gamer_girl
        # self.position = position
        self.BG = Background(os.path.join(ROOT_DIR, 'wise_nebula.png'), [0, 0])
        self.screen.fill(WHITE)
        self.screen.blit(self.BG.image, self.BG.rect)
        self.render_frame(0)

    def talk_animation(self, response, intent="explain"):
        if not self.screen_on:
            return None
        print("inside talk_animation")
        # print("in talk_animation")
        # response = response[["response_text", "response_mp3", "animation", "image", "img_x", "img_y"]]
        response = response[["response_text", "response_mp3", "image", "img_x", "img_y"]]
        print("response table:\n", response)
        self.start_time = time.time()
        print("before fadout")
        if pygame.get_init():
            try:
                pygame.mixer.fadeout(0.25)
            except:
                print("mixer not fading out")
            self.frame_i = 0
        print("after fadout")
        for index, row in response.iterrows():
            print("will this show up? 1")
            print("row:", row)
            print("will this show up? 2")
            print("""row["response_mp3"]:""", dir(row))
            file = os.path.join(ROOT_DIR, 'intents', intent.lower(), row["response_mp3"])
            print("file:", file)
            if row["image"] is not None and type(row["image"]) == str:
                image = os.path.join(ROOT_DIR, "images", row["image"])
            else:
                image = None
            print("image:", image)
            if self.pygame_initalized:
                song_end = pygame.USEREVENT + 1
                # print("song_end:", song_end)
                running = True
                if image is not None and type(image) == str:
                    insert_image(screen=self.screen, image=image, img_pos=(row["img_x"], row["img_y"]))
                # print("file", file)
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
                self.screen.fill(WHITE)
                self.screen.blit(self.BG.image, self.BG.rect)
                self.render_frame(self.frame_i)
                while running:
                    events = pygame.event.get()
                    # for event in pygame.event.get():
                    self._animate()
                    if 0 == len(events):
                        continue
                    else:
                        for event in events:
                            self._animate()
                            if event.type == song_end:
                                running = False
                                break
            else:
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

        if self.pygame_initalized:
            self.screen.fill(WHITE)
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



class Template(object):
    """Class used to wrap action code with mqtt connection

        Please change the name refering to your application
    """

    def __init__(self, screen_on=False):
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
        self.tables={}
        self._display_surf = None
        self.PAT_position = (-200, 100)
        self.pygame_initalized = screen_on
        self.intents = ["Explain", "Purpose", "Availability", "hello", "Show_Menu"]
        self._running = True
        # start listening to MQTT
        self._get_tables()



        # print("end of __init__ of Template")


    def _get_slots(self, intent_message, slot_names=[]):
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
        hermes.publish_start_session_notification(intent_message.site_id, "", "")

    def play_explain(self, component):
        print("inside play_explain")
        response = self.tables["Explain"][self.tables["Explain"]["component"] == component]#.sort_values(by=["play_order"])

        self.PAT.talk_animation(response, intent="explain")

    def intent_purpose(self, hermes, intent_message):
        hermes.publish_end_session(intent_message.session_id, "")
        slots = self._get_slots(intent_message, slot_names=["Components", "People"])
        self.play_purpose(slots["Components"], slots["People"])
        hermes.publish_start_session_notification(intent_message.site_id, "", "")


    def play_purpose(self, component, people):
        response = self.tables["Purpose"][self.tables["Purpose"]["component"] == component and
                                          self.tables["Purpose"]["people"] == people]#.sort_values(by=["play_order"])
        self.PAT.talk_animation(response, intent="purpose")

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
        response = self.cursor.fetchall()

        self.PAT.talk_animation(response, intent="Availability")

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
        if not pygame.get_init() and self.pygame_initalized:
            print("before initialization of pygame")
            pygame.init()
            pygame.mixer.init()
            self._display_surf = ScreenSingleTone()
            self.PAT = PAT_simple(self.PAT_position, screen_on=self.pygame_initalized)
            print("after initialization of pygame")
        try:
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
            # terminate the session first if not continue
            # hermes.publish_start_session_notification(intent_message.site_id, "", "")
            # if pygame.get_init() and self.pygame_initalized:
            #     pygame.mixer.quit()
            #     pygame.quit()
        except:
            print("something got caught somewhere")
            if pygame.get_init():
                pygame.mixer.quit()
                pygame.quit()
            sys.exit()
        print(f'[Received] intent: {intent_message.intent.intent_name}')
        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()


if __name__ == "__main__":
    screen_on = False

    with Hermes(MQTT_ADDR) as h:
        if len(sys.argv) > 1 and "pygame" in sys.argv:
            screen_on = True
        if "DEBUG" in sys.argv:
            DEBUG = True
        PAT_avatar = Template(screen_on=screen_on)
        h.subscribe_intents(PAT_avatar.master_intent_callback).start()
    # PAT_avatar = Template()
    # print("start Talking")
    # PAT_avatar.start_blocking()
    # print("end blocking")