# Enhanced SRT-to-Audio with Alternative Language Model Approach

## New Features

### Alternative Text-to-Audio Processing
The enhanced script now supports two different approaches for text-to-audio conversion:

1. **Traditional SRT-based approach** (original): Uses timing information from SRT files
2. **Alternative TXT-based approach** (new): Uses Whisper's .txt output directly (most straightforward text output)

### Language Model TTS Options
- **Edge TTS** (traditional): Windows Text-to-Speech
- **OpenAI TTS** (language model approach): Advanced AI-powered text-to-speech
- **ChatterboxTTS** (production-grade open-source): High-quality voice synthesis with cloning capabilities

### Enhanced Error Handling
- All error conditions are assigned to variables and logged as requested
- Comprehensive logging with detailed error tracking
- Graceful fallback mechanisms

## Configuration Options

Set these environment variables to configure the enhanced behavior:

```bash
# Select TTS method
export TTS_METHOD=edge_tts          # Options: edge_tts, openai_tts, chatterbox_tts
export TTS_METHOD=openai_tts        # Use OpenAI language model approach
export TTS_METHOD=chatterbox_tts    # Use ChatterboxTTS production-grade open-source approach

# Select processing approach  
export USE_TXT_APPROACH=true        # Use Whisper .txt output (alternative)
export USE_TXT_APPROACH=false       # Use SRT timing-based approach (default)

# OpenAI TTS configuration (when using openai_tts method)
export OPENAI_API_KEY=your_api_key  # Required for OpenAI TTS
export OPENAI_VOICE=alloy           # Options: alloy, echo, fable, onyx, nova, shimmer

# ChatterboxTTS configuration (when using chatterbox_tts method)
export CHATTERBOX_EXAGGERATION=0.5  # Emotion intensity (0.25-2.0)
export CHATTERBOX_TEMPERATURE=0.1   # Randomness (0.05-5.0)
export CHATTERBOX_CFG_WEIGHT=0.5    # Guidance strength (0.0-1.0)

# Testing mode (for development/testing without internet)
export USE_MOCK_TTS=true            # Use mock TTS for testing
```

## Usage Examples

### Traditional Approach (SRT-based with Edge TTS)
```bash
python srt_to_timed_audio.py
```

### Alternative Approach (TXT-based with Edge TTS)
```bash
USE_TXT_APPROACH=true python srt_to_timed_audio.py
```

### Production-Grade Open-Source Approach (ChatterboxTTS with Edge TTS)
```bash
TTS_METHOD=chatterbox_tts python srt_to_timed_audio.py
```

### Production-Grade Open-Source Approach (ChatterboxTTS with TXT processing)
```bash
TTS_METHOD=chatterbox_tts USE_TXT_APPROACH=true python srt_to_timed_audio.py
```

### ChatterboxTTS with Custom Settings
```bash
export TTS_METHOD=chatterbox_tts
export CHATTERBOX_EXAGGERATION=0.7  # More expressive speech
export CHATTERBOX_CFG_WEIGHT=0.3    # Faster pacing
USE_TXT_APPROACH=true python srt_to_timed_audio.py
```

### Language Model Approach (TXT-based with OpenAI TTS)
```bash
export OPENAI_API_KEY=your_key_here
TTS_METHOD=openai_tts USE_TXT_APPROACH=true python srt_to_timed_audio.py
```

### Testing Mode
```bash
USE_MOCK_TTS=true USE_TXT_APPROACH=true python srt_to_timed_audio.py
```

## Technical Implementation

### Whisper Text Output Processing
The alternative approach uses Whisper's `.txt` output files (the most straightforward text format) and processes them by:
1. Splitting text into natural sentences
2. Converting each sentence to audio
3. Concatenating without timing constraints

### Error Handling with Condition Logging
All error conditions are properly assigned to variables and logged:
```python
api_key_available = OPENAI_API_KEY is not None and OPENAI_API_KEY.strip() != ""
if not api_key_available:
    error_condition = "OpenAI API key not available"
    logger.error(f"Error condition: {error_condition}")
```

### Language Model Integration
OpenAI's TTS API provides advanced language model-powered text-to-speech as an alternative to traditional TTS engines.

### ChatterboxTTS Integration
ChatterboxTTS is ResembleAI's production-grade open-source TTS model offering:
- **High-quality voice synthesis** comparable to commercial solutions
- **Voice cloning capabilities** for personalized speech
- **Configurable emotion and expressiveness** via exaggeration parameter
- **Flexible speech pacing** through CFG weight control
- **No API key required** - completely open-source and self-hosted

## Dependencies

Additional dependencies for the enhanced features:
```bash
pip install openai         # For OpenAI TTS language model approach
pip install chatterbox-tts # For ChatterboxTTS production-grade approach
pip install soundfile      # For ChatterboxTTS audio file handling
```

Existing dependencies remain the same:
```bash
pip install srt edge-tts
```