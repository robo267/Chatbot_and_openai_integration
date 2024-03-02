function sendmsg(){
    var box = document.getElementById('prompt')
    var prompt = box.value
    box.value = ""
    var userMessageHTML = "<br><div class='user_message'><span>" + prompt + "</span></div>";
    var userMessage = document.createElement('div');
    userMessage.innerHTML = userMessageHTML;
    bot_interface.appendChild(userMessage);
    //bot_interface.innerHTML += "<span style='color: red;'>" + "User: " + "</span>"+prompt+"<br>";
    bot_interface.scrollTop = bot_interface.scrollHeight;
    var data = {
        "prompt":prompt
    };

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/msg', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);
            var reply = response.reply;
            var bot_interface = document.getElementById('bot_interface')
            console.log(typeof reply, reply,reply==="404");
            if(reply=="Something is wrong.....!")
                
                bot_interface.value = reply
            else{
                /*var textContent = "";
                reply.forEach(function(dict) {
                for (var key in dict) {
                    if (dict.hasOwnProperty(key)) {
                        textContent += key + "<br>" + dict[key] + "<br>";
                    }
                    }
                });
                console.log(textContent)*/
                var botMessageHTML = "<br><div class='bot_message'><span>" + reply + "</span></div><br>";
                var botMessage = document.createElement('div');
                botMessage.innerHTML = botMessageHTML;
                bot_interface.appendChild(botMessage);
                //bot_interface.innerHTML += "<span style='color: blue;'>" + "Bot: " + "</span>"+reply+"<br>"
                bot_interface.scrollTop = bot_interface.scrollHeight;
            }
                       
        }
    };
    xhr.send(JSON.stringify(data));
}