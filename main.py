"""
Main Application Entry Point
Coordinates all components of the Edge-QLM MVP
"""
import sys
import signal
import threading
from pathlib import Path

import config
from src.utils import setup_logger, get_system_info
from src.clipboard_manager import ClipboardManager
from src.audio_recorder import AudioRecorder
from src.background_processor import BackgroundProcessor
from src.ui_simple import SimpleEdgeQLMApp
from filelock import FileLock, Timeout

logger = setup_logger(__name__)


class EdgeQLMApp:
    """Main application class"""
    
    def __init__(self):
        self.clipboard_manager = None
        self.audio_recorder = None
        self.background_processor = None
        self.ui = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
        
    def initialize_components(self):
        """Initialize all application components"""
        try:
            logger.info("Initializing Edge-QLM components...")
            
            # Initialize clipboard manager
            self.clipboard_manager = ClipboardManager()
            logger.info("Clipboard manager initialized")
            
            # Initialize audio recorder
            self.audio_recorder = AudioRecorder()
            logger.info("Audio recorder initialized")
            
            # Initialize background processor
            self.background_processor = BackgroundProcessor(
                self.clipboard_manager, 
                self.audio_recorder
            )
            logger.info("Background processor initialized")
            
            # Initialize UI
            self.ui = SimpleEdgeQLMApp(
                self.clipboard_manager,
                self.audio_recorder,
                config
            )
            logger.info("UI initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
            
    def start_services(self):
        """Start background services"""
        try:
            logger.info("Starting background services...")
            
            # Start clipboard monitoring
            self.clipboard_manager.start_monitoring()
            
            # Start background processing
            self.background_processor.start()
            
            self.running = True
            logger.info("All services started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            raise
            
    def shutdown(self):
        """Shutdown all services gracefully"""
        if not self.running:
            return
            
        try:
            logger.info("Shutting down Edge-QLM...")
            
            # Stop services
            if self.background_processor:
                self.background_processor.stop()
            
            if self.clipboard_manager:
                self.clipboard_manager.stop_monitoring()
            
            if self.audio_recorder:
                self.audio_recorder.cleanup_recording()
            
            self.running = False
            logger.info("Shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            # Release instance lock
            if instance_lock.is_locked:
                instance_lock.release()
            
    def run(self):
        """Run the main application"""
        try:
            # Log system info
            system_info = get_system_info()
            logger.info(f"System info: {system_info}")
            
            # Initialize components
            if not self.initialize_components():
                logger.error("Failed to initialize components")
                return False
            
            # Start background services
            self.start_services()
            
            # Run UI (blocking call)
            logger.info("Starting UI...")
            self.ui.run()
            
            # Shutdown after UI closes
            self.shutdown()
            
            return True
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.shutdown()
            return True
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.shutdown()
            return False


def main():
    """Main entry point"""
    logger.info("Starting Edge-QLM MVP...")
    
    # Print startup banner
    print("╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                                                                                                                                                                                                                                                          ║")
    print("║  ███████╗██████╗  ██████╗ ███████╗      ██████╗ ██╗     ███╗   ███╗                                                                                                                                                                                                                                 ║")
    print("║  ██╔════╝██╔══██╗██╔════╝ ██╔════╝     ██╔═══██╗██║     ████╗ ████║                                                                                                                                                                                                                                 ║")
    print("║  █████╗  ██║  ██║██║  ███╗█████╗       ██║   ██║██║     ██╔████╔██║                                                                                                                                                                                                                                 ║")
    print("║  ██╔══╝  ██║  ██║██║   ██║██╔══╝       ██║▄▄ ██║██║     ██║╚██╔╝██║                                                                                                                                                                                                                                 ║")
    print("║  ███████╗██████╔╝╚██████╔╝███████╗     ╚██████╔╝███████╗██║ ╚═╝ ██║                                                                                                                                                                                                                                 ║")
    print("║  ╚══════╝╚═════╝  ╚═════╝ ╚══════╝      ╚══▀▀═╝ ╚══════╝╚═╝     ╚═╝                                                                                                                                                                                                                                 ║")
    print("║                                                                                                                                                                                                                                                                                                          ║")
    print("║  Productivity Tool for Semiconductor & Software Engineers                                                                                                                                                                                                                                               ║")
    print("║  Version: 0.1.0 MVP                                                                                                                                                                                                                                                                                     ║")
    print("║                                                                                                                                                                                                                                                                                                          ║")
    print("║  Features:                                                                                                                                                                                                                                                                                               ║")
    print("║  • Clipboard History Management                                                                                                                                                                                                                                                                          ║")
    print("║  • Command Generation (qlm CLI)                                                                                                                                                                                                                                                                         ║")
    print("║  • Audio Recording & Transcription                                                                                                                                                                                                                                                                      ║")
    print("║  • Background Processing                                                                                                                                                                                                                                                                                 ║")
    print("║                                                                                                                                                                                                                                                                                                          ║")
    print("║  Usage:                                                                                                                                                                                                                                                                                                  ║")
    print("║  • Run 'python main.py' to start the GUI                                                                                                                                                                                                                                                               ║")
    print("║  • Run 'python -m src.command_generator' for qlm CLI                                                                                                                                                                                                                                                   ║")
    print("║                                                                                                                                                                                                                                                                                                          ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Create and run application
    app = EdgeQLMApp()
    success = app.run()
    
    if success:
        logger.info("Edge-QLM MVP shutdown successfully")
        print("Thank you for using Edge-QLM!")
    else:
        logger.error("Edge-QLM MVP encountered errors")
        print("Edge-QLM encountered errors. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    LOCK_FILE = config.DATA_DIR / "qlm_instance.lock"
    instance_lock = FileLock(str(LOCK_FILE))
    try:
        instance_lock.acquire(timeout=0)
    except Timeout:
        print("Another instance of Edge-QLM is already running. Exiting.")
        sys.exit(0)
    main() 