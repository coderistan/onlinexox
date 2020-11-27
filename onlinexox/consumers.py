from channels.generic.websocket import WebsocketConsumer
from onlinexox import minmax
import json
from django.utils.crypto import get_random_string

class ComputerConsumer(WebsocketConsumer):
    def connect(self):
        self.game = minmax.GameAlpha()
        self.accept()
        

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)

        x = int(data["x"])
        y = int(data["y"])
        if self.game.play(x,y,self.game.player):
            winner = self.game.is_finish()
            if winner:
                result = {"board":self.game.board,"finish":True,"winner":winner}
                self.send(text_data=json.dumps(result))
                self.game.clear()
                return

            self.game.play_computer()
            winner = self.game.is_finish()

            if winner:
                result = {"board":self.game.board,"finish":True,"winner":winner}
                self.send(text_data=json.dumps(result))
                self.game.clear()
                return
            
            result = {"board":self.game.board,"finish":False}
            self.send(text_data=json.dumps(result))
        else:
            print("Hatalı hamle")            

class FriendConsumer(WebsocketConsumer):
    info = {}
    START_GAME = 1
    BROKEN_GAME = 2
    BOARD_INFO = 3

    def connect(self):
        self.connection = False
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self,"code"):
            # Oyun aktif ise
            info = FriendConsumer.info.get(self.code,False)
            
            if info:
                if self.player == minmax.Game.player_1:
                    # Kurucu oyundan ayrılırsa oyuna dair tüm bilgiler kaldırılır ve
                    # davetli oyuncuya oyunun sona  erdiğine dair bildirim gönderilir

                    if info.get("player_2",False):
                        info.get("player_2").send(json.dumps({
                            "type":"game",
                            "message":"Kurucu oyunu sona erdirdi",
                            "code":FriendConsumer.BROKEN_GAME
                            }))
                        info.get("player_2").connection = False

                    del FriendConsumer.info[self.code]
                    
                else:
                    # Davetli oyundan ayrılırsa oyun bilgileri sıfırlanır
                    # ve aynı davet bağlantısından tekrar bağlanması beklenilir

                    del info["player_2"]
                    
                    info.get("game").clear()
                    info.get("player_1").connection = False
                    info.get("player_1").send(json.dumps({
                            "type":"game",
                            "message":"Davetli oyundan ayrıldı. Aynı linki kullanarak tekrar bağlanabilir",
                            "code":FriendConsumer.BROKEN_GAME
                            }))

    def play_game(self,data):
        if self.connection:
            game = FriendConsumer.info.get(self.code).get("game")
            x = data["coordinates"]["x"]
            y = data["coordinates"]["y"]
            game.play(x,y,self.player)

            winner = game.is_finish()
            if winner:
                # tüm oyunculara oyunun bittiğini bildir
                result = json.dumps({"type":"game","code":FriendConsumer.BOARD_INFO,"board":game.board,"is_finish":True,"winner":winner})
                game.clear()
                self.send(result)

            else:
                result = json.dumps({"type":"game","code":FriendConsumer.BOARD_INFO,"board":game.board,"is_finish":False})                
            
            self.get_opponent().send(result)

    def get_opponent(self):
        # Oyuncu için karşı oyuncu nesnesini elde etme
        if self.connection:
            if self.player == minmax.Game.player_1:
                return FriendConsumer.info.get(self.code).get("player_2")
            else:
                return FriendConsumer.info.get(self.code).get("player_1")

        else:
            return None

    def get_message_type(self,data):

        if data["type"] == "message":
            return self.send_message

        elif data["type"] == "game":
            return self.play_game

        elif data["type"] == "connect":
            return self.create_game

    def send_message(self,data):
        if self.connection:
            # Bağlantı kurulmadı ise mesajlar es geçilir
            temp = self.get_opponent()
            temp.send(json.dumps({"type":"message","message":data["message"]}))

    def start_game(self,code):
        info = FriendConsumer.info.get(self.code)
        info.get("player_1").connection = True
        info.get("player_1").send(json.dumps({"type":"game","message":"Oyun başladı. Hadi sıra sende!","code":FriendConsumer.START_GAME,"turn":True}))
        info.get("player_2").connection = True
        info.get("player_2").send(json.dumps({"type":"game","message":"Bağlantı kuruldu. Arkadaşın oynuyor","code":FriendConsumer.START_GAME,"turn":False}))

    def create_game(self,data):
        if FriendConsumer.info.get(data["code"],False):
            if not data["invite"]:
                # Oyun var, eğer gelen davetli değilse red mesajı yollanacak
                self.send(json.dumps({"type":"connect","status":False}))
                return
            
            elif FriendConsumer.info[data["code"]].get("player_2",False):
                # Ortada bir oyun var ve davet var. Ancak fazladan bir davetli geldi ise
                self.send(json.dumps({"type":"connect","status":False}))
                return

            else:
                # Ortada bir oyun var, davetli geldi ve tüm oyunun başlaması için herşey tamam
                # Bu durumda tüm oyunculara oyunun başladığına dair bildiri gidecek
                self.player = minmax.Game.player_2 # katılan kişi 2. oyuncu olur, ilk başlayan kurucu olur
                self.code = data["code"]

                FriendConsumer.info.get(self.code)["player_2"] = self
                self.start_game(self.code)

        else:
            # Oyun yok. Davetli geldi ise red mesajı yolla
            if data["invite"]:
                self.send(json.dumps({"type":"connect","status":False}))
                return
            
            else:
                # Oyun oluşturma
                self.player = minmax.Game.player_1
                self.code = data["code"]
            
                FriendConsumer.info[self.code] = {
                    "player_1":self,
                    "game":minmax.Game(),
                }
            
    def receive(self, text_data):
        data = json.loads(text_data)

        message_type = self.get_message_type(data)
        message_type(data)