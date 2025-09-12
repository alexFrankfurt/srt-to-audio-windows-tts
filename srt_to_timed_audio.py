import asyncio
import srt
import os
import logging
from datetime import timedelta
from edge_tts import Communicate
from pathlib import Path
import subprocess
import string
from openai import OpenAI
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_speakable(text):
    return any(char.isalnum() for char in text)

# Configuration
VOICE = "en-US-JennyNeural"  # Default edge-tts voice
SAMPLE_RATE = 24000
OUTPUT_DIR = "output_audio"
SRT_FILE = "your_subtitles.srt"
FINAL_AUDIO = "final_output.mp3"

# TTS Method configuration
TTS_METHOD = os.getenv("TTS_METHOD", "edge_tts")  # Options: "edge_tts", "openai_tts"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_VOICE = "alloy"  # OpenAI TTS voice options: alloy, echo, fable, onyx, nova, shimmer

def seconds(td):
    return td.total_seconds()

def generate_silence(duration, filename):
    """Generate silence audio file using FFmpeg"""
    try:
        cmd = [
            "ffmpeg", "-f", "lavfi", "-t", str(duration),
            "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
            "-q:a", "9", "-acodec", "libmp3lame", filename, "-y"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info(f"Generated silence file: {filename} ({duration}s)")
    except subprocess.CalledProcessError as e:
        error_condition = f"FFmpeg silence generation failed for {filename}"
        logger.error(f"Error condition: {error_condition}, Error: {e}")
        raise

async def generate_audio_edge_tts(text, filename):
    """Generate audio using Edge TTS (original method)"""
    try:
        communicate = Communicate(text, VOICE)
        await communicate.save(filename)
        logger.info(f"Generated Edge TTS audio: {filename}")
    except Exception as e:
        error_condition = f"Edge TTS generation failed for text: {text[:50]}..."
        logger.error(f"Error condition: {error_condition}, Error: {e}")
        raise

async def generate_audio_mock_edge_tts(text, filename):
    """Generate mock Edge TTS audio for testing purposes when internet is not available"""
    try:
        # Create a simple MP3 file with silent audio for testing
        duration = min(len(text) * 0.1, 5.0)  # Estimate duration based on text length
        cmd = [
            "ffmpeg", "-f", "lavfi", "-t", str(duration),
            "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
            "-q:a", "9", "-acodec", "libmp3lame", filename, "-y"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info(f"Generated mock Edge TTS audio: {filename} (duration: {duration}s)")
        
    except Exception as e:
        error_condition = f"Mock Edge TTS generation failed for text: {text[:50]}..."
        logger.error(f"Error condition: {error_condition}, Error: {e}")
        raise

def generate_audio_openai_tts(text, filename):
    """Generate audio using OpenAI TTS (alternative language model approach)"""
    try:
        # Check if API key is available
        api_key_available = OPENAI_API_KEY is not None and OPENAI_API_KEY.strip() != ""
        if not api_key_available:
            error_condition = "OpenAI API key not available"
            logger.error(f"Error condition: {error_condition}")
            raise ValueError("OpenAI API key not set. Set OPENAI_API_KEY environment variable.")
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=OPENAI_VOICE,
            input=text
        )
        
        response.stream_to_file(filename)
        logger.info(f"Generated OpenAI TTS audio: {filename}")
        
    except Exception as e:
        error_condition = f"OpenAI TTS generation failed for text: {text[:50]}..."
        logger.error(f"Error condition: {error_condition}, Error: {e}")
        raise

def generate_audio_mock_tts(text, filename):
    """Generate mock audio for testing purposes when internet is not available"""
    try:
        # Create a simple MP3 file with silent audio for testing
        duration = min(len(text) * 0.1, 5.0)  # Estimate duration based on text length
        cmd = [
            "ffmpeg", "-f", "lavfi", "-t", str(duration),
            "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
            "-q:a", "9", "-acodec", "libmp3lame", filename, "-y"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info(f"Generated mock TTS audio: {filename} (duration: {duration}s)")
        
    except Exception as e:
        error_condition = f"Mock TTS generation failed for text: {text[:50]}..."
        logger.error(f"Error condition: {error_condition}, Error: {e}")
        raise

async def generate_audio(text, filename):
    """Generate audio using selected TTS method"""
    method_is_openai = TTS_METHOD.lower() == "openai_tts"
    use_mock_mode = os.getenv("USE_MOCK_TTS", "false").lower() == "true"
    
    if use_mock_mode:
        logger.info(f"Using Mock TTS (testing mode) for: {text[:50]}...")
        if method_is_openai:
            generate_audio_mock_tts(text, filename)
        else:
            await generate_audio_mock_edge_tts(text, filename)
    elif method_is_openai:
        logger.info(f"Using OpenAI TTS (language model approach) for: {text[:50]}...")
        generate_audio_openai_tts(text, filename)
    else:
        logger.info(f"Using Edge TTS (traditional approach) for: {text[:50]}...")
        await generate_audio_edge_tts(text, filename)

def load_whisper_txt_output(input_audio_path: str) -> Optional[str]:
    """
    Load Whisper's .txt output (most straightforward text output).
    This is the alternative approach using language model's direct text output.
    """
    try:
        # Get the base name of the input audio file
        base_name = Path(input_audio_path).stem
        txt_file = f"{base_name}.txt"
        
        txt_file_exists = os.path.exists(txt_file)
        if not txt_file_exists:
            error_condition = f"Whisper .txt output not found: {txt_file}"
            logger.error(f"Error condition: {error_condition}")
            return None
            
        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        logger.info(f"Loaded Whisper .txt output from {txt_file}: {len(content)} characters")
        return content
        
    except Exception as e:
        error_condition = f"Failed to load Whisper .txt output from {txt_file}"
        logger.error(f"Error condition: {error_condition}, Error: {e}")
        return None

async def process_srt_based(srt_file_path: str):
    """Process audio generation using SRT file (original timing-based approach)"""
    logger.info("Using SRT-based processing (original approach)")
    
    try:
        srt_file_readable = os.path.exists(srt_file_path)
        if not srt_file_readable:
            error_condition = f"SRT file not found: {srt_file_path}"
            logger.error(f"Error condition: {error_condition}")
            raise FileNotFoundError(f"SRT file not found: {srt_file_path}")
            
        with open(srt_file_path, "r", encoding="utf-8") as f:
            subs = list(srt.parse(f.read()))

        concat_list = []
        current_time = timedelta(seconds=0)

        for i, sub in enumerate(subs, 1):
            text = sub.content.strip().replace("\n", " ")

            text_is_speakable = is_speakable(text)
            if not text_is_speakable:
                logger.info(f"⏭️ Skipping non-speakable subtitle #{i}: {repr(text)}")
                current_time = sub.end
                continue
                
            # Skip empty lines
            text_is_empty = not text
            if text_is_empty:
                logger.info(f"⏭️ Skipping empty subtitle #{i}")
                current_time = sub.end
                continue

            # Add silence if there's a gap
            gap_exists = sub.start > current_time
            if gap_exists:
                gap = seconds(sub.start - current_time)
                silence_file = f"{OUTPUT_DIR}/silence_{i:03}.mp3"
                generate_silence(gap, silence_file)
                concat_list.append(silence_file)

            # Generate speech
            audio_file = f"{OUTPUT_DIR}/line_{i:03}.mp3"
            logger.info(f"🔊 Generating audio for line {i}: {text}")
            await generate_audio(text, audio_file)
            concat_list.append(audio_file)

            current_time = sub.end

        return concat_list
        
    except Exception as e:
        error_condition = f"SRT processing failed for file: {srt_file_path}"
        logger.error(f"Error condition: {error_condition}, Error: {e}")
        raise

async def process_txt_based(whisper_txt_content: str):
    """Process audio generation using Whisper .txt output (alternative approach)"""
    logger.info("Using TXT-based processing (alternative language model approach)")
    
    try:
        # Split text into sentences for more natural audio generation
        sentences = []
        current_sentence = ""
        
        for char in whisper_txt_content:
            current_sentence += char
            sentence_end_reached = char in '.!?'
            if sentence_end_reached and len(current_sentence.strip()) > 10:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # Add any remaining text
        remaining_text_exists = current_sentence.strip()
        if remaining_text_exists:
            sentences.append(current_sentence.strip())
        
        concat_list = []
        
        for i, sentence in enumerate(sentences, 1):
            sentence_is_speakable = is_speakable(sentence)
            if not sentence_is_speakable:
                logger.info(f"⏭️ Skipping non-speakable sentence #{i}: {repr(sentence[:50])}...")
                continue
                
            audio_file = f"{OUTPUT_DIR}/sentence_{i:03}.mp3"
            logger.info(f"🔊 Generating audio for sentence {i}: {sentence[:50]}...")
            await generate_audio(sentence, audio_file)
            concat_list.append(audio_file)
        
        return concat_list
        
    except Exception as e:
        error_condition = f"TXT processing failed for content length: {len(whisper_txt_content)}"
        logger.error(f"Error condition: {error_condition}, Error: {e}")
        raise

async def main():
    """Main function with enhanced error handling and alternative approaches"""
    try:
        logger.info(f"Starting TTS processing using method: {TTS_METHOD}")
        
        Path(OUTPUT_DIR).mkdir(exist_ok=True)
        
        # Check for alternative approach using Whisper .txt output
        use_txt_approach = os.getenv("USE_TXT_APPROACH", "false").lower() == "true"
        
        concat_list = []
        
        if use_txt_approach:
            logger.info("Alternative approach selected: Using Whisper .txt output")
            
            # Look for any .txt file in the current directory (most likely Whisper output)
            txt_files = list(Path(".").glob("*.txt"))
            txt_files_found = len(txt_files) > 0
            
            if txt_files_found:
                # Use the first .txt file found (most straightforward approach)
                txt_file = txt_files[0]
                logger.info(f"Using .txt file: {txt_file}")
                
                with open(txt_file, "r", encoding="utf-8") as f:
                    txt_content = f.read().strip()
                
                concat_list = await process_txt_based(txt_content)
            else:
                error_condition = "No .txt files found for alternative approach"
                logger.error(f"Error condition: {error_condition}")
                logger.info("Falling back to SRT-based approach")
                use_txt_approach = False
        
        srt_approach_needed = not use_txt_approach
        if srt_approach_needed:
            logger.info("Standard approach selected: Using SRT file")
            concat_list = await process_srt_based(SRT_FILE)

        # Write concat list
        concat_txt = "concat_list.txt"
        concat_list_has_files = len(concat_list) > 0
        
        if not concat_list_has_files:
            error_condition = "No audio files generated for concatenation"
            logger.error(f"Error condition: {error_condition}")
            raise ValueError("No audio files were generated")
            
        with open(concat_txt, "w", encoding="utf-8") as f:
            for file in concat_list:
                f.write(f"file '{file}'\n")

        logger.info(f"Generated {len(concat_list)} audio segments")

        # Stitch everything together
        logger.info("Concatenating audio files...")
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", concat_txt, "-c", "copy", FINAL_AUDIO, "-y"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        final_audio_created = os.path.exists(FINAL_AUDIO)
        if final_audio_created:
            file_size = os.path.getsize(FINAL_AUDIO)
            logger.info(f"✅ Done! Final audio saved as: {FINAL_AUDIO} ({file_size} bytes)")
        else:
            error_condition = "Final audio file was not created despite successful FFmpeg execution"
            logger.error(f"Error condition: {error_condition}")
            raise RuntimeError("Final audio file was not created")
            
    except Exception as e:
        error_condition = f"Main processing failed"
        logger.error(f"Error condition: {error_condition}, Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
