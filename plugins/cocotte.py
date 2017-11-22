"""
.. module: hubcommander.command_plugins.repeat
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Mike Grima <mgrima@netflix.com>
.. moduleauthor:: Duncan Godfrey @duncangodfrey
"""
import datetime

from hubcommander.bot_components.decorators import hubcommander_command
from hubcommander.bot_components.bot_classes import BotCommander
from hubcommander.bot_components.slack_comm import send_info, send_error, send_success

from louisebot.config import config
from louisebot.db import DBSession, User, Day, Presence

endpoint = config.get('default', 'endpoint')
bot_id = config.get(endpoint, 'bot_id')
start_string = '<@{0}>'.format(bot_id)


class CocottePlugin(BotCommander):
    def __init__(self):
        super().__init__()

        self.commands = {
            "!Balance": {
                "command": "!Balance",
                "func": self.balance,
                "help": "Affiche l'état actuel des comptes.",
                "user_data_required": True,
                "enabled": True
            },
            "!Manger": {
                "command": "!Manger",
                "func": self.manger,
                "help": "Pour dire 'Je mange ce midi !'",
                "user_data_required": True,
                "enabled": True
            },
            "!CancelManger": {
                "command": "!CancelManger",
                "func": self.cancelmanger,
                "help": "Pour dire 'Je mange PAS ce midi !'",
                "user_data_required": True,
                "enabled": True
            },
            "!QuiMange": {
                "command": "!QuiMange",
                "func": self.quimange,
                "help": "Liste les inscrits du midi.",
                "user_data_required": True,
                "enabled": True
            },
            "!Achat": {
                "command": "!Achat",
                "func": self.achat,
                "help": "Pour déclarer un achat.",
                "user_data_required": True,
                "enabled": True
            },
            "!MyBalance": {
                "command": "!MyBalance",
                "func": self.mybalance,
                "help": "Liste les derniers repas / achats et affiche sa balance.",
                "user_data_required": True,
                "enabled": True
            },
        }

    def setup(self, *args):
        # Add user-configurable arguments to the command_plugins dictionary:
        #for cmd, keys in USER_COMMAND_DICT.items():
        #    self.commands[cmd].update(keys)
        pass

    @staticmethod
    def get_db_user(user_data):
        session = DBSession()
        return session.query(User).filter(User.slackid == user_data['id']).first()

    @staticmethod
    def get_db_day():
        session = DBSession()
        today = datetime.date.today()
        return session.query(Day).filter(Day.date == today).first()

    @hubcommander_command(
        name="!Balance",
        usage="!Balance",
        description="Affiche les balances !",
        required=[],
    )
    def balance(self, data, user_data):
        session = DBSession()
        users = session.query(User).all()
        outputs = []
        outputs.append('Voici l\'état des compte chez Louise :')
        for user in users:
            outputs.append('{0} : balance à {1}'.format(user.name, 0.0))
        send_info(data['channel'], text='\n'.join(outputs))

    @hubcommander_command(
        name="!Manger",
        usage="!Manger",
        description="Pour indiquer qu'on mange le midi !",
        required=[],
	optional=[
            dict(name="guest", properties=dict(nargs="?", default=0, type=int,
                                                help="Nombre d'invité avec vous"))
        ]
    )
    def manger(self, data, user_data, guest):
        session = DBSession()

        day = self.get_db_day()
        if not day:
            day = Day(date=datetime.date.today())
            session.add(day)
            session.commit()

        outputs = []

        user = self.get_db_user(user_data)
        if not user:
            send_error(data['channel'], 'Erreur il faut ```python manage.db sync``` d\'abort !')

        presence = session.query(Presence).filter(
                Presence.user_id == user.id,
                Presence.day_id == day.id).first()
        if not presence:
            presence = Presence(user_id=user.id,
                                day_id=day.id,
                                meals=guest+1)
            session.add(presence)
            session.commit()
            outputs.append("J'ai pris en compte ta demande <@{0}>".format(user_data['id']))
            if guest > 0:
                outputs.append("Je te compterai {0} part ce jour".format(guest+1))
        else:
            if presence.meals != guest+1:
                presence.meals = guest+1
                session.add(presence)
                session.commit()
                if guest > 0:
                    outputs.append("J'ai modifié ta demande, et rajouté {0} invité(s) <@{1}>".format(guest, user_data['id']))
                else:
                    outputs.append("J'ai modifié ta demande, et enlevé les invités <@{1}>".format(guest, user_data['id']))
            else:
                outputs.append("Rien n'a changé, tu étais déjà inscrit <@{1}> :)".format(guest, user_data['id']))

        outputs.append("Si besoin tu peux !CancelManger ou !Manger avec des invités :)")
        send_info(data['channel'], text='\n'.join(outputs), markdown=True)

    @hubcommander_command(
        name="!CancelManger",
        usage="!CancelManger",
        description="Pour annuler une inscription !",
        required=[],
	optional=[],
    )
    def cancelmanger(self, data, user_data):
        session = DBSession()

        day = self.get_db_day()
        if not day:
            day = Day(date=datetime.date.today())
            session.add(day)
            session.commit()

        outputs = []

        user = self.get_db_user(user_data)
        if not user:
            send_error(data['channel'], 'Erreur zjaifnazgoizangoiazg')

        presence = session.query(Presence).filter(
                Presence.user_id == user.id,
                Presence.day_id == day.id).first()
        if not presence:
            outputs.append("Tu n'étais pas inscrit, pas de soucis <@{0}> !".format(user_data['id']))
        else:
            session.query(Presence).filter_by(id=presence.id).delete()
            session.commit()
            outputs.append("J'ai supprimé ta demande <@{0}>, dommage ça allait être trop bon !".format(user_data['id']))

            outputs.append("Si besoin tu !Manger à nouveau :)")
        send_info(data['channel'], text='\n'.join(outputs), markdown=True)

    @hubcommander_command(
        name="!QuiMange",
        usage="!QuiMange",
        description="Liste les inscrits du midi.",
        required=[],
	optional=[],
    )
    def quimange(self, data, user_data):
        return

    @hubcommander_command(
        name="!Achat",
        usage="!Achat",
        description="Pour déclarer un achat.",
        required=[],
	optional=[],
    )
    def achat(self, data, user_data):
        return

    @hubcommander_command(
        name="!MyBalance",
        usage="!MyBalance",
        description="Liste les derniers repas / achats et affiche sa balance.",
        required=[],
	optional=[],
    )
    def mybalance(self, data, user_data):
        return
