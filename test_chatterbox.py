#!/usr/bin/env python3
"""
Simple test script to verify ChatterboxTTS integration works properly.
This tests the three TTS methods: Edge TTS, OpenAI TTS, and ChatterboxTTS.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add current directory to path to import the main module
sys.path.insert(0, '.')

from srt_to_timed_audio import generate_audio, logger

async def test_tts_methods():
    """Test all three TTS methods"""
    
    # Create test output directory
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    test_text = "Hello world, this is a test of the text-to-speech system."
    
    # Test 1: Edge TTS (default)
    logger.info("=== Testing Edge TTS (traditional approach) ===")
    os.environ["TTS_METHOD"] = "edge_tts"
    os.environ["USE_MOCK_TTS"] = "true"  # Use mock mode for testing
    try:
        await generate_audio(test_text, str(test_dir / "test_edge.mp3"))
        logger.info("✅ Edge TTS test passed")
    except Exception as e:
        logger.error(f"❌ Edge TTS test failed: {e}")
    
    # Test 2: OpenAI TTS (language model approach)
    logger.info("=== Testing OpenAI TTS (language model approach) ===")
    os.environ["TTS_METHOD"] = "openai_tts"
    os.environ["USE_MOCK_TTS"] = "true"  # Use mock mode for testing
    try:
        await generate_audio(test_text, str(test_dir / "test_openai.mp3"))
        logger.info("✅ OpenAI TTS test passed")
    except Exception as e:
        logger.error(f"❌ OpenAI TTS test failed: {e}")
    
    # Test 3: ChatterboxTTS (production-grade open-source approach)
    logger.info("=== Testing ChatterboxTTS (production-grade open-source approach) ===")
    os.environ["TTS_METHOD"] = "chatterbox_tts"
    os.environ["USE_MOCK_TTS"] = "true"  # Use mock mode for testing
    try:
        await generate_audio(test_text, str(test_dir / "test_chatterbox.mp3"))
        logger.info("✅ ChatterboxTTS test passed")
    except Exception as e:
        logger.error(f"❌ ChatterboxTTS test failed: {e}")
    
    # Test 4: ChatterboxTTS without mock (to test actual library detection)
    logger.info("=== Testing ChatterboxTTS library detection ===")
    os.environ["USE_MOCK_TTS"] = "false"
    try:
        await generate_audio(test_text, str(test_dir / "test_chatterbox_real.mp3"))
        logger.info("✅ ChatterboxTTS library detection test passed")
    except Exception as e:
        logger.error(f"❌ ChatterboxTTS library detection test failed (expected): {e}")
    
    logger.info("=== TTS Integration Tests Complete ===")
    
    # Check output files
    for test_file in test_dir.glob("*.mp3"):
        size = test_file.stat().st_size
        logger.info(f"Generated test file: {test_file.name} ({size} bytes)")

if __name__ == "__main__":
    asyncio.run(test_tts_methods())