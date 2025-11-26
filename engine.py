import sys
import os
import soundfile as sf
import numpy as np

# Add Supertonic to path
SUPERTONIC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "supertonic", "py"))
if SUPERTONIC_PATH not in sys.path:
    sys.path.append(SUPERTONIC_PATH)

from helper import load_text_to_speech, load_voice_style

class SupertonicEngine:
    def __init__(self, 
                 onnx_dir="./supertonic/assets/onnx", 
                 voice_style_path="./supertonic/assets/voice_styles/M1.json",
                 use_gpu=False):
        
        print("Initializing Supertonic Engine...")
        self.tts = load_text_to_speech(onnx_dir, use_gpu)
        self.style = load_voice_style([voice_style_path])
        self.sample_rate = self.tts.sample_rate
        
    def generate_audio(self, text: str, output_file="output.wav", steps=5, speed=1.5):
        """Generates audio from text using Supertonic."""
        print(f"Generating audio for: {text[:50]}... (Speed: {speed})")
        
        # Supertonic inference
        # text_to_speech call returns (wav, duration)
        wav, duration = self.tts(text, self.style, steps, speed)
        
        # Save to file
        # wav is float32, usually -1 to 1
        audio_data = wav[0]
        sf.write(output_file, audio_data, self.sample_rate)
        
        return output_file
