import numpy as np
import sounddevice as sd
from moviepy.editor import VideoFileClip

class AudioAnalyzer:
    def __init__(self):
        self.volume_history = []
        self.samplerate = 44100

    def analyze_live_chunk(self, indata):
        """Calculates volume (RMS) from live microphone data"""
        # 1. Calculate Root Mean Square (Standard volume metric)
        rms = np.sqrt(np.mean(indata**2))
        
        # 2. HYPER BOOST 
        # RMS is usually tiny (e.g., 0.0002). 
        # We multiply by 50,000 to get numbers between 10 and 100.
        level = int(rms * 50000) 
        
        # Cap it at 100 so it doesn't break the UI
        return min(level, 100)

    def analyze_video_file(self, filename):
        """Extracts audio from video file"""
        try:
            clip = VideoFileClip(filename)
            duration = min(clip.duration, 60) 
            audio = clip.audio.subclip(0, duration)
            audio_array = audio.to_soundarray(fps=22000)
            
            if audio_array.ndim > 1:
                magnitudes = np.abs(audio_array[:, 0]) 
            else:
                magnitudes = np.abs(audio_array)

            avg_volume = np.mean(magnitudes)
            dynamic_range = np.std(magnitudes)
            
            silence_threshold = avg_volume * 0.2
            silent_frames = np.sum(magnitudes < silence_threshold)
            silence_ratio = silent_frames / len(magnitudes)
            
            clip.close()
            return {
                "avg_volume": avg_volume,
                "is_monotone": dynamic_range < 0.02, 
                "silence_ratio": silence_ratio
            }
        except Exception as e:
            print(f"Audio Error: {e}")
            return None