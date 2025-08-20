import asyncio
import srt
import os
from datetime import timedelta
from edge_tts import Communicate
from pathlib import Path
import subprocess
import string

def is_speakable(text):
    return any(char.isalnum() for char in text)

VOICE = "en-US-GuyNeural"
VOICE = "en-US-JennyNeural"
SAMPLE_RATE = 24000
OUTPUT_DIR = "output_audio"
SRT_FILE = "your_subtitles.srt"
FINAL_AUDIO = "final_output.mp3"

def seconds(td):
    return td.total_seconds()

def generate_silence(duration, filename):
    cmd = [
        "ffmpeg", "-f", "lavfi", "-t", str(duration),
        "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
        "-q:a", "9", "-acodec", "libmp3lame", filename, "-y"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

async def generate_audio(text, filename):
    communicate = Communicate(text, VOICE)
    await communicate.save(filename)

async def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    with open(SRT_FILE, "r", encoding="utf-8") as f:
        subs = list(srt.parse(f.read()))

    concat_list = []
    current_time = timedelta(seconds=0)

    for i, sub in enumerate(subs, 1):
        text = sub.content.strip().replace("\n", " ")

        if not is_speakable(text):
            print(f"⏭️ Skipping non-speakable subtitle #{i}: {repr(text)}")
            current_time = sub.end
            continue
        # Skip empty lines
        if not text:
            print(f"⏭️ Skipping empty subtitle #{i}")
            current_time = sub.end
            continue

        # Add silence if there's a gap
        if sub.start > current_time:
            gap = seconds(sub.start - current_time)
            silence_file = f"{OUTPUT_DIR}/silence_{i:03}.mp3"
            generate_silence(gap, silence_file)
            concat_list.append(silence_file)

        # Generate speech
        audio_file = f"{OUTPUT_DIR}/line_{i:03}.mp3"
        print(f"🔊 Generating audio for line {i}: {text}")
        await generate_audio(text, audio_file)
        concat_list.append(audio_file)

        current_time = sub.end

    # Write concat list
    concat_txt = f"concat_list.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for file in concat_list:
            f.write(f"file '{file}'\n")

    # Stitch everything together
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", FINAL_AUDIO, "-y"
    ])

    print(f"✅ Done! Final audio saved as: {FINAL_AUDIO}")

asyncio.run(main())
