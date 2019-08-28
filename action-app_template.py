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

def play_mp3(path):
    subprocess.Popen(['mpg123', '-q', path]).wait()


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
        print("in talk_animation")
        response = response[["response_text", "response_mp3", "animation", "image", "img_x", "img_y"]]
        self.start_time = time.time()

        if self.pygame_initalized:
            pygame.mixer.fadeout(0.25)
            self.frame_i = 0
        for index, row in response.iterrows():
            file = os.path.join(ROOT_DIR, 'intents', intent, row["response_mp3"])
            image = os.path.join(ROOT_DIR, "images", row["image"])
            print("image:", image)
            if self.pygame_initalized:
                song_end = pygame.USEREVENT + 1
                print("song_end:", song_end)
                running = True
                if image is not None and type(image) == str:
                    insert_image(screen=self.screen, image=image, img_pos=(row["img_x"], row["img_y"]))
                print("file", file)
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
                    img = Image.open(image)
                    img.show()
                play_mp3(file)
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
        self.PAT_position = (-200, 100)
        self.tables={}
        self.intents = ["Explain", "Purpose", "Availability", "hello", "Show_Menu"]
        self._running = True
        # start listening to MQTT
        self._get_tables()
        self.pygame_initalized = screen_on
        if self.pygame_initalized:
            self._display_surf = ScreenSingleTone()

        self.PAT = PAT_simple(self.PAT_position, screen_on=self.pygame_initalized)
        print("end of __init__ of Template")


    def _get_slots(self, intent_message, slot_names=[]):
        slots = {}
        print("slots:", intent_message.slots)
        print("slots dir:", dir(intent_message.slots))
        print("intents dir:", dir(intent_message.intent))
        for slot_name, v in intent_message.slots.items():
            # for k, v in slot.items():
            print("k:", slot_name)
            print("v:", dir(v))
            print("v:", v)
            for val in v:
                print(dir(val))
            # print(slot.slotName)
            print("slot type:")
            # print(slot, type(slot))
            print("attributes of slot_value", dir(v[-1].slot_value))
            # Attributes of slot_value: from_c_repr, value, value_type
            print("attributes of slot_value.value", dir(v[-1].slot_value.value))
            slots[slot_name] = v[-1].slot_value.value.value
            # also has attributes confidence_score, entity, from_c_repr, range_end, range_start, raw_value, slot_name
            # slot_value
            print(slots)
        for slot_name in slot_names:
            if slot_name not in slots.keys():
                slots[slot_name] = "default"
        return slots


    '''
    {
  "input": "Give me the weather in Paris today please",
  "intent": {
    "intentName": "SearchWeatherForecast",
    "probability": 0.8302662399999999
  },
  "slots": [
    {
      "entity": "locality",
      "slotName": "weatherForecastLocality",
      "rawValue": "Paris",
      "value": {
        "kind": "Custom",
        "value": "Paris"
      },
      "range": {
        "start": 23,
        "end": 28
      }
    },
    {
      "entity": "snips/datetime",
      "slotName": "weatherForecastStartDatetime",
      "rawValue": "today",
      "value": {
        "kind": "InstantTime",
        "value": {
          "grain": "Day",
          "precision": "Exact",
          "value": "2017-06-13 00:00:00 +00:00"
        }
      },
      "range": {
        "start": 29,
        "end": 34
      }
    }
  ]
}
    '''

    def _get_tables(self):
        print("in _get_tables()")
        for intent in self.intents:
            self.tables[intent] = pd.read_csv(os.path.join(ROOT_DIR, "intents", f"{intent.lower()}.csv"))
            print(self.tables[intent])
        print("got all tables")

    def intent_explain(self, hermes, intent_message):
        slots = self._get_slots(intent_message, slot_names=["Components"])
        print("slots:", slots)
        self.play_explain(slots["Components"])
        hermes.publish_end_session(intent_message.session_id, "")

    def play_explain(self, component):
        print("will this show up?")
        response = self.tables["Explain"][self.tables["Explain"]["component"] == component].sort_values(by=["play_order"])

        self.PAT.talk_animation(response, intent="explain")

    def intent_purpose(self, hermes, intent_message):
        slots = self._get_slots(intent_message, slot_names=["Components", "People"])
        self.play_purpose(slots["Components"], slots["People"])
        hermes.publish_end_session(intent_message.session_id, "")

    def play_purpose(self, component, people):
        response = self.tables["Purpose"][self.tables["Purpose"]["component"] == component and
                                          self.tables["Purpose"]["people"] == people].sort_values(by=["play_order"])
        self.PAT.talk_animation(response, intent="purpose")

    def intent_availability(self, hermes, intent_message):
        if len(intent_message.slots.Location) > 0:
            location = intent_message.slots.Location.first().value
        else:
            location = "default"
        self.play_availability(location)
        hermes.publish_end_session(intent_message.session_id, "")

    def play_availability(self, location):
        response = self.tables["Availability"][self.tables["Availability"]["location"] \
                                               == location].sort_values(by=["play_order"])
        response = self.cursor.fetchall()

        self.PAT.talk_animation(response, intent="Availability")

    def intent_bye(self, hermes, intent_message):
        self.play_bye()
        hermes.publish_end_session(intent_message.session_id, "")

        # if need to speak the execution result by tts
        # Hermes.publish_start_session_notification(intent_message.site_id,
        #                                             "bye has been done")

    def play_bye(self):
        pass
        # self.PAT.talk_animation(response, intent="bye")

    def intent_hello(self, hermes, intent_message):
        self.play_hello()
        hermes.publish_end_session(intent_message.session_id, "")

    def play_hello(self):
        pass
        # self.PAT.talk_animation(response, intent="hello")

    def intent_show_menu(self, hermes, intent_message):
        pass
        '''
        Not sure what to do here
        '''
        hermes.publish_end_session(intent_message.session_id, "")


    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self, hermes, intent_message):

        coming_intent = intent_message.intent.intent_name
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
            print("before initialization of pygame")
            pygame.init()
            pygame.mixer.init()
            print("after initialization of pygame")
            screen_on = True
        if "DEBUG" in sys.argv:
            DEBUG = True
        PAT_avatar = Template(screen_on=screen_on)
        h.subscribe_intents(PAT_avatar.master_intent_callback).start()
    # PAT_avatar = Template()
    # print("start Talking")
    # PAT_avatar.start_blocking()
    # print("end blocking")