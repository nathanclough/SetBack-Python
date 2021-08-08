from attr import Factory
from twisted.internet.protocol import ServerFactory
from twisted.test import proto_helpers
from server.server import SetbackServerApp, SetbackServerFactory
from setback import CreateGameResult, GetGamesResult
import json
import pytest


class FakeServer():
    def  __init__(self) -> None: 
        self.app = SetbackServerApp()
        self.factory = SetbackServerFactory(self.app)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)
    
    # Takes in json and sends to server 
    def send_request(self,requestJson):
        self.proto.dataReceived(requestJson.encode("utf-8"))
    
    # Returns Json Response
    def get_result(self):
        return self.tr.value().decode('utf-8')

@pytest.fixture
def server():
    return FakeServer()

class TestServer:
    def test_create_game(self,server:FakeServer):
        # Arrange 
        # Create the request as dict 
        request = {
            "method": "create_game",
            "args": {
                "name" : "Game1",
                "player": {
                    "name" : "Nathan",
                    "id" : 123,
                    "team": 1
                }
            }
        }
        # Convert to json 
        request = json.dumps(request)
        
        # Act 
        # Send the request 
        server.send_request(request)
        
        # Assert 
        # get the result
        result = server.get_result()
        
        # Convert it to result object from json 
        create_game_result = CreateGameResult.from_json(json.loads(result))
        
        # Verify that the result is correct
        assert create_game_result.id != None and create_game_result.name == "Game1"

    def test_get_games(self,server:FakeServer):   
        request = {
            "method": "get_games"
        }
        request = json.dumps(request)

        server.send_request(request)
        result = server.get_result()
        get_games_result = GetGamesResult.from_json(json.loads(result))
        assert len(get_games_result.games) == 1 

    def test_leave_game(self,server:FakeServer):
        game_id = server.app.games[0].id
        
        request = {"method": "leave_game",
            "args" : { "game_id": game_id, "player_id" : 123}}

        server.send_request(json.dumps(request))

        result = server.get_result()
        
        assert len(server.app.games[0].team_one) == 0 
    
    def test_unknown_method(self,server:FakeServer):
        request = {
            "method": "foo",
            }

        # 
        # Convert to json 
        request = json.dumps(request)
        
        # Act 
        # Send the request 
        server.send_request(request)
        
        # Assert 
        # get the result
        result = server.get_result()

        assert result == "'SetbackServerApp' object has no attribute 'foo'"