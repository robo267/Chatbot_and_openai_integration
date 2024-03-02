// static/script.js
function showPopup() {
    var intent = document.getElementById('intent').value;
    var question = document.getElementById('question').value;
    var answer = document.getElementById('answer').value;
    
    var data = {
        "intent": intent,
        "question": question,
        "answer": answer
    };
    // AJAX request to the Flask server
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/check', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);
            var predictions = response.predictions;
            console.log(typeof predictions, predictions,predictions==="404");

            if(predictions==="404"){
                var res = document.getElementById('mess');
                res.innerText = "Intent Already Exists...!";
            }
            else{
                var predictionTextarea = document.getElementById('predictionTextarea');
                predictionTextarea.value = predictions.join('\n');
                
                var popup = document.getElementById('popup_bg');
                popup.style.display = 'block';
            }            
        }
    };
    xhr.send(JSON.stringify(data));
}

function closePopup() {
    var popup = document.getElementById('popup');
    popup.style.display = 'none';
}
