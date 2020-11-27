// https://techoverflow.net/2018/03/30/copying-strings-to-the-clipboard-using-pure-javascript/
function copyStringToClipboard (str) {
    // Create new element
    var el = document.createElement('textarea');
    // Set value (string to be copied)
    el.value = str;
    // Set non-editable to avoid focus and move outside of view
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    // Select text inside element
    el.select();
    // Copy text to clipboard
    document.execCommand('copy');
    // Remove temporary element
    document.body.removeChild(el);
}

function Game(character,token){
    this.score = 0;
    this.opponent_score = 0;
    this.turn = false;
    this.is_start = false;
    this.character = character;
    this.token = token;
    var self = this;

    this.coordinates = {
        "cell_1":{"x":0,"y":0},
        "cell_2":{"x":0,"y":1},
        "cell_3":{"x":0,"y":2},
        "cell_4":{"x":1,"y":0},
        "cell_5":{"x":1,"y":1},
        "cell_6":{"x":1,"y":2},
        "cell_7":{"x":2,"y":0},
        "cell_8":{"x":2,"y":1},
        "cell_9":{"x":2,"y":2}
    };

    this.clear_board = function(){
        $(".cell").text("-");
    }

    this.fill_board = function(board){
        for(let i in self.coordinates){
            x = self.coordinates[i].x;
            y = self.coordinates[i].y;
            document.getElementById(i).innerText = board[x][y];
        }
    }

    this.start = function(turn){
        self.turn = turn;
        self.is_start = true;
        
        if(self.turn){
            bildirim("Sıra sende!");
        }else{
            bildirim("Arkadaşın oynuyor...");
        }
    }

    this.stop = function(){
        self.is_start = false;
        self.score = 0;
        self.opponent_score = 0;
        self.clear_board();
    }

    this.end_game = function(){
        self.is_start = false;
        self.clear_board();
    }

    this.play = function(socket,e){   
        if(self.is_start){
            e.target.innerText = self.character;
            socket.send(JSON.stringify({"type":"game","coordinates":self.coordinates[e.target.getAttribute("id")]}))
            self.turn = false;
            bildirim("Arkadaşın oynuyor...");
        }
    }
    
    this.reload = function(){
        // bir oyun bittikten sonra tüm bilgiler sıfırlanır ve
        // sıraya göre yeniden oynanır
        self.clear_board();
        FIRST_TURN = !FIRST_TURN
        self.start(FIRST_TURN);
    }

    this.reload_score = function(winner){
        if(winner == self.character){
            self.score += 1;
        }else if(winner == "-"){
            bildirim("Kazanan yok");
        }else{
            self.opponent_score += 1;
        }
        $("#score").text("Sen: "+self.score+" - "+"Arkadaşın: "+self.opponent_score);
    }
}

function bildirim(mesaj){
    $("#bilgi").text(mesaj);
}

function send_message(message){
    if(message == null){
        message = document.getElementById("mesaj_girdisi").value;
    }

    if(message.length == 0){
        return;
    }
    
    $("#mesaj_kutusu").text($("#mesaj_kutusu").text()+"\n+ "+message);
    document.getElementById("mesaj_kutusu").scrollTop = document.getElementById("mesaj_kutusu").scrollHeight;
    baglanti.send(JSON.stringify({
        "type":"message",
        "message":message
    }));

    document.getElementById("mesaj_girdisi").value = "";
}

const START_GAME = 1;
const BROKEN_GAME = 2;
const BOARD_INFO = 3;
var FIRST_TURN = null; // değişimli olarak oyuna ilk başlayacak kişiyi belirleme
var baglanti = new WebSocket("ws://"+window.location.host+"/xoxfriend/");

window.onload = function(){
    var invite = document.getElementById("kopyala");

    if(invite){
        invite.onclick = function(e){           
            copyStringToClipboard($(this).text());
            $("#notify").show().delay(1000).slideUp(200, function() {
                $(this).hide();
            });
        }
    }
    
    var is_invite = document.getElementById("invite").getAttribute("name")=="True"?true:false; // davet edilmiş mi
    var token = document.getElementById("davet_kodu").getAttribute("name");
    var game = new Game(is_invite?"o":"x",token);

    baglanti.onopen = function(){
        baglanti.send(JSON.stringify(
            {
                "type":"connect",
                "code":token,
                "invite":is_invite,
            }
        ));        
    }
    baglanti.onclose = function(){
        $("#bilgi").text("Bağlantı koptu");
        game.stop();
    }

    baglanti.onmessage = function(e){
        mesaj = JSON.parse(e.data);

        switch(mesaj.type){
            case "connect":
                if(mesaj.status == false){
                    // bağlantı kurulamadı
                    bildirim("Malesef bağlantı kurulamadı");
                }
                break;

            case "message":
                // karşı taraftan bir mesaj geldi
                $("#mesaj_kutusu").text($("#mesaj_kutusu").text()+"\n- "+mesaj.message);
                document.getElementById("mesaj_kutusu").scrollTop = document.getElementById("mesaj_kutusu").scrollHeight;
                break;

            case "game":
                // oyun bilgisi iletildi
                $("#bilgi").text(mesaj.message);
                switch(mesaj.code){
                    case START_GAME:
                        game.start(mesaj.turn);
                        FIRST_TURN = mesaj.turn;
                        break;

                    case BROKEN_GAME:
                        game.stop();
                        break;

                    case BOARD_INFO:
                        if(mesaj.is_finish){
                            bildirim("Oyun bitti. Kazanan: "+mesaj.winner);
                            game.fill_board(mesaj.board);
                            game.reload_score(mesaj.winner);
                            game.end_game();
                            console.log(game.turn);
                            setTimeout(game.reload,1000);

                        }else{
                            game.fill_board(mesaj.board);
                            game.turn = true;
                            bildirim("Sıra sende!");
                        }
                        
                        break;
                    default:
                        // pass
                }
            default:
                break;
        }
    }

    document.getElementById("mesaj_girdisi").addEventListener("keyup",function(event){
        if(event.keyCode == 13){
            send_message(this.value);
        }
    });

    document.getElementById("friend_tablo").onclick = function(e){
        if(game.start && game.turn){
            if(e.target.innerText == "-"){
                game.play(baglanti,e);
            }
        }
    }; 
}