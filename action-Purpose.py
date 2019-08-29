#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import os
import subprocess
from PIL import Image

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"
ROOT_DIR = "/home/pi/PAT"

def play_mp3(path):
    subprocess.Popen(['mpg123', '-q', path]).wait()

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    mp3_file = row["response_mp3"]
    image = None
    file = os.path.join(ROOT_DIR, 'intents', "purpose", mp3_file)
    if image is not None and type(image) == str:
        try:
            img = Image.open(image)
            img.show()
        except:
            print("image file not found:", image)
    play_mp3(file)
    pass
    #{{#each action_code as |a|}}{{a}}
    #{{/each}}


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("{{intent_id}}", subscribe_intent_callback) \
         .start()