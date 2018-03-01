#!/usr/bin/env python

import os
import time
import logging
import click


from slackclient import SlackClient
from sqlalchemy.orm import sessionmaker
from alkivi.logger import Logger

from louisebot.config import config
from louisebot.db import Base, engine, DBSession, User

logger = Logger(min_log_level_to_mail=None,
                min_log_level_to_save=logging.INFO,
                min_log_level_to_print=logging.INFO)


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    logger.info('Starting manager.py')

    if debug:
        logger.set_min_level_to_print(logging.DEBUG)
        logger.set_min_level_to_save(logging.DEBUG)
        logger.debug('Debug mode activated')

@cli.command()
def createdb():
    """Create the SQL database."""
    logger.info('Creating database')
    Base.metadata.create_all(engine)

@cli.command()
def sync():
    """Sync user with slack."""
    endpoint = config.get('default', 'endpoint')
    bot_token = config.get(endpoint, 'bot_token')
    slack_client = SlackClient(bot_token)
    session = DBSession()

    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if user['name'] == 'slackbot':
                continue
            if not user['is_bot']:
                _sync_user(user, session)
    else:
        logger.warning('Error', api_call)
    session.commit()

def _sync_user(slack_data, session):
    """Sync a slack user in SQL."""
    user = session.query(User).filter(User.slackid == slack_data['id']).first()
    if not user:
        user = User(name=slack_data['name'],
                    slackid=slack_data['id'],
                    admin=slack_data['is_admin'])
        logger.debug('Creating user {0}'.format(slack_data['name']))
        session.add(user)
    else:
        logger.info('User {0} already exist'.format(user.name))
        if slack_data['name'] != user.name:
            user.name = slack_data['name']
            logger.info('Updating name {0}'.format(user.name))
        if slack_data['is_admin'] != user.admin:
            user.admin = slack_data['is_admin']
            logger.info('Updating admin status for {0}'.format(user.name))
        session.add(user)

@cli.command()
@click.option('--user', prompt='User to delete',
                      help='The user to delete.')
def delete_user(user):
    """Sync user with slack."""
    session = DBSession()
    db_user = session.query(User).filter(User.name == user).first()
    if not db_user:
        logger.warning('User {0} does not exist'.format(user))
        exit(0)

    balance = db_user.balance
    logger.info('test {0} {1}'.format(user, balance))

    if balance == 0.0:
        session.delete(db_user)
        session.commit()
        logger.info('User {0} deleted !'.format(user))
    else:
        logger.warning('User {0} has a balance of {1}'.format(user, balance))
        logger.warning('Must be reseted to 0 :)')
        exit(1)

if __name__ == '__main__':
    cli()

