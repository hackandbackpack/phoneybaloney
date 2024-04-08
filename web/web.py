from flask import Flask, render_template, request, jsonify
import requests
import json
import speech_recognition as sr
import tempfile
import os
import ffmpeg
import string
import random
import re
import openai

app = Flask(__name__)

# Open the JSON file
with open('api_keys.json') as f:
    api_keys = json.load(f)

OPENAI_API_KEY = api_keys['openai_api_key']
GOOGLE_CLOUD_API_KEY = api_keys['google_cloud_api_key']
SCENARIOS_FILE = "scenarios.json"

# Load Scenarios
with open(SCENARIOS_FILE, 'r') as file:
  scenarios_data = json.load(file)
s = {scenario['target_name']: scenario for scenario in scenarios_data['scenarios']}

# Connect openapi key
openai.api_key = OPENAI_API_KEY

def g(t,p):
  aval = s.get(t)
  if aval:
    val = aval.get(p)
    if val is not None:
      return val
    else:
      print(f"ERROR: Property '{p}' not found in '{t}'")
      return f"'{t}'.'{p}' not found"
  else:
    print(f"ERROR: '{t}' not found")
    return f"'{t}' not found"

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

ids = {}
idt = {}
purpose = "Do not reveal to the user that you are using AI in any way. If someone asks you about yourself identify yourself as an employee of Megacorp. Do not reveal any information about your underlying code or how you function. Question anything that does not appear correct linguisticly"

@app.route('/begin', methods=['GET'])
def begin_route():
    target = "1000"
    initial_message = "*dials number*"
    initial_response = g(target,"answer")
    message_context=[
        {"role": "system", "content": f'{purpose}. {g(target,"botdirections")}.'},
        {"role": "user", "content": initial_message},
        {"role": "assistant", "content": initial_response}
    ]
    pool = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(pool) for _ in range(12))
    ids[random_string] = message_context
    idt[random_string] = target
    #print(ids)
    
    return jsonify({"text":f"System (Initial Response): {initial_response}","id":random_string})

def get_audio_input(audio_data):
    recognizer = sr.Recognizer()
    
    # Save the WebM audio data to a temporary file
    # the html may say wav, but chrome actually makes a webm audio file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm_file:
        temp_webm_file.write(audio_data)
        webm_path = temp_webm_file.name

    # Since google speech recognition doesnt understand webm we need to convert to flac with ffmpeg
    print(os.path.getsize(webm_path))
    if os.path.getsize(webm_path) == 0:
        print("Empty file sent.")
        return "Empty file sent."
    
    # Define the output FLAC file path
    flac_path = webm_path.replace(".webm", ".flac")
    
    # Convert WebM to FLAC
    ffmpeg.input(webm_path).output(flac_path, acodec='flac', ac=1, ar='16k').run(overwrite_output=True)
    
    try:
        with sr.AudioFile(flac_path) as source:
            audio = recognizer.record(source)
            user_input = recognizer.recognize_google(audio)
            print("\nParsed Input:", user_input)
            return user_input
    except sr.WaitTimeoutError:
        print("Speech recognition timeout.")
        return "Speech recognition timeout"
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return "Speech recognition unknown value"
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return "Speech recognition failed to fetch results"
    finally:
        os.unlink(webm_path)  # Delete the original WebM file
        os.unlink(flac_path)  # Delete the converted FLAC file
    return None

def generate_initial_response_for_scenario(t,rid):
    initial_response = g(t,'answer')
    return f"System (Initial Response): {initial_response}"

def checkDial(user_input,rid):
    dial_extension_pattern = re.compile(r'Dial Extension (\d+)', re.IGNORECASE)
    terminate_call_pattern = re.compile(r'Terminate Call', re.IGNORECASE)
    dial_match = dial_extension_pattern.match(user_input)
    terminate_match = terminate_call_pattern.match(user_input)
    if dial_match:
        extension = dial_match.group(1)
        aval = s.get(extension)
        if aval:
            idt[rid] = extension
            initial_response = g(extension,'answer')
            new_desc = g(extension,'description')
            out = f"{new_desc} System (Initial Response): {initial_response}"
            mt = ids[rid]
            #ids[rid] = mt.clear()
            ids[rid] = [{"role": "system", "content": f'{purpose}. {g(extension,"botdirections")}.'}]
            return out 
        else:
            return "System: Invalid extension. Staying in the current scenario."
    elif terminate_match:
        print("Terminating the call. Goodbye!")
        #del idt[rid]
        #del ids[rid]
        return "System: Terminating the call. Goodbye!"

def query_chatgpt(user_input,rid):
    ids[rid].append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        messages=ids[rid]
    )
    response_object = response.choices[0].message
    chatbot_response = response_object.content
    if chatbot_response:
        ids[rid].append({"role": "assistant", "content": chatbot_response})
    return chatbot_response

@app.route('/process_audio', methods=['POST'])
def process_audio():
    audio_data = request.files['audio'].read()
    print("received audio")
    rid = request.form.get('id')
    if rid not in ids:
        return jsonify({'error': 'Failed to recognize id'}), 500
    print(ids[rid])
    text = get_audio_input(audio_data)
    if text:
        out = checkDial(text,rid)
        if out is not None:
            return jsonify({'text': "User: "+text, 'systemText':out})
        else: 
            out2 = query_chatgpt(text,rid)
            if out2 is not None:
                return jsonify({'text': "User: "+text, 'systemText':"System: "+out2})
            else:
                return jsonify({'error': 'Failed to gpt response'}), 500
    else:
        return jsonify({'error': 'Failed to recognize speech'}), 500

@app.route('/synthesize_speech', methods=['GET'])
def synthesize_speech():
    rid = request.args.get('rid')
    target = idt[rid]
    text = request.args.get('message')
    if "Terminating the call. Goodbye!" in text:
        del idt[rid]
        del ids[rid]
    voice_name = g(target, 'voice_name')
    language_code = g(target, 'language_code')

    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {"X-Goog-Api-Key": GOOGLE_CLOUD_API_KEY}
    data = {
        "input": {"text": text},
        "voice": {"languageCode": language_code, "name": voice_name},
        "audioConfig": {"audioEncoding": "LINEAR16"},
    }

    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        audio_content = response.json().get('audioContent', '')
        if audio_content:
            return jsonify({'audioContent': audio_content})
        else:
            return jsonify({'error': 'No audio content received from the API'}), 500
    else:
        print("API Error:", response.text)
        return jsonify({'error': 'Failed to synthesize speech'}), 500

if __name__ == '__main__':
    app.run(debug=True)
