# listening_livekit.py
"""
LiveKit-based voice recognition module for Atlas
Provides real-time speech-to-text using LiveKit API
"""

import os
import time
import threading
import asyncio
from livekit import rtc
from livekit.agents import stt
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveKitListener(threading.Thread):
    """
    LiveKit-based listener for real-time voice recognition
    """
    def __init__(
        self,
        on_recognized_callback,
        on_error_callback=None,
        config_file="materials/livekit_config.txt"
    ):
        super().__init__()
        self._running = True
        self.paused = False
        
        self.on_recognized_callback = on_recognized_callback
        self.on_error_callback = on_error_callback
        
        # Load LiveKit configuration
        self.config = self.load_config(config_file)
        
        # LiveKit connection
        self.room = None
        self.stt_stream = None
        
    def load_config(self, config_file):
        """Load LiveKit configuration from file"""
        config = {}
        try:
            if not os.path.exists(config_file):
                logger.error(f"Config file not found: {config_file}")
                return None
                
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
            
            # Validate required keys
            required_keys = ['API_KEY', 'API_SECRET', 'WS_URL']
            for key in required_keys:
                if key not in config or config[key].startswith('your_'):
                    logger.error(f"Please configure {key} in {config_file}")
                    return None
                    
            logger.info("LiveKit configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return None
    
    def run(self):
        """Main thread loop - runs async event loop"""
        if not self.config:
            logger.error("LiveKit not configured. Falling back to Google Speech Recognition.")
            if self.on_error_callback:
                self.on_error_callback("LiveKit configuration missing")
            return
            
        # Run async loop
        asyncio.run(self.async_listen())
    
    async def async_listen(self):
        """Async listening loop using LiveKit"""
        try:
            logger.info("[LiveKit] Connecting to LiveKit server...")
            
            # Generate access token for connection
            from livekit import api
            token = api.AccessToken(self.config['API_KEY'], self.config['API_SECRET'])
            token.with_identity("atlas-user")
            token.with_name("Atlas Voice Assistant")
            token.with_grants(api.VideoGrants(
                room_join=True,
                room="atlas-room",
                can_publish=True,
                can_subscribe=True
            ))
            
            # Generate JWT token
            jwt_token = token.to_jwt()
            
            # Create room connection
            self.room = rtc.Room()
            
            # Connect to LiveKit server with proper token
            await self.room.connect(
                self.config['WS_URL'],
                jwt_token,
                rtc.RoomOptions(
                    auto_subscribe=True,
                )
            )
            
            logger.info("[LiveKit] Connected successfully!")
            logger.info("[LiveKit] Started listening... (LiveKit Mode)")
            
            # Setup speech-to-text stream
            await self.setup_stt_stream()
            
            # Keep connection alive
            while self._running:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"[LiveKit] Error: {e}")
            if self.on_error_callback:
                self.on_error_callback(f"LiveKit error: {e}")
        finally:
            if self.room:
                await self.room.disconnect()
    
    async def setup_stt_stream(self):
        """Setup speech-to-text streaming"""
        try:
            # Get local audio track
            source = rtc.AudioSource(sample_rate=48000, num_channels=1)
            track = rtc.LocalAudioTrack.create_audio_track("microphone", source)
            
            # Publish track
            options = rtc.TrackPublishOptions()
            publication = await self.room.local_participant.publish_track(track, options)
            
            logger.info("[LiveKit] Microphone track published")
            
            # Listen for transcription events
            @self.room.on("track_subscribed")
            def on_track_subscribed(track, publication, participant):
                logger.info(f"[LiveKit] Track subscribed: {track.kind}")
            
            # Handle transcription results
            @self.room.on("data_received")
            def on_data_received(data, participant):
                try:
                    text = data.decode('utf-8')
                    if text and not self.paused:
                        logger.info(f"[LiveKit] ✓ Recognized: {text}")
                        self.on_recognized_callback(text.lower())
                except Exception as e:
                    logger.error(f"[LiveKit] Error processing data: {e}")
                    
        except Exception as e:
            logger.error(f"[LiveKit] Error setting up STT: {e}")
    
    def stop(self):
        """Stop the listener"""
        self._running = False
        logger.info("[LiveKit] Stopping listening thread...")
    
    def pause_listening(self):
        """Pause listening temporarily"""
        self.paused = True
        logger.info("[LiveKit] Listening paused.")
    
    def resume_listening(self):
        """Resume listening"""
        self.paused = False
        logger.info("[LiveKit] Listening resumed.")


# Test function
if __name__ == "__main__":
    def on_recognized(text):
        print(f"Recognized: {text}")
    
    def on_error(error):
        print(f"Error: {error}")
    
    listener = LiveKitListener(
        on_recognized_callback=on_recognized,
        on_error_callback=on_error
    )
    listener.daemon = True
    listener.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
        print("Stopped")
