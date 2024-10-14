import os.path
import configparser

class Config():
    def __init__(self):
        self.configFile = 'cfg.ini'
        self.config = configparser.ConfigParser()

        if os.path.exists(self.configFile):
            self.load()
        else:
            self.config['TWITCH'] = {
                'username': '',
                'command-prefix': '!',
                'token': '',
                'client-secret': '',
                'enable-cooldown-msg': False
                #to be continiued
            }
            self.save()

        self.username = self.config.get('TWITCH', 'username').split(',')
        self.username = [name.strip() for name in self.username]
        self.commandPrefix = self.config.get('TWITCH', 'command-prefix')
        self.token = self.config.get('TWITCH', 'token')
        self.clientSecret = self.config.get('TWITCH', 'client-secret')
        self.enableCooldownMsg = self.config.getboolean('TWITCH', 'enable-cooldown-msg')

    def save(self):
        with open(self.configFile, 'w') as configfile:
            self.config.write(configfile)

    def load(self):
        self.config.read(self.configFile)        