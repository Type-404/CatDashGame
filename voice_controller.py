import sounddevice as sd
import numpy as np
import threading
import time


class VoiceDetector:
    def __init__(self, threshold=0.05, cooldown=0.3):
        self.threshold = threshold
        self.cooldown = cooldown
        self.jump_triggered = False
        self.is_running = False
        self._thread = None
        self._last_trigger_time = 0

    def audio_callback(self, indata, frames, time_info, status):
        """Callback for the sounddevice InputStream."""
        if not self.is_running:
            return

        if status:
            print(f"VoiceDetector Status: {status}")

        # Calculate RMS (Root Mean Square) volume
        rms = np.sqrt(np.mean(indata ** 2))

        current_time = time.time()
        # Trigger jump if volume > threshold and cooldown has elapsed
        if rms > self.threshold and (current_time - self._last_trigger_time) > self.cooldown:
            self.jump_triggered = True
            self._last_trigger_time = current_time

    def start(self):
        """Starts the voice detector in a background thread."""
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_stream, daemon=True)
        self._thread.start()

    def _run_stream(self):
        # We use a context manager for the InputStream so it closes properly on exit
        try:
            with sd.InputStream(callback=self.audio_callback, channels=1, samplerate=44100):
                while self.is_running:
                    sd.sleep(100)
        except Exception as e:
            print(f"VoiceDetector: Could not open audio stream: {e}")
            self.is_running = False

    def stop(self):
        """Stops the voice detector."""
        self.is_running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    def consume_trigger(self):
        """Returns True if a jump was triggered, and resets the flag."""
        if self.jump_triggered:
            self.jump_triggered = False
            return True
        return False