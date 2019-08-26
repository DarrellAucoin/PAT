# !/usr/bin/env python3
# encoding: utf-8

# import paho.mqtt.client as mqtt



# def on_connect(client, userdata, flags, rc):
#     print('Connected')
#     mqtt.subscribe('hermes/intent/#')
#
# mqtt = mqtt.Client()
# mqtt.on_connect = on_connect
# mqtt.connect('raspberrypi.local', 1883)
# mqtt.loop_forever()

from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import pygame
from pygame.locals import *
from pygame.math import Vector2
import sqlite3 as sql
import os
import time
import sys
#import pygameMenu
import subprocess
from sys import platform

if platform == "darwin":
    # OS X
    ROOT_DIR = "Users/daucoin/github/PAT_on_Pi"
    bashStartSnips = ["brew services start mosquitto",
                      "brew services start snips-audio-server",
                      "brew services start snips-hotword",
                      "brew services start snips-tts",
                      "brew services start snips-nlu",
                      "brew services start snips-asr",
                      "brew services start snips-dialogue"]
    bashStopSnips = ["brew services stop mosquitto",
                     "brew services stop snips-audio-server",
                     "brew services stop snips-hotword",
                     "brew services stop snips-tts",
                     "brew services stop snips-nlu",
                     "brew services start snips-asr",
                     "brew services stop snips-dialogue"]

    def start_snips():
        for command in bashStartSnips:
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

    def stop_snips():
        for command in bashStopSnips:
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

else:
    # Raspberry pi
    ROOT_DIR = "/home/pi/PAT"

    def start_snips():
        pass

    def stop_snips():
        pass


start_snips()

CONFIG_INI = "config.ini"

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = f"{MQTT_IP_ADDR}:{str(MQTT_PORT)}"

WHITE = (255, 255, 255)
BLACK = (0, 0 ,0)
RED = (255, 0 ,0)

screen_size = (1024, 600)

def play_mp3(path):
    #subprocess.Popen(['mplayer', '-nolirc', '-really-quiet', path]).wait()
    subprocess.Popen(['mpg123', '-q', path]).wait()
    #subprocess.Popen(['mpg321', '-q', path]).wait()


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class ChatBubble(pygame.sprite.Sprite):
    def __init__(self, position=[450, 100], width=10, height=100):
        pygame.sprite.Sprite.__init__(self)
        self.screen = ScreenSingleTone()
        self.line_width = 5
        self.bubble_black = pygame.draw.rect(self.screen, BLACK, position + [width] + [height])
        self.bubble = pygame.draw.rect(self.screen, WHITE, position + [width+self.line_width] + [height+self.line_width])
        # self.bubble_triangle = pygame.draw.polygon()
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        # self.bubble = pygame.display.set_mode((X, Y))

    def change_text(self, text):
        pass

    def render(self):
        pass


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
        self.screen = ScreenSingleTone()
        self.gamer_girl = [pygame.image.load(os.path.join(ROOT_DIR, f'PAT/png/frame_{i}_delay-0.2s.png')).convert_alpha() for i in range(14)]
        self.frames = self.gamer_girl
        self.position = position
        self.BG = Background(os.path.join(ROOT_DIR, 'wise_nebula.png'), [0, 0])
        self.screen.fill(WHITE)
        self.screen.blit(self.BG.image, self.BG.rect)
        self.render_frame(0)

    def talk_animation(self, response, intent="explain"):
        pass
        '''
        pygame.mixer.fadeout(0.25)
        song_end = pygame.USEREVENT + 1
        start_time = time.time()
        i = 0
        for response_text, response_mp3, actions, image, img_x, img_y in response:
            running = True
            file = os.path.join(ROOT_DIR, 'intents', intent, response_mp3)
            #play_mp3(file)
            if image is not None:
                insert_image(screen=self.screen, image=image, img_pos=(img_x, img_y))
            try:
                file = os.path.join(ROOT_DIR, 'intents', intent, response_mp3)
                play_mp3(file)
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
            except:
                print("cannot load file")
            self.screen.fill(WHITE)
            self.screen.blit(self.BG.image, self.BG.rect)
            self.render_frame(i)
            while running:
                if time.time() - start_time >= 0.2:
                    start_time = time.time()
                    i = (i + 1) % len(self.frames)
                    self.render_frame(i)
                for event in pygame.event.get():
                    if time.time() - start_time >= 0.2:
                        start_time = time.time()
                        i = (i + 1) % len(self.frames)
                        self.render_frame(i)
                    if event.type == song_end:
                        running = False
                        break
           
        self.screen.fill([255, 255, 255])
        self.screen.blit(self.BG.image, self.BG.rect)
        self.render_frame(0)
        '''

    def render_frame(self, i):
        self.screen.blit(self.frames[i], self.position)
        pygame.display.update()




class Menu(object):
    """


    """

    def __init__(self):
        pass

    def show_menu(self):
        pass



class FAQ_PAT(object):
    """Class used to wrap action code with mqtt connection

        Please change the name refering to your application
    """

    def __init__(self):
        # get the configuration if needed
        self._running = True
        self._display_surf = None
        '''
        try:
            from snipsTools import SnipsConfigParser
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except:
            self.config = None
        '''
        self.config = None
        self.con = None
        self.cursor = None
        self.PAT = None
        self.PAT_position = (-200, 100)
        file = 'PAT/intents/explain/AppHolo_00.mp3'
        play_mp3(file)

    def on_init(self):
        pygame.init()
        self._display_surf = ScreenSingleTone()
        pygame.mixer.init()
        self.PAT = PAT_simple(self.PAT_position)
        self.con = sql.connect(os.path.join(ROOT_DIR, 'PAT_on_pi.db'))
        self.cursor = self.con.cursor()
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
            sys.exit()

    def on_loop(self):
        pass

    def on_render(self):
        pass

    def _on_cleanup(self):
        self.con.close()
        pygame.mixer.quit()
        pygame.quit()
        stop_snips()

        sys.exit()

    def on_execute(self):
        self.on_init()
        while self._running:
            for event in pygame.event.get():
                # start listening to MQTT
                self.start_blocking()
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self._on_cleanup()

    def _get_slots(self, intent_message, slot_names=[]):
        slots = {}
        for slot in intent_message["slots"]:
            slots[slot['slotName']] = slot['value']['value']
        for slot_name in slot_names:
            if slot_name not in slots.keys():
                slots[slot_name] = "default"
        return slots

    # --> Sub callback function, one per intent

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

        '''
        Not sure what to do here
        '''

    def master_intent_callback(self, Hermes, intent_message):
        '''
        --> Master callback function, triggered everytime an intent is recognized

        :param Hermes:
        :param intent_message:
        :return:
        '''
        coming_intent = intent_message['intent']['intentName']
        # terminate the session first if not continue
        Hermes.publish_end_session(intent_message.session_id, "")

        print("will this show up?")
        if coming_intent == 'explain':
            self.intent_explain(intent_message)
        elif coming_intent == 'purpose':
            self.intent_purpose(intent_message)
        elif coming_intent == 'availability':
            self.intent_availability(intent_message)
        elif coming_intent == 'hello':
            self.intent_hello(intent_message)
        elif coming_intent == 'bye':
            self.intent_bye(intent_message)
        elif coming_intent == 'show_menu':
            self.intent_show_menu(Hermes, intent_message)

        print(f'[Received] intent: {intent_message.intent.intent_name}')

    def start_blocking(self):
        '''
        --> Register callback function and start MQTT
        :return:
        '''
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()


if __name__ == "__main__":
    PAT = FAQ_PAT()
    PAT.on_execute()