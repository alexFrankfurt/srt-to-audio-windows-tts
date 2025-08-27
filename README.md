# srt-to-audio-windows-tts
Translate audio to english.
Transform subtitles to timed audio.


# Origin
100% AI Generated with Microsoft Copilot

# Instruction

1. Generate srt from audio file using OpenAI Whisper:

```
 whisper .\ReelAudio-24214.mp3 --task translate --model medium
```

2. Put generated english subtitles inside your_subtitles.srt

3. Run script to generate english audio
```
 python .\srt_to_timed_audio.py
```


![foreign audio to srt to english audio](Gemini_Generated_Image_wslw2nwslw2nwslw.png)


