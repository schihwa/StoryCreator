
import subprocess
import re
from pydub import AudioSegment, silence
import pyttsx3
import pysubs2

def videoFormatter():
    #you can copy and paste your story here. hyphens ruin the timings of subtitles
    speech = """ your story """

    # deines required variables
    soundFile = "speech.wav"
    subtitlesFile = "script.ssa"
    videoFile = "test.mp4"
    backgroundSound = "test.mp3"
    video = "StoryTime.mp4"

    # creates audio file of the speech
    textToSpeech(speech, soundFile)

    # creates SSA file of the subtitlies
    subtitles(speech, soundFile, subtitlesFile)

    #cuts video appropriate for youtube shorts
    soundFileDuration = soundFile.SoundFile('speech.wav').frames / soundFile.SoundFile('speech.wav').samplerate
    if soundFileDuration > 60:
        soundFileDuration = 59

    #mute the original sound of the mp4 file and add the sound of the selected music and the Text to speech sound file
    command = [
            "ffmpeg",
            "-i", videoFile,
            "-i", soundFile,
            "-i", backgroundSound,
            "-filter_complex", "[1:a][2:a]amerge=inputs=2[a]",
            "-t", str(soundFileDuration),
            "-map", "0:v",
            "-map", "[a]",
            "-vf", f"subtitles={subtitlesFile}:force_style='Alignment=10,OutlineColour=&H100000000,Shadow=0,Fontsize=18,MarginL=5,MarginV=25'",
            "-crf", "1",
            video
        ]

    subprocess.run(command)


def textToSpeech(speech, soundFile):
    #Initialize the TTS engine
    engine = pyttsx3.init()

    #Set the voice to use
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    #Set the rate of speech
    engine.setProperty('rate', 170)

    #Set the volume
    engine.setProperty('volume', 1.0)

    #Set the pauses
    engine.setProperty('pause', 0.3)

    #Save the story to speech
    engine.save_to_file(speech, soundFile)
    engine.runAndWait()


def subtitles(speech, soundFile, subtitlesFile):
    #Split the story into sentences
    subtitles = re.split(r'[,.;:!?]', speech)
    subtitles = [sub.strip() for sub in subtitles if sub and not sub.isspace()]

    #Create the subtitles using pysrt
    subs = pysubs2.SSAFile()

    myaudio = AudioSegment.from_mp3(soundFile)
    dBFS = myaudio.dBFS
    silences = silence.detect_silence(
        myaudio, min_silence_len=40, silence_thresh=dBFS-1600)

    #put time stamps in silences
    silences = [((start), (stop)) for start, stop in silences]

    #Create a new list with time stamps between pauses
    time_stamps = []
    previous_end = silences[0][0]

    for i in range(1, len(silences)):
        start, stop = silences[i]
        time_stamps.append((previous_end, stop))
        previous_end = stop

    for i, sub in enumerate(subtitles):
        start, end = time_stamps[i]
        print(start, end)

        subs.append(pysubs2.SSAEvent(start=start, end=end, text=sub))

    subs.save(subtitlesFile)

videoFormatter()
