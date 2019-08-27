# !/usr/bin/env python3
# encoding: utf-8

#from snipsTools import SnipsConfigParser

from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import sqlite3 as sql
import os
import subprocess
import pygame
import time

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

    def __init__(self, position):
        if not DEBUG:
            self.screen = ScreenSingleTone()
            self.gamer_girl = [
                pygame.image.load(os.path.join(ROOT_DIR, f'PAT/png/frame_{i}_delay-0.2s.png')).convert_alpha() for i in
                range(14)]
            self.frames = self.gamer_girl
            self.position = position
            self.BG = Background(os.path.join(ROOT_DIR, 'wise_nebula.png'), [0, 0])
            self.screen.fill(WHITE)
            self.screen.blit(self.BG.image, self.BG.rect)
            self.render_frame(0)
            self.frame_i = 0
            self.start_time = time.time()

    def talk_animation(self, response, intent="explain"):
        if DEBUG:
            _, response_mp3, __, ___, ____, _____ = response[0]
            file = os.path.join(ROOT_DIR, 'intents', intent, response_mp3)
            play_mp3(file)
            return None
        pygame.mixer.fadeout(0.25)
        self.start_time = time.time()
        i = 0
        for response_text, response_mp3, actions, image, img_x, img_y in response:
            song_end = pygame.USEREVENT + 1
            running = True
            #file = os.path.join(ROOT_DIR, 'intents', intent, response_mp3)
            if image is not None:
                insert_image(screen=self.screen, image=image, img_pos=(img_x, img_y))
            try:
                file = os.path.join(ROOT_DIR, 'intents', intent, response_mp3)
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
            except:
                print("cannot load file")
            self.screen.fill(WHITE)
            self.screen.blit(self.BG.image, self.BG.rect)
            self.render_frame(i)
            self.frame_i = 0
            while running:
                events = pygame.event.get()
                #for event in pygame.event.get():
                self._animate()
                if 0 == len(events):
                    continue
                else:
                    for event in events:
                        self._animate()
                        if event.type == song_end:
                            running = False
                            break

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

    def __init__(self):
        # get the configuration if needed
        '''
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None
        '''
        self.config = None
        self.con = None
        self.cursor = None
        self.PAT = None
        self.PAT_position = (-200, 100)
        self.con = sql.connect(os.path.join(ROOT_DIR, 'PAT_on_pi.db'))
        self.cursor = self.con.cursor()
        self._running = True
        # start listening to MQTT
        self.start_blocking()
        if not DEBUG:
            pygame.init()
            self._display_surf = ScreenSingleTone()
            pygame.mixer.init()
        self.PAT = PAT_simple(self.PAT_position)


    def _get_slots(self, intent_message, slot_names=[]):
        slots = {}
        for slot in intent_message["slots"]:
            slots[slot['slotName']] = slot['value']['value']
        for slot_name in slot_names:
            if slot_name not in slots.keys():
                slots[slot_name] = "default"
        return slots

    def intent_explain(self, intent_message):
        slots = self._get_slots(intent_message, slot_names=["Components"])
        self.play_explain(slots["Components"])

    def play_explain(self, component):
        self.cursor.execute(f"""select response_text, response_mp3, actions, image, img_x, img_y
                                from explain_play
                                where component = '{component}'
                                order by play_order asc""")
        response = self.cursor.fetchall()

        self.PAT.talk_animation(response, intent="explain")

    def intent_purpose(self, intent_message):
        slots = self._get_slots(intent_message, slot_names=["Components", "People"])
        self.play_purpose(slots["Components"], slots["People"])

    def play_purpose(self, component, people):
        self.cursor.execute(f"""select response_text, response_mp3, actions, image, img_x, img_y
                                from purpose_play
                                where component = '{component}' and people = '{people}'
                                order by play_order asc""")
        response = self.cursor.fetchall()

        self.PAT.talk_animation(response, intent="purpose")

    def intent_availability(self, intent_message):
        if len(intent_message.slots.Location) > 0:
            location = intent_message.slots.Location.first().value
        else:
            location = "default"
        self.play_availability(location)

    def play_availability(self, location):
        self.cursor.execute(f"""select response_text, response_mp3, actions, image, img_x, img_y
                                from availability_play
                                where location = '{location}'
                                order by play_order asc""")
        response = self.cursor.fetchall()

        self.PAT.talk_animation(response, intent="availability")

    def intent_bye(self, intent_message):
        self.play_bye()

        # if need to speak the execution result by tts
        # Hermes.publish_start_session_notification(intent_message.site_id,
        #                                             "bye has been done")

    def play_bye(self):
        self.cursor.execute(f"""select response_text, response_mp3, actions, image, img_x, img_y
                                from bye
                                order by rand()
                                limit 1""")
        rows = self.cursor.fetchall()
        response = rows
        self.PAT.talk_animation(response, intent="bye")

    def intent_hello(self, intent_message):
        self.play_hello()

    def play_hello(self):
        self.cursor.execute(f"""select response_text, response_mp3, actions, image, img_x, img_y
                                from hello
                                order by rand()
                                limit 1""")
        response = self.cursor.fetchall()
        self.PAT.talk_animation(response, intent="hello")

    def intent_show_menu(self, Hermes, intent_message):
        pass
        '''
        Not sure what to do here
        '''


    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        print("coming_intent:", intent_message)
        coming_intent = intent_message.intent.intent_name

        print("will this show up?")
        if coming_intent == 'Explain':
            self.intent_explain(intent_message)
        elif coming_intent == 'Purpose':
            self.intent_purpose(intent_message)
        elif coming_intent == 'Availability':
            self.intent_availability(intent_message)
        elif coming_intent == 'hello':
            self.intent_hello(intent_message)
        elif coming_intent == 'bye':
            self.intent_bye(intent_message)
        elif coming_intent == 'Show_Menu':
            self.intent_show_menu(Hermes, intent_message)
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")
        print(f'[Received] intent: {intent_message.intent.intent_name}')
        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Template()