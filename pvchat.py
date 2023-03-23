import sys
import json
import openai
import os
import io
import pyttsx3
import pyaudio
import datetime
import pvporcupine
import audioop
import wave
import random
import requests, json  
from pvrecorder import PvRecorder
from dotenv import load_dotenv
from pydub import AudioSegment
from dateutil.parser import parse

keyword = "jarvis"
#MODEL = "gpt-3.5-turbo-0301"
MODEL = "gpt-3.5-turbo"
totalCost = 0

# Do you want to sample the microphone or get an input      
#isSampleMicrophone = False
isSampleMicrophone = True       
        
# createWakeWord - create the instance for recognising wakewords
def createWakeWord():
    global porcupine, keywords
    
    porc_key = os.environ["PICA_KEY"]

    # Define the keywords    
    keywords = []
    keywords.append( keyword )

    porcupine = pvporcupine.create( access_key=porc_key,
                                    keywords=keywords
                                    )
    
# detectWakeWord
def detectWakeWord():
    recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
    try:
        recorder.start()
        while True:
            keyword_index = porcupine.process(recorder.read())
            if keyword_index >= 0:
                print(f"Detected {keywords[keyword_index]}")
                break
    except KeyboardInterrupt:
        recorder.stop()
    finally:
        # print("Deleted recorder")
        recorder.delete()

def listModelNames():
    # List the available models
    models = openai.Model.list()
    chat_model_ids = [(model.id, model.created) for model in models["data"] if model.id.startswith("gpt")]
    for model_id, created in chat_model_ids:
        created_at = datetime.datetime.fromtimestamp(created)
        print(model_id, created_at)
            
# sampleWavToFile
# Records from the microphone and saves to file. I wanted more control over the thresholds
# and didn't want to 
def sampleWavToFile():
    # Set the parameters of the audio stream
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 5

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open the audio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    # Create a buffer to store the audio data
    frames = bytearray()

    # Don't waste any recording on sampling "silence"
    MIN_RECORD_SECONDS = 2
    MAX_RECORD_SECONDS = 10
    THRESHOLD = 1500
    
    minRecording = int( (RATE / CHUNK) * MIN_RECORD_SECONDS)
    maxRecording = int( (RATE / CHUNK) * MAX_RECORD_SECONDS)
    
    avg = 0
    minRms = 100000
    maxRms = 0
    silence = 0
    silenceWait = 0.25
    
    for i in range(0, maxRecording):
        data = stream.read(CHUNK)

        rms = audioop.rms(data, 2)
        
        avg += rms;       
        avgRms = avg / (i+1)
        
        minRms = min(rms, minRms)
        maxRms = max(rms, maxRms)
        
        #print("Avg:" + (str)(avgRms) )
        #print("Rms:" + (str)(rms) )
        
        lowerThreshold = ((avgRms - minRms) * 0.25) + minRms
        
        if( ( i > minRecording) and (rms < lowerThreshold)):
            silence+=1 / (RATE / CHUNK)
        else:
            frames += data
            
        if( silence > silenceWait ):
            print("Silence, stopping recording.")
            break
        
    print("Finished recording.")

    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # save the recorded audio as a WAV file
    with wave.open("audio.wav", 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(RATE)
        wav_file.writeframes(frames)    

    rangeRms = maxRms - minRms
    
    if( rangeRms > 100 ):
        #print("Large range: likely speech: " + str(rangeRms) )
        return True
    else:
        #print("Small range: likely silence: " + str(rangeRms) )
        return False
    
def convertToMp3():       
    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")
            
    # Import an audio file
    wav_file = AudioSegment.from_file(file = "audio.wav", format = "wav")
    
    # export audio to mp3 format
    wav_file.export("audio.mp3", format="mp3")        

def saveToFile(audio_data):
    # get the audio data in WAV format as a bytes object
    wav_bytes = audio_data.get_wav_data()
    
    if len( wav_bytes ) > 0:
    
        # create a temporary file to hold the audio data in WAV format
        with io.BytesIO(wav_bytes) as wav_buffer:
            # create an AudioSegment object from the WAV file
            audio_segment = AudioSegment.from_file(wav_buffer, format="wav")
        
        if os.path.exists("audio.mp3"):
            os.remove("audio.mp3")
        
        # export audio to mp3 format
        audio_segment.export("audio.mp3", format="mp3")

# getTranscription
# gets the transcription using the whisper API
def getTranscription():
    prompt = ""

    #print("Saved to file")
           
    try:
        # Send the file to whisper
        file = open("audio.mp3", "rb")
        transcription = openai.Audio.transcribe("whisper-1", file, language="en")
        file.close()
    except openai.error.APIError as e:
        print("Error message:", e.message)            
    else:    
        # Print the transcription
        prompt = transcription["text"]

    return prompt

def appendCurrentTime():
    # append the current time - so the AI has current time    
    current_time = datetime.datetime.now()
    return f"\nThe current date is {current_time:%#I:%M%p}.\n"
    

def appendCurrentDate():
    # append the current date - so the AI has current time    
    return f"\nThe current date is {date.today():%d-%m-%Y}.\n"

def calculateTokens(messages):
    global totalCost
    strMessage = str(messages)
    tokens =  len(strMessage) / 4
    # gpt-3.5-turbo	$0.002 / 1K tokens
    cost = (tokens / 1000) * 0.002
    totalCost += cost
    print( f"Estimated message cost ${cost:.6f}\nTotal cost is ${totalCost:.2f}" )

def appendCurrentWeather():
    # Enter your API key here
    weather_api_key = os.environ["WEATHER_KEY"]
     
    # base_url variable to store url
    base_url = "http://api.weatherapi.com/v1/current.json?key="+weather_api_key+"&q=Tynemouth"
        
    # get method of requests module
    # return response object
    response = requests.get(base_url)
     
    # json method of response object
    # convert json format data into
    # python format data
    x = response.json()
     
    y = x["current"]
    
    return "\nThe current weather is " + str(y) + ".\n"

def appendNews():
    # Enter your API key here
    api_key =  os.environ["NEWS_KEY"]
    
    # only call the API if we have a key
    if len(api_key) == 0:
        return ""
        
    # base_url variable to store url
    base_url = "https://newsapi.org/v2/top-headlines?category=general&country=gb&apiKey="+api_key
        
    # get method of requests module
    # return response object
    response = requests.get(base_url)
     
    # json method of response object
    # convert json format data into
    # python format data
    x = response.json()
    numArticles = len( x["articles"]);
    
    #print("Number of articles " + str(numArticles) )
    
    myDictObj = {}
    
    for i in range(0, numArticles ):
        fullTitle = str( x["articles"][i]['title'] )
        url = str( x["articles"][i]['url'] )
        
        title = fullTitle.split('-')[0]
        myDictObj[i] = { "headline" : title }

    news = f"\nThe current news is {str(myDictObj)}.\n"
    print(news)
    
    text_file = open("news.txt", "w")
    n = text_file.write(news)
    text_file.close()

    return news
    
def say(reply):
    engine.say(reply)
    engine.runAndWait()        

def readPrompt(filename):
    with open(filename, 'r') as file:
        prompt = file.read()
    return prompt

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.environ["OPENAI_API_KEY"]

# Set API key for OpenAI package
openai.api_key = api_key

# List the OpenAI model names
listModelNames()

# WAKE WORD CODE
# Get API key from environment variable
createWakeWord()

# initialize the pyttsx3 engine
engine = pyttsx3.init()

# Read the prompt
prompt = readPrompt('prompt1.txt')

# Seed the news at the start of our conversation
prompt += appendNews()

# initialize the conversation
messages = [
    {"role": "user", "content": prompt},
]
#print(messages)

print("Starting main loop")

# set properties of the engine
engine.setProperty('rate', 180)  # speed of the voice in words per minute
engine.setProperty('volume', 1.0)  # volume level (ranges from 0 to 1)

try:
    # main loop
    while True:
    
        # print messages
        text_file = open("messages.txt", "w")
        for t in messages:
            n = text_file.write( t["content"] + "\n" )
        text_file.close()
        
        # print the cost
        calculateTokens(messages)
        
        if isSampleMicrophone:
            
            print("Use the wake word: " + keyword)
                       
            # detect the wake word
            detectWakeWord()    
            
            userPrompt = random.randint(1,3)
            if( userPrompt == 1 ):
                say("yes")
            if( userPrompt == 2 ):
                say("go on")
            if( userPrompt == 3 ):
                say("huh")
                  
            # Sample 
            if( sampleWavToFile() ):
            
                # Convert to mp3
                convertToMp3()

                # Translate the audio file
                prompt = getTranscription()
                
                #print("User utterance: " + prompt)
                
            else:
                prompt = ""
                
        else:
            print("Input:")
            
            # allow a user to enter an input
            prompt = input()

        # Check we have a valid prompt
        if len(prompt) > 0:
        
            finalPrompt = ""
            
            print("User prompt was " + prompt)
            
            # we can give the chat prompt additional information here
            # like the time
            
            finalPrompt = ""
            
            # alternative prepend the current time
            timeKeywords = ['hour', 'time', 'clock', 'watch']
            if any([x in prompt for x in timeKeywords]):
                #print("The user may ask about time")
                finalPrompt += appendCurrentTime()
           
            # alternative prepend the current date
            dateKeywords = ['date','calendar','month','year','day']
            if any([x in prompt for x in dateKeywords]):
                #print("The user may ask about time")
                finalPrompt += appendCurrentDate()
                
            # alternative prepend information about the weather
            weatherKeywords = ['weather', 'temperature', 'wind', 'rain', 'snow']
            if any([x in prompt for x in weatherKeywords]):
                finalPrompt += appendCurrentWeather()
                
            finalPrompt += prompt
      
            #newsKeywords = ['news', 'headline', 'world', 'latest', 'happening']
            #if any([x in prompt for x in newsKeywords]):
            #    prompt += appendNews()
                          
            #print(prompt)
                
            # append the users prompt            
            messages.append({"role": "user", "content": finalPrompt})
        
            # debug the prompt
            # print("prompt is \"" + prompt + "\"")
            
            # create the completion request
            try:
                # set up the parameters for gpt-3.5-turbo  
                chat = openai.ChatCompletion.create(
                    model=MODEL,
                    messages=messages,
                    temperature=0   # most deterministic temperatore - 
                    # 0 is zero arousel. 1 is more blue sky thinking
                )
                reply = chat.choices[0].message.content

                messages.append({"role": "assistant", "content": reply})

            except openai.error.APIError as e:
                print("Error message:", e.message)
            else:
                # process reply
                newsKeywords = ['[https']
                if any([x in reply for x in newsKeywords]):
                    print("Reply will be a special case fetch")
                else:
                    print(reply)                
                    say(reply)
        else:
            print("Nothing was said")
        
except KeyboardInterrupt:
    pass   

# delete resources
porcupine.delete()

print("Done.")