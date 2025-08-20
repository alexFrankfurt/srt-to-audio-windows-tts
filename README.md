# srt-to-audio-windows-tts
Translate audio to english.
Transform subtitles to timed audio.


# Origin
100% AI Generated

# Instruction

1. Generate srt from audio file using OpenAI Whisper:

```
 whisper .\ReelAudio-24214.mp3 --task translate --model medium
```

2. Run script to generate english audio
```
 python .\srt_to_timed_audio.py
```


