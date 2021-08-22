# install_twisted_rector must be called before importing the reactor
from __future__ import unicode_literals
from setback.results.get_games_result import GetGamesResult

from kivy.support import install_twisted_reactor
install_twisted_reactor()

# A Simple Client that send messages to the Echo Server
from twisted.internet import protocol
import json
from time import sleep

class SetbackClient(protocol.Protocol):
    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):
        message = data.decode('utf-8')
        message = json.loads(data)

        # Get the handler and run it 
        handle_method = self.factory.app.stateManager.response_handlers.pop(message["request_id"])
        handle_method(message["response"])
