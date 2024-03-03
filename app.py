from flask import Flask, request, jsonify, render_template, render_template_string, redirect
import xml.etree.ElementTree as ET
import requests

import json
# from SimilarSentences import SimilarSentences
import json
from flask import Flask, request, jsonify, render_template, render_template_string, redirect
from pymongo import MongoClient
import openai

app = Flask(__name__)

username=""
chat=[]

intent=""
question=""
answer=""
intent_answers=[]
message=""
sim_sens=[]
# model = SimilarSentences('model.zip',"predict")

client=MongoClient() 
client = MongoClient("mongodb://localhost:27017/") 
mydatabase = client["database1"] 
mycollection=mydatabase["similar_questions"]


@app.route('/flaskapp/bot',methods=['GET','POST'])
def bot_page():
    global username
    username = request.args.get('username')
    print(username)
    print(chat)
    tree = ET.parse(f"{username}.xml")
    root = tree.getroot()
    title = root.find('title').text
    icon = root.find('icon').text
    return render_template('bot.html',username=username,title=title,chat=chat,icon=icon)

@app.route('/msg',methods=["GET","POST"])
def msg():
    global chat
    data = request.get_json()
    print(data)
    prompt = data.get("prompt")
    try:
        rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
        payload = {'sender':username,'message': prompt}
        response = requests.post(rasa_url, json=payload)
        print("payload:",payload)
        rasa_data = response.json()
        print("Rasa data:",rasa_data)
        res = rasa_data[0]['text']
        print("Rasa's response:",res)
        if res!="404":
            chat.append({prompt:res})
            print("Chat:",chat)
            return jsonify({'reply': res})
        else:
            chat.append({prompt:"Sorry I can't answer that."})
            return jsonify({'reply': "Sorry I can't answer that."})
    except:
        return jsonify({'reply': "Something is wrong.....!"})


'''def rewrite():
    root = ET.Element("data")

    for intent, answer in intent_answers:
        intent_elem = ET.SubElement(root, "intent", category=intent)
        answer_elem = ET.SubElement(intent_elem, "answer")
        answer_elem.text = answer

    tree = ET.ElementTree(root)
    tree.write(f"{username}.xml", encoding="UTF-8", xml_declaration=True)'''

def rewrite():
    tree = ET.parse(f'{username}.xml')
    root = tree.getroot()

    new_element = ET.Element('intent', category=intent)
    answer_element = ET.SubElement(new_element, 'answer')
    answer_element.text = answer

    root.append(new_element)

    tree.write(f'{username}.xml')

@app.route('/delete',methods=['GET','POST'])
def delete():
    global intent_answers
    global username
    tree = ET.parse(f'{username}.xml')
    root = tree.getroot()
    category = request.form.get('category')
    print("Category to delete:",category)
    intent_answers = [(intent, answer) for intent, answer in intent_answers if intent != category]
    #rewrite()
    node = root.find('.//intent[@category="{}"]'.format(category))
    root.remove(node)
    tree.write(f'{username}.xml')
    return redirect(f'/flaskapp/configurecompanyquestion?username={username}')

@app.route('/flaskapp/configurecompanyquestion',methods=['GET','POST'])
def hello_world():
    global username
    global intent_answers
    global message
    username = request.args.get('username')
    #print("Username:",username)
    try:
        result = []
        tree = ET.parse(f"{username}.xml")
        root = tree.getroot()
        for tag in root.findall('intent'):
            intent = tag.get('category')
            answer = tag.find('answer').text
            result.append((intent,answer))
        intent_answers = result
        #print(intent_answers)
        message2=message
        message=""
        print(message2,message)
        return render_template('I&T.html',result=intent_answers,message=message2,username=username)
    
    except:
        return 'Not a valid user name....!'
    # return render_template('Home.html')

@app.route('/check',methods=['GET','POST'])
def check():
    global username
    global intent_answers
    global message
    global intent
    global question
    global answer
    print("Chiru")
    data = request.get_json()
    print(data)
    intent = data.get('intent')
    question = data.get('question')
    answer = data.get('answer')
    # intent,question,answer = request.form.get('intent'),request.form.get('question'),request.form.get('answer')
    
    try:
        rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
        payload = {'message': question}
        response = requests.post(rasa_url, json=payload)
        print("Rasa's response:",response)

        rasa_data = response.json()
        print("Rasa data:",rasa_data)
        intent_trig = rasa_data[0]['text']
        print("Intent triggered:",intent_trig)
        if intent_trig!="404":
            # message="Intent already exists...!"
            # return render_template('Home.html',result=intent_answers,message="Intent already exists..!")
            # return redirect(f'/flaskapp/configurecompanyquestion?username={username}')
            return jsonify({'predictions': "404"})
        else:
            return predict()
            # message=""
        # intent_answers.append((intent,answer))
        # rewrite()
        # return redirect(f'/flaskapp/configurecompanyquestion?username={username}')
    except:
        return 'something went wrong...!'
    



def predict():
    global question
    global sim_sens
    #try:
    openai.api_key = '<YOUR-API-KEY>'
    mess = [ {"role": "system", "content":
			"You are a intelligent assistant."} ]
    prompt = f"Give me similar questions for this sentence '{question}'"
    print("Prompt:",prompt)
    mess.append(
		{"role": "user", "content": prompt},
        )
    chat = openai.ChatCompletion.create(
			model="gpt-3.5-turbo", messages=mess
        )
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    mess.append({"role": "assistant", "content": reply})
    sim_sens = reply.split('\n')
    return jsonify({'predictions': sim_sens})
    '''except:
        predictions = model.predict(question, 5, "simple")
        sim_sens = predictions[2:-2].split('", "')
        sim_sens = list(set(sim_sens))
        return jsonify({'predictions': sim_sens})'''


@app.route("/save",methods=["POST","GET"])
def save():
    intent_answers.append((intent,answer))
    rewrite()
    save_ques()
    return redirect(f'/flaskapp/configurecompanyquestion?username={username}')


def save_ques():
    global question
    global sim_sens
    sim_sens.insert(0,question)
    print(question,sim_sens)
    data = {
        intent:sim_sens
    }
    print(data)
    data_in = mycollection.insert_one(data)
    print(data_in)


# replacing the actions.py
    
@app.route('/webhook',methods=["GET","POST"])
def webhook():
    try:
        data = request.json
        #print(data)
        user_message = data.get("tracker", {}).get("latest_message", {}).get("text", "")
        id = data.get('sender_id',"")
        intent_trig = data.get("tracker", {}).get("latest_message", {}).get("intent", {}).get("name","")
        print("Intent triggered:",intent_trig)
        var = " h"
        try:
            #BRClientdata.xml
            tree = ET.parse("data.xml")
            root = tree.getroot()

            client_id = id.split('_')[0]
            path = root.find(f".//client[@name='{client_id}']/path").text
            tree2 = ET.parse(f'{path}')
            root2 = tree2.getroot()
            client_data = root2.find(f".//intent[@category='{intent_trig}']/answer").text
            print(client_data)
            var = var[0]+client_data
        except:
            var = var[0]+"failed"

        rasa_response = {
        "responses": [
            {
                "text": var,
            }
            ]
            }

        return jsonify(rasa_response)

        # return id
    except:
        return 'Hello man man!!!!!!!!!!!!!!!'
    





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5056)