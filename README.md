# PhoneyBaloney #
PhoneyBaloney is Python based vishing simulator. Using OpenAI and Google Text to Speech it allows a user to have an interactive conversation with designed scenarios, originally designed as a CTF platform for use at security conventions.
Shout out to Brandon for the original thought <3 - (https://github.com/brandonscholet/MakeAVish)

Honestly, this is my first "larger" python project and I had a lot of help from Google and ChatGPT to make this happen. My code sucks, but it works. Happy to hear about any optimization or improvements I can make. Find me and let's talk about it. Twitter @hackandbackpack or on Discord - RedSiege.com/Discord

## Simple Installation ##
```
1. git clone https://github.com/hackandbackpack/phoneybaloney.git
2. cd phoneybaloney
3. pip install -r requirements.txt
4. If on Linux you might need to install portaudio for pyaudio to install properly -
   pip install portaudio19-dev
   Mac OSX users you will need to install portaudio for pyaudio to install propertly -
   brew install portaudio19-dev
```

## Website

There is a website you can use as well in the web folder

## Usage ##
python3 phoneybaloney.py

You will need a microphone to interact with phoneybaloney as it only allows for input via voice. After the launching the script you are ready to talk your way through the scenarios that have been designed.

With how it is designed currently, phoneybaloney imitates a company called MegaCorp. Upon starting the script you are immediately greeted by the operator and using your voice, you will need to use common vishing setups to move throughout the company. The generation is done by OpenAI so there are lots of ways to get sucked in as it imagines things that I didn't account for while writing the scenarios, if it seems like it is going off the rails ... it probably is. 

You will learn quickly that you will need to talk to multiple "people" at MegaCorp to unlock all your goals. This is accomplished by discovering extensions for employees. Since phoneybaloney only supports voice input, you dial different extensions by saying the phrase 'DIAL EXTENSION ####'.
You can also end the program by saying the phrase 'TERMINATE CALL'

Good luck.

## Tips ##
All the flags are gained by getting employees of MegaCorp to reveal their passwords.

There are no external sources that have information on Megacorp. So anything you need you can learn from a Megacorp employee ... if you ask the right questions.

For some added realism I added male and female voices, however OpenAI doesn't recognize whether the caller (you) are male or female should you want to pretend to be someone else.

Like most companies employees behave differently.

## ToDo ##
Clean up code and work out kinks.
Release version where users can write their own scenarios.
