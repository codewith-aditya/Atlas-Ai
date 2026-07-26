# listening.py - SMOOTH CONTINUOUS LISTENING

import time
import speech_recognition as sr
import threading

# Use same speech module as main.py
from speech_windows import speak, is_speaking


class Listener(threading.Thread):
    def __init__(
        self,
        on_recognized_callback,
        on_error_callback=None,
        phrase_time_limit=10,
        pause_threshold=0.3
    ):
        super().__init__()
        self._running = True
        self.paused = False

        self.on_recognized_callback = on_recognized_callback
        self.on_error_callback = on_error_callback

        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True  # Auto-adapt to environment
        self.recognizer.dynamic_energy_adjustment_damping = 0.15  # Smooth adjustment
        self.recognizer.dynamic_energy_ratio = 1.5  # Sensitivity (lower = more sensitive)
        self.recognizer.pause_threshold = pause_threshold
        self.phrase_time_limit = phrase_time_limit
        self.lock = threading.Lock()

    def run(self):
        """Main listening loop with proper calibration"""
        print("[Listener] Initializing microphone...")
        
        # Try to find working microphone
        mic = None
        for device_index in [None, 0, 1, 2]:
            try:
                print(f"[Listener] Trying microphone device {device_index}...")
                if device_index is None:
                    mic = sr.Microphone()
                else:
                    mic = sr.Microphone(device_index=device_index)
                
                # Test if it works
                with mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    print(f"[Listener] Microphone {device_index} works!")
                    break
            except Exception as e:
                print(f"[Listener] Device {device_index} failed: {e}")
                mic = None
                continue
        
        if mic is None:
            print("[Listener] No working microphone found!")
            return
        
        # Proper ambient noise calibration (2 seconds)
        try:
            with mic as source:
                print("[Listener] Calibrating for ambient noise (2 seconds)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print(f"[Listener] Calibration done! Energy threshold: {self.recognizer.energy_threshold:.0f}")
        except Exception as e:
            print(f"[Listener] Calibration error: {e}, using defaults")
            self.recognizer.energy_threshold = 300
        
        # Main listening loop
        try:
            with mic as source:
                print("[Listener] Listening for commands...")
                print("=" * 60)
                
                while self._running:
                    # Skip listening while Atlas is speaking
                    if self.paused or is_speaking.is_set():
                        time.sleep(0.05)
                        continue

                    try:
                        # timeout=8: wait up to 8 seconds for speech to START
                        # phrase_time_limit: max duration of a single phrase
                        audio = self.recognizer.listen(
                            source,
                            timeout=8,
                            phrase_time_limit=self.phrase_time_limit
                        )
                        
                        if not self._running:
                            break
                        
                        # Don't process if Atlas started speaking while we were listening
                        if is_speaking.is_set():
                            continue
                        
                        with self.lock:
                            text = self.recognizer.recognize_google(audio)
                            if text.strip():
                                print(f"[Listener] Recognized: {text}")
                                
                                if self.on_recognized_callback:
                                    self.on_recognized_callback(text)
                    
                    except sr.WaitTimeoutError:
                        # No speech detected in 8 seconds - totally normal, just loop
                        continue
                    except sr.UnknownValueError:
                        # Speech detected but couldn't understand - normal
                        continue
                    except sr.RequestError as e:
                        err_msg = f"Speech recognition service error: {e}"
                        print(f"[Listener] {err_msg}")
                        if self.on_error_callback:
                            self.on_error_callback(err_msg)
                        # Don't break - try to recover
                        time.sleep(2)
                        continue

        except Exception as e:
            print(f"[Listener] Fatal error: {e}")
            import traceback
            traceback.print_exc()

    def stop(self):
        self._running = False
        print("[Listener] Stopping listening thread...")

    def pause_listening(self):
        self.paused = True
        print("[Listener] Listening paused.")

    def resume_listening(self):
        self.paused = False
        print("[Listener] Listening resumed.")
