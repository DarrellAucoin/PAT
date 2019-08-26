#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import pygame

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    #{{#each action_code as |a|}}{{a}}
    #{{/each}}


if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("{{intent_id}}", subscribe_intent_callback) \
         .start()

        # initialize the pygame module
        pygame.init()
        # load and set the logo
        logo = pygame.image.load("logo32x32.png")
        pygame.display.set_icon(logo)
        pygame.display.set_caption("minimal program")
	     
        # create a surface on screen that has the size of 240 x 180
        screen = pygame.display.set_mode((240,180))
        # define a variable to control the main loop
        running = True
        # main loop
        while running:
            # event handling, gets all event from the event queue
            for event in pygame.event.get():
            # only do something if the event is of type QUIT
                if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                    running = False
            