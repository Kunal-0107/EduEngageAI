import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import cv2
from PIL import Image, ImageTk
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os

# --- SAFE IMPORT SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Try Loading Visual Brain
try:
    from models.engagement_model import EngagementAnalyzer
    print("✅ Visual Model Loaded.")
except Exception as e:
    print(f"⚠️ VISUAL MODEL FAILED: {e}")
    class EngagementAnalyzer:
        def analyze_frame(self, f): return f, 0.5

# Try Loading Audio Brain
AUDIO_ENABLED = False
try:
    from models.audio_model import AudioAnalyzer
    print("✅ Audio Model Loaded.")
    AUDIO_ENABLED = True
except Exception as e:
    print(f"⚠️ AUDIO MODEL FAILED: {e}")
    # Dummy class to prevent crash
    class AudioAnalyzer:
        def analyze_live_chunk(self, d): return 0
        def analyze_video_file(self, f): return None

class EduEngageApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("EduEngage AI: Master's Level Analytics")
        self.geometry("1280x900")
        
        self.visual_analyzer = EngagementAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        
        self.is_running = False
        self.history = [] 
        self.audio_history = [] 
        self.source = 0   
        
        self.create_widgets()

    def create_widgets(self):
        # Sidebar
        sidebar = ttk.Frame(self, bootstyle="secondary", padding=15)
        sidebar.pack(side=LEFT, fill=Y)
        
        ttk.Label(sidebar, text="EduEngage AI", font=("Segoe UI", 22, "bold"), bootstyle="inverse-secondary").pack(pady=20)
        ttk.Label(sidebar, text="Advanced Analytics", font=("Segoe UI", 10), bootstyle="inverse-secondary").pack(pady=(0, 20))
        
        ttk.Label(sidebar, text="Input Source", font=("Segoe UI", 12), bootstyle="inverse-secondary").pack(pady=(10,5))
        ttk.Button(sidebar, text="🔴 Start Live Camera", command=self.start_live, bootstyle="danger").pack(fill=X, pady=5)
        ttk.Button(sidebar, text="📂 Upload Video File", command=self.upload_video, bootstyle="info").pack(fill=X, pady=5)
        
        ttk.Separator(sidebar).pack(fill=X, pady=20)
        
        ttk.Button(sidebar, text="⏹ Stop & Generate Report", command=self.stop_analysis, bootstyle="warning").pack(fill=X, pady=10)
        
        self.lbl_score = ttk.Label(sidebar, text="Visual Score: --", font=("Segoe UI", 14), bootstyle="inverse-secondary")
        self.lbl_score.pack(pady=20)
        self.lbl_audio = ttk.Label(sidebar, text="Audio Level: --", font=("Segoe UI", 14), bootstyle="inverse-secondary")
        self.lbl_audio.pack(pady=5)
        self.lbl_status = ttk.Label(sidebar, text="Status: Idle", bootstyle="secondary")
        self.lbl_status.pack(side=BOTTOM, pady=10)

        # Main Area
        content = ttk.Frame(self, padding=10)
        content.pack(side=RIGHT, fill=BOTH, expand=True)
        
        self.video_frame = ttk.Frame(content, border=2, relief="sunken")
        self.video_frame.pack(pady=10)
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()
        
        self.fig, self.ax = plt.subplots(figsize=(8, 2.5), dpi=100)
        self.ax.set_title("Engagement Velocity (Real-time)")
        self.ax.set_ylim(0, 1)
        self.line, = self.ax.plot([], [], 'c-', linewidth=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=content)
        self.canvas.get_tk_widget().pack(fill=X, pady=10)

    def start_live(self):
        self.source = 0 
        self.start_processing("Live Mode: Camera Active")

    def upload_video(self):
        filename = filedialog.askopenfilename(title="Select Teaching Video", filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if filename:
            self.source = filename
            self.start_processing(f"File Analysis Mode")

    def start_processing(self, status_text):
        if self.is_running: return
        self.is_running = True
        self.history = [] 
        self.audio_history = []
        self.lbl_status.config(text=status_text)
        
        threading.Thread(target=self.process_video, daemon=True).start()
        
        if AUDIO_ENABLED and isinstance(self.source, int):
             threading.Thread(target=self.process_live_audio, daemon=True).start()

    def stop_analysis(self):
        self.is_running = False
        self.lbl_status.config(text="Stopping... Computing Analytics...")

    def process_live_audio(self):
        import sounddevice as sd
        def callback(indata, frames, time, status):
            if self.is_running:
                vol = self.audio_analyzer.analyze_live_chunk(indata)
                self.audio_history.append(vol)
                self.after(100, lambda: self.lbl_audio.config(text=f"Audio Level: {vol}"))
        try:
            with sd.InputStream(device=1, callback=callback): # FORCE DEVICE 1
                while self.is_running: sd.sleep(100)
        except:
            with sd.InputStream(callback=callback):
                while self.is_running: sd.sleep(100)

    def process_video(self):
        if isinstance(self.source, int):
            print(f"Opening Camera {self.source}...")
            cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
            if not cap.isOpened(): cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        else:
            print(f"Opening File: {self.source}")
            cap = cv2.VideoCapture(self.source)

        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open video source.")
            self.is_running = False
            return
        
        file_audio_stats = None
        if AUDIO_ENABLED and not isinstance(self.source, int):
            self.lbl_status.config(text="Analyzing Audio Track... (Please Wait)")
            file_audio_stats = self.audio_analyzer.analyze_video_file(self.source)
            self.lbl_status.config(text="Audio Analyzed. Playing Video...")

        while self.is_running and cap.isOpened():
            ret, frame = cap.read()
            if not ret: break 
            
            frame, score = self.visual_analyzer.analyze_frame(frame)
            self.history.append(score)
            
            frame = cv2.resize(frame, (640, 360))
            img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            try:
                self.video_label.configure(image=img)
                self.video_label.image = img
            except: pass
            
            self.lbl_score.config(text=f"Visual Score: {score:.2f}")
            self.update_graph()
            
        cap.release()
        self.is_running = False
        self.generate_advanced_report(file_audio_stats)

    def update_graph(self):
        data = self.history[-100:]
        self.line.set_data(range(len(data)), data)
        self.ax.set_xlim(0, 100)
        self.canvas.draw()

    # --- NEW: MASTER'S LEVEL REPORT GENERATOR ---
    def generate_advanced_report(self, file_audio_stats):
        if not self.history: return
        
        # --- 1. CALCULATE DEEP METRICS ---
        avg_score = np.mean(self.history)
        std_dev = np.std(self.history)
        max_score = np.max(self.history)
        
        # Trend Analysis (First half vs Second half)
        mid = len(self.history) // 2
        first_half = np.mean(self.history[:mid])
        second_half = np.mean(self.history[mid:])
        trend = second_half - first_half
        
        # Distraction Analysis
        distracted_frames = sum(1 for x in self.history if x < 0.4)
        distracted_pct = (distracted_frames / len(self.history)) * 100
        
        # --- 2. BUILD THE TEXT REPORT ---
        report = []
        report.append("📊 TEACHING PERFORMANCE ANALYTICS")
        report.append("="*50)
        
        # A. HEADLINE GRADE
        if avg_score > 0.85:
            report.append(f"🏆 OVERALL GRADE: A ({avg_score:.2f})")
            report.append("Summary: Excellent teaching presence. Highly engaging.")
        elif avg_score > 0.65:
            report.append(f"✅ OVERALL GRADE: B ({avg_score:.2f})")
            report.append("Summary: Good performance, but some lapses in engagement.")
        else:
            report.append(f"⚠️ OVERALL GRADE: C ({avg_score:.2f})")
            report.append("Summary: Engagement levels were critically low.")

        # B. VISUAL DYNAMICS
        report.append("\n👁️ VISUAL DYNAMICS")
        report.append("-" * 30)
        
        # Consistency Check
        if std_dev < 0.1:
            report.append("• Stability: [HIGH] - Very calm and professional.")
        elif std_dev < 0.25:
            report.append("• Stability: [MODERATE] - Normal movement levels.")
        else:
            report.append("• Stability: [LOW] - High jitter/fidgeting detected.")

        # Fatigue/Trend Check
        if trend < -0.15:
            report.append("• Energy Trend: [DECLINING] 📉")
            report.append("  Analysis: You started strong but lost energy in the second half.")
        elif trend > 0.1:
            report.append("• Energy Trend: [IMPROVING] 📈")
            report.append("  Analysis: You became more engaging as the session went on.")
        else:
            report.append("• Energy Trend: [STABLE] ➡️")
            report.append("  Analysis: You maintained consistent energy.")

        # Eye Contact Check
        if distracted_pct < 10:
             report.append(f"• Eye Contact: [EXCELLENT] - Looked away only {distracted_pct:.1f}% of time.")
        elif distracted_pct < 30:
             report.append(f"• Eye Contact: [GOOD] - Looked away {distracted_pct:.1f}% of time.")
        else:
             report.append(f"• Eye Contact: [POOR] - Looked away {distracted_pct:.1f}% of time.")

        # C. VOCAL ANALYTICS
        report.append("\n🎤 VOCAL ANALYTICS")
        report.append("-" * 30)
        
        if file_audio_stats:
            if file_audio_stats['is_monotone']:
                report.append("• Intonation: MONOTONE (Robot-like). Try varying pitch.")
            else:
                report.append("• Intonation: DYNAMIC (Good variance).")
        elif self.audio_history:
            avg_vol = np.mean(self.audio_history)
            if avg_vol < 10: 
                report.append("• Volume: TOO QUIET. Move closer to the microphone.")
            elif avg_vol > 90:
                report.append("• Volume: TOO LOUD (Peaking). Move back slightly.")
            else:
                report.append("• Volume: OPTIMAL levels.")
        else:
            report.append("• Status: Audio Analysis Disabled/Unavailable.")

        # D. SPECIFIC RECOMMENDATIONS
        report.append("\n🤖 AI COACH RECOMMENDATIONS")
        report.append("-" * 30)
        tips = []
        if distracted_pct > 20: tips.append("1. Maintain eye contact with the camera lens, not the screen.")
        if trend < -0.1: tips.append("2. Keep your energy up! Take breaks if recording long sessions.")
        if std_dev > 0.2: tips.append("3. Reduce chair swiveling or excessive hand movement.")
        if not tips: tips.append("• No major corrections needed. Keep doing what you're doing!")
        
        for tip in tips:
            report.append(tip)

        final_text = "\n".join(report)
        messagebox.showinfo("Detailed Analytics", final_text)
        self.lbl_status.config(text="Report Generated.")

if __name__ == "__main__":
    app = EduEngageApp()
    app.mainloop()