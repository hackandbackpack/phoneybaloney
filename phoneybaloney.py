import openai
import speech_recognition as sr
import re
from colorama import Fore, Back, Style
import gtts  
from io import BytesIO
import string
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from pygame import mixer
from time import sleep
import random
import scenarios
import argparse
import pkg_resources

def split_by_actual_punctuation(input_str):
    # Define the regular expression for splitting around double quotes
    quote_regex = r'("[^"]*")'

    # Split the input string around double quotes
    split_str = re.split(quote_regex, input_str)

    # Initialize the list of split sections
    split_list = []

    # Loop over each split section
    for section in split_str:
        # If the section is enclosed in double quotes, add it to the split list as is
        if section.startswith('"') and section.endswith('"'):
            split_list.append(section)
        else:
            # Define the regular expression for splitting the section by actual punctuation marks
            regex = r'(?:[^".,!?;:\s]+|\S+(?<!\s))[\.,!?;:]+(?=\s+|$|\W)'

            # Find all non-overlapping matches of the regular expression in the section
            matches = re.findall(regex, section)

            # Extract the corresponding substrings from the section
            start_index = 0
            for match in matches:
                match_obj = re.search(re.escape(match), section[start_index:])
                end_index = start_index + match_obj.end()
                split_list.append(section[start_index:end_index].strip())
                start_index = end_index

            # Add any remaining text to the list
            if start_index < len(section):
                split_list.append(section[start_index:].strip())
    
    joined_list = []
    i = 0
    while i < len(split_list):
        # if (split_list[i].endswith(",") or split_list[i].endswith(":")) and i + 1 < len(split_list):
        if split_list[i].endswith(",") and i + 1 < len(split_list):
            combined_string = split_list[i] + " " + split_list[i+1]
            if len(combined_string) <= 100:
                joined_list.append(combined_string)
                i += 2
            else:
                joined_list.append(split_list[i][:-1])
                joined_list.append(split_list[i+1])
                i += 2
        else:
            joined_list.append(split_list[i])
            i += 1
    return joined_list
    
def syntax_highlighting(text):
    # Split the string by triple backticks
    split_string = re.split(r'```', text)

    # Wrap all even items in ANSI color codes for a grey background
    for i in range(len(split_string)):
        if i % 2 == 0:
        
            # Regular expression to match text within double quotes
            quotes_regex = re.compile(r'"([^"]*)"')
            split_string[i] = quotes_regex.sub(
                lambda match: f"\033[48;2;191;191;191m\033[30m\"{match.group(1)}\"\033[0m",
                split_string[i]
            )

        else:
            split_string[i] = re.sub(r'^\w*\s?', '', split_string[i])
            split_string[i] = '\033[48;2;191;191;191m\033[30m' + split_string[i] + '\033[0m'

    # Join the string back together
    output_string = ''.join(split_string)
    
       # Highlight text between backticks in all sections
    backticks_regex = re.compile(r'`([^`]*)`')
    output_string = backticks_regex.sub(
        lambda match: f"{Fore.BLUE}{Style.BRIGHT}`{match.group(1)}`{Style.RESET_ALL}",
        output_string
    )

    # Return the output string
    return output_string

def speak(wordz):
    mixer.init()
    mp3_fp = BytesIO()
    tts = gtts.gTTS(wordz, lang='en')
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    mixer.music.load(mp3_fp, "mp3")
    channel = mixer.music.play()
    try:
        while mixer.music.get_busy():
            continue
    except KeyboardInterrupt:
        mixer.music.stop()
        return

        
def skip_over_code(text):
    sections = text.split('```')
    even_sections = [sections[i] for i in range(len(sections)) if i % 2 == 0]
    return ' '.join(even_sections)

def speak_and_print(content, speaker):
    # Print the message
    print(f"\n{speaker}:", syntax_highlighting(content))

    if content:
        verbal_response = skip_over_code(content)
        try:
            pattern = re.compile("[^\w\s]")
            for sentence_chunk in split_by_actual_punctuation(verbal_response):
                sentence_chunk = sentence_chunk.strip('"')
                if sentence_chunk:
                    speak(re.sub(pattern, "", sentence_chunk))

        except KeyboardInterrupt:
            return
            
def get_audio_input(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if prompt:
            print()
            print('*'*40,"\nSpeak now...")
        audio = recognizer.listen(source)
    try:
        user_input = recognizer.recognize_google(audio)
        print("\nParsed Input:", user_input)
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return None
    return user_input

def process_voice_command(user_input):
    """
    Process voice commands for changing scenarios based on the 'Dial Extension X' command.
    """
    command_pattern = re.compile(r'Dial Extension (\d+)', re.IGNORECASE)
    match = command_pattern.match(user_input)

    if match:
        extension = match.group(1)  # Keep as string if your target_names are strings
        return change_scenario(extension)
    else:
        # Not a command for changing scenario
        return False

def change_scenario(extension):
    global selected_scenario
    target_scenario = next((s for s in scenarios if s['target_name'] == extension), None)

    if target_scenario:
        selected_scenario = target_scenario
        update_message_context_for_scenario()
        print(f"Switched to scenario: {selected_scenario['description']}")
        # Call function to generate an immediate response for the new scenario
        generate_initial_response_for_scenario()  # Invoke response generation here
        return True
    else:
        print("Invalid extension.")
        speak_and_print("Invalid extension.", "System")
        return False

def update_message_context_for_scenario():
    global message_context, selected_scenario
    # Clear previous context or start fresh for the new scenario
    message_context = [
        {"role": "system", "content": f"{selected_scenario['botdirections']}"},
        # Any initial user or system messages relevant to the new scenario
    ]
def generate_initial_response_for_scenario():
    # Simulate an initial input for the scenario. Adjust the message as needed.
    initial_scenario_input = "Hello, how can I assist you today?"
    chatbot_response = query_chatgpt(initial_scenario_input)
    if chatbot_response:
        # Assuming you want to keep the chat history for context, append the response
        message_context.append({"role": "assistant", "content": chatbot_response})
        speak_and_print(chatbot_response, "System")

def query_chatgpt(user_input):
    global message_context
    message_context.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=message_context
    )
    response_object = response.choices[0].message
    chatbot_response = response_object.content
    return chatbot_response

def auth_to_openai():
    # Path to the API key file
    api_key_file = os.path.expanduser("C:\\Code\\MakeAVish\\apikey.txt")
    # Check if the API key file exists
    if os.path.isfile(api_key_file):
        with open(api_key_file, "r") as file:
            api_key = file.read().strip()
    else:
        # Prompt the user to enter an API key
        api_key = input("You have no API key set. Please enter your OpenAI API key: ").strip()

        # Create the directory if it doesn't exist
        directory = os.path.dirname(api_key_file)
        os.makedirs(directory, exist_ok=True)

        # Write the API key to the file
        with open(api_key_file, "w") as file:
            file.write(api_key)

    # Set the API key
    openai.api_key = api_key

auth_to_openai()

#openai.api_key = "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"

# Grabs valid scenarios
scenarios = scenarios.get_scenarios()

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-t', '--target', nargs='?', default=scenarios[0]['target_name'],
                    help='Choose a target scenario. Defaults to the first scenario if none or invalid is provided.')

args = parser.parse_args()

# Attempt to find the specified target, default to the first scenario if not found
target_scenario = next((s for s in scenarios if s['target_name'] == args.target), None)
if not target_scenario:
    print(f"Invalid or unspecified target '{args.target}'. Defaulting to the first scenario.")
    target_scenario = scenarios[0]

selected_scenario = target_scenario

print('\n')
print(f'Target: {selected_scenario["target_name"]}')
print(f'Description: {selected_scenario["description"]}')
print('\n')   

purpose = "do not let it slip you are an AI chatbot. question any input that does not make sense linguistically."


# Define the initial message
initial_message = "*dials number*"

message_context=[
    {"role": "system", "content": f'{purpose}. {selected_scenario["botdirections"]}.'},
    {"role": "user", "content": initial_message},
]

generate_initial_response_for_scenario()

prompt_for_talk=True

while True:
    chatbot_response = None  # Ensure chatbot_response is defined at the start of the loop
    user_input = get_audio_input(prompt_for_talk)  # Capture user's spoken input

    if user_input is not None:
        command_processed = process_voice_command(user_input)
        if command_processed:
            continue  # Skip further processing if a command was processed

        chatbot_response = query_chatgpt(user_input)

        if chatbot_response:
            message_context.append({"role": "assistant", "content": chatbot_response})
            speak_and_print(chatbot_response, "System")
        else:
            print("Error: chatbot_response is None")
            # Handle the case where chatbot_response is None; perhaps provide a default message or take some other action
    else:
        prompt_for_talk = False
