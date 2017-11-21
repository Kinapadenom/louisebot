#!/usr/bin/env python

import os
import time
import logging
import click

from louisebot.config import config
from slackbot.bot import Bot

from alkivi.logger import Logger

logger = Logger(min_log_level_to_mail=None,
                min_log_level_to_save=logging.DEBUG,
                min_log_level_to_print=logging.DEBUG)



@click.command()
def run():

    # Load config
    endpoint = config.get('default', 'endpoint')
    bot_id = config.get(endpoint, 'bot_id')
    bot_token = config.get(endpoint, 'bot_token')

    API_TOKEN = bot_token

    bot = Bot()
    bot.run()


if __name__ == "__main__":
    run()
