import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                             QVBoxLayout, QWidget, QProgressBar, QLabel, QHBoxLayout,
                             QSlider, QStyle, QFrame)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QUrl, QTimer
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from engine import SupertonicEngine

class GenerationThread(QThread):
    finished = pyqtSignal(str) # output_file
    error = pyqtSignal(str)

    def __init__(self, engine, text, speed, output_file):
        super().__init__()
        self.engine = engine
        self.text = text
        self.speed = speed
        self.output_file = output_file

    def run(self):
        try:
            output_file = self.engine.generate_audio(self.text, output_file=self.output_file, speed=self.speed)
            self.finished.emit(output_file)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supertonic Text Reader")
        self.resize(900, 700)
        self.setup_dark_theme()

        # Layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title_label = QLabel("Supertonic Reader")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(title_label)

        # Text Input
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter text here...")
        self.text_edit.setText("## Welcome to Supertonic\n\nThis is a demonstration of the **lightning fast** text to speech engine.\n\nIt runs locally on your device.")
        self.text_edit.setFont(QFont("Consolas", 12))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout.addWidget(self.text_edit)

        # Controls Container
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        controls_layout = QVBoxLayout(controls_frame)
        layout.addWidget(controls_frame)

        # Speed Control
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        speed_label.setStyleSheet("color: #aaaaaa; font-weight: bold;")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200) # 0.5x to 2.0x
        self.speed_slider.setValue(160) # Default 1.5x
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_value_label = QLabel("1.6x")
        self.speed_value_label.setStyleSheet("color: #ffffff; min-width: 40px;")
        self.speed_slider.valueChanged.connect(self.update_speed_label)
        
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_value_label)
        controls_layout.addLayout(speed_layout)

        # Playback Buttons
        buttons_layout = QHBoxLayout()
        
        self.read_button = QPushButton(" Generate & Play")
        self.read_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.read_button.clicked.connect(self.start_reading)
        self.read_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1084d9; }
            QPushButton:disabled { background-color: #444444; color: #888888; }
        """)
        
        self.pause_button = QPushButton(" Pause")
        self.pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setEnabled(False)
        self.pause_button.setStyleSheet(self.read_button.styleSheet().replace("#0078d4", "#444444"))

        self.stop_button = QPushButton(" Stop")
        self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.clicked.connect(self.stop_reading)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(self.read_button.styleSheet().replace("#0078d4", "#d13438"))

        buttons_layout.addWidget(self.read_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.stop_button)
        controls_layout.addLayout(buttons_layout)

        # Clipboard Toggle
        self.clipboard_toggle = QPushButton(" Auto-Read Clipboard: OFF")
        self.clipboard_toggle.setCheckable(True)
        self.clipboard_toggle.clicked.connect(self.toggle_clipboard_mode)
        self.clipboard_toggle.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #aaaaaa;
                border: 1px solid #555555;
                padding: 8px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
                border: 1px solid #0078d4;
            }
        """)
        # Enable by default (set checked but don't call handler yet)
        self.clipboard_toggle.setChecked(True)
        
        controls_layout.addWidget(self.clipboard_toggle)

        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #888888; margin-top: 10px;")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #3d3d3d;
                height: 4px;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Engine
        try:
            self.engine = SupertonicEngine()
        except Exception as e:
            self.status_label.setText(f"Error initializing engine: {e}")
            self.read_button.setEnabled(False)
            
        # Audio Player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.player.errorOccurred.connect(self.on_player_error)

        # Clipboard
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)
        self.last_clipboard_text = ""
        self.clipboard_debounce_timer = QTimer()
        self.clipboard_debounce_timer.setSingleShot(True)
        self.clipboard_debounce_timer.setInterval(500) # 500ms debounce
        self.clipboard_debounce_timer.timeout.connect(self.process_clipboard_text)
        
        # Initialize Clipboard Mode (now that everything is ready)
        self.toggle_clipboard_mode(True)

    def setup_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(32, 32, 32))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        QApplication.setPalette(palette)

    def toggle_clipboard_mode(self, checked):
        if checked:
            self.clipboard_toggle.setText(" Auto-Read Clipboard: ON")
            self.status_label.setText("Clipboard monitoring enabled")
            self.last_clipboard_text = self.clipboard.text()
        else:
            self.clipboard_toggle.setText(" Auto-Read Clipboard: OFF")
            self.status_label.setText("Clipboard monitoring disabled")

    def on_clipboard_changed(self):
        if not self.clipboard_toggle.isChecked():
            return
        # Restart debounce timer
        self.clipboard_debounce_timer.start()

    def process_clipboard_text(self):
        text = self.clipboard.text()
        if text and text != self.last_clipboard_text:
            print("Clipboard change detected and processed.")
            self.last_clipboard_text = text
            self.text_edit.setText(text)
            self.status_label.setText("Clipboard detected! Reading...")
            
            # Stop any current playback
            if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.player.stop()
            
            # Start reading
            self.start_reading()

    def update_speed_label(self, value):
        speed = value / 100.0
        self.speed_value_label.setText(f"{speed:.1f}x")

    def start_reading(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            return

        self.read_button.setEnabled(False)
        self.status_label.setText("Generating audio...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) # Indeterminate

        speed = self.speed_slider.value() / 100.0
        
        # Unique filename to prevent locking/caching issues
        import time
        filename = f"output_{int(time.time() * 1000)}.wav"
        
        # Pass filename to thread (we need to update GenerationThread to accept it)
        self.thread = GenerationThread(self.engine, text, speed, filename)
        self.thread.finished.connect(self.on_generation_finished)
        self.thread.error.connect(self.on_generation_error)
        self.thread.start()

    def on_generation_finished(self, output_file):
        self.progress_bar.setVisible(False)
        self.status_label.setText("Playing...")
        self.stop_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        
        # Play audio
        full_path = os.path.abspath(output_file)
        print(f"Playing file: {full_path}")
        self.player.setSource(QUrl.fromLocalFile(full_path))
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)
        self.player.play()

    def on_generation_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.read_button.setEnabled(True)
        self.status_label.setText(f"Error: {error_msg}")

    def toggle_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.pause_button.setText(" Resume")
            self.pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.player.play()
            self.pause_button.setText(" Pause")
            self.pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def stop_reading(self):
        self.player.stop()
        self.reset_ui_state()

    def on_media_status_changed(self, status):
        print(f"Media Status Changed: {status}")
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.reset_ui_state()
            self.status_label.setText("Finished")
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            self.status_label.setText("Error: Invalid Media")

    def on_player_error(self):
        print(f"Player Error: {self.player.errorString()}")
        self.status_label.setText(f"Player Error: {self.player.errorString()}")
        self.reset_ui_state()

    def reset_ui_state(self):
        self.read_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.pause_button.setText(" Pause")
        self.pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.status_label.setText("Ready")

    def cleanup_temp_files(self):
        import glob
        for f in glob.glob("output_*.wav"):
            try:
                os.remove(f)
                print(f"Cleaned up {f}")
            except Exception as e:
                print(f"Failed to delete {f}: {e}")

    def closeEvent(self, event):
        self.cleanup_temp_files()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # Clean up old files on startup
    window.cleanup_temp_files()
    window.show()
    app.exec()
