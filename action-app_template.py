# !/usr/bin/env python3
# encoding: utf-8

#from snipsTools import SnipsConfigParser

from hermes_python.hermes import Hermes
import paho.mqtt.client as mqtt
from hermes_python.ontology import *
import os
import subprocess
import pandas as pd
import sys
from snipsTools import SnipsConfigParser
import json

CONFIG_INI = "config.ini"
ROOT_DIR = "/home/pi/PAT"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = f"{MQTT_IP_ADDR}:{MQTT_PORT}"
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
screen_size = (1024, 600)
PAT_position = (-250, 100)
DEBUG = False
BG_IMAGE = "CSA_logo.jpg"
CONFIG_INI = "config.ini"


def play_mp3(path):
    subprocess.Popen(['mpg123', '-q', path]).wait()


def on_connect(client, userdata, flags, rc):
    # print('Connected')
    mqtt.subscribe('hermes/intent/#')


def insert_image(image=None, delay=7):
    args = ['pqiv', '--fullscreen', "--hide-info-box", "--scale-images-up", "--background-pattern=white"]
    if type(image) != str:
        images = [os.path.join(ROOT_DIR, "images", BG_IMAGE)]
    else:
        images = [os.path.join(ROOT_DIR, "images", img.strip()) for img in image.split(";")]
        images = [img for img in images if os.path.isfile(img)]
    if len(images) > 1:
        args = args + ["--slideshow", "-d", str(delay)]
    elif len(images) == 0:
        images = [os.path.join(ROOT_DIR, "images", BG_IMAGE)]
    args = args + images
    # print("image files:", images)
    subprocess.Popen(['xdotool', 'key', "Escape"])
    subprocess.Popen(args=args)


class FAQ_PAT(object):
    """Class used to wrap action code with mqtt connection

        Please change the name refering to your application
    """

    def __init__(self, mp3_only=False, wake_word=True):
        # get the configuration if needed
        '''
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None
        '''
        # print("In __init__ of Template")
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except Exception:
            self.config = None
        self.image_up = False
        self.introduction = True
        self.wake_word = wake_word
        self.tables = {}
        self.mp3_only = mp3_only
        self.intents = {"Explain": ["Components"],
                        "Purpose": ["Components", "People"],
                        "Availability": ["Location"],
                        "hello": [],
                        "bye": [],
                        "none": []}
        self._get_tables()
        # start listening to MQTT

    def show_image(self, image, delay=7):
        if image is None or type(image) not in [str, list] or not self.mp3_only:
            return None
        try:
            insert_image(image, delay=delay)
        except Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)  # __str__ allows args to be printed directly,
            print("image file not found:", image)

    def _play_mp3(self, file):
        if self.mp3_only:
            subprocess.Popen(['mpg123', '-q', file])#.wait()

    def talk_animation(self, response, intent="explain"):
        if not self.mp3_only:
            return None
        response = response[["response_text", "response_mp3", "image", "delay"]]
        for index, row in response.iterrows():
            mp3_file = os.path.join(ROOT_DIR, 'intents', intent.lower(), row["response_mp3"].strip())
            self.show_image(row["image"], delay=row["delay"])
            self._play_mp3(file=mp3_file)
            break

    def _get_response(self, intent_message):
        intent = intent_message.intent.intent_name
        if ':' in intent:
            intent = intent.split(":")[1]
        response = self.tables[intent]
        slots_dict = {}
        slot_names = self.intents[intent]
        for slot_name, v in intent_message.slots.items():
            # Attributes of slot_value: from_c_repr, value, value_type
            if slot_name in response.columns:
                found_slot = False
                for val in v:
                    if val.slot_value.value.value in response[slot_name].values:
                        response = response[response[slot_name] == val.slot_value.value.value]
                        print(f"slot {slot_name}: {val.slot_value.value.value}")
                        slots_dict[slot_name] = val.slot_value.value.value
                        # also has attributes confidence_score, entity, from_c_repr, range_end, range_start, raw_value,
                        # slot_name, slot_value
                        found_slot = True
                        break
                if not found_slot:
                    response = response[response[slot_name] == "default"]
                # try:
                #     slot_names.remove(slot_name)
                # except:
                #     print(f"{slot_name} not in provided slot_names: {slot_names}")
        if len(response) == 1:
            return response
        else:
            for slot_name in slot_names:
                if slot_name not in slots_dict.keys():
                    response = response[response[slot_name] == "default"]
                if len(response) == 1:
                    return response
        return response

    def _get_tables(self):
        for intent in self.intents.keys():
            self.tables[intent] = pd.read_csv(os.path.join(ROOT_DIR, "intents", f"{intent.lower()}.csv"))
            slot_names = self.intents[intent]
            for slot in slot_names:
                assert slot in self.tables[intent].columns, f"slot {slot} not in {intent} table"

    def play_intent(self, hermes, intent_message):
        # hermes.publish_end_session(intent_message.session_id, "")
        response = self._get_response(intent_message=intent_message)
        self.talk_animation(response, intent=intent_message.intent.intent_name.split(":")[1])

    '''
    def intent_explain(self, hermes, intent_message):
        # hermes.publish_end_session(intent_message.session_id, "")
        response = self._get_response(intent_message=intent_message, slot_names=["Components"])
        self.talk_animation(response, intent="explain")

    def intent_purpose(self, hermes, intent_message):
        response = self._get_response(intent_message=intent_message, slot_names=["Components", "People"])
        self.talk_animation(response, intent="purpose")
        # hermes.publish_start_session_notification(intent_message.site_id, "", "")

    def intent_availability(self, hermes, intent_message):
        # hermes.publish_end_session(intent_message.session_id, "")
        response = self._get_response(intent_message=intent_message, slot_names=["Location"])
        self.talk_animation(response, intent="availability")
    '''
    def intent_bye(self, hermes, intent_message):
        # hermes.publish_end_session(intent_message.session_id, "")
        response = self.tables["bye"]
        self.talk_animation(response, intent="bye")
        if self.mp3_only:
            for i in range(3):
                subprocess.Popen(['xdotool', 'key', "Escape"])
            sys.exit()

    def intent_hello(self, hermes, intent_message):
        # hermes.publish_end_session(intent_message.session_id, "")
        if self.introduction:
            intro = "yes"
            self.introduction = False
        else:
            intro = "no"
        response = self.tables["hello"][self.tables["hello"]["introduction"] == intro]
        self.talk_animation(response, intent="hello")
        # hermes.publish_start_session_notification(intent_message.site_id, "", "")

    def intent_none(self, hermes, intent_message):
        # hermes.publish_end_session(intent_message.session_id, "")
        response = self.tables["none"]
        self.talk_animation(response, intent="none")
        # hermes.publish_start_session_notification(intent_message.site_id, "", "")

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self, hermes, intent_message):
        if self.wake_word:
            hermes.publish_end_session(intent_message.session_id, "")
        else:
            hermes.publish_continue_session(intent_message.session_id, "",
                                            [f"{intent_message.intent.intent_name}"])
        # data = json.loads(intent_message.custom_data)
        # print("data json:", data)
        # hermes.publish_continue_session(intent_message.session_id, "")
        # print("hermes methods:", dir(hermes))
        if self.mp3_only:
            subprocess.Popen(["pkill", "mpg123"])
        try:
            coming_intent = intent_message.intent.intent_name
            if ':' in coming_intent:
                coming_intent = coming_intent.split(":")[1]
            print("coming_intent:", coming_intent)

            if coming_intent == 'hello':
                self.intent_hello(hermes, intent_message)
            elif coming_intent == 'bye':
                self.intent_bye(hermes, intent_message)
            elif coming_intent in self.intents.keys():
                self.play_intent(hermes, intent_message)
            # elif coming_intent == 'Explain':
            #     self.intent_explain(hermes, intent_message)
            # elif coming_intent == 'Purpose':
            #     self.intent_purpose(hermes, intent_message)
            # elif coming_intent == 'Availability':
            #     self.intent_availability(hermes, intent_message)
            else:
                self.intent_none(hermes, intent_message)
        except: # Exception as inst:
            # print(type(inst))  # the exception instance
            # print(inst.args)  # arguments stored in .args
            # print(inst)  # __str__ allows args to be printed directly,
            print("something got caught somewhere")
            sys.exit()
        finally:
            print(f'[Received] intent: {intent_message.intent.intent_name}')

        # terminate the session first if not continue
        # hermes.publish_start_session_notification(intent_message.site_id, "", "")
        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()


if __name__ == "__main__":
    mp3_only = False
    wake_word = True
    if "mp3_only" in sys.argv:
        mp3_only = True
    if "DEBUG" in sys.argv:
        DEBUG = True
    insert_image()
    insert_image()
    if "hdmi-sound" in sys.argv:
        subprocess.Popen(['amixer', 'cset', "numid=3", "2"])
    else:
        subprocess.Popen(['amixer', 'cset', "numid=3", "1"])
    PAT_avatar = FAQ_PAT(mp3_only=mp3_only, wake_word=wake_word)
    PAT_avatar.start_blocking()
