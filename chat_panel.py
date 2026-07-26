# chat_panel.py
"""
Interactive Chat Panel for Atlas GUI
Allows users to type commands and see responses in a modern chat interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QColor
from datetime import datetime


class ChatPanel(QWidget):
    """Modern chat panel for text-based interaction with Atlas"""
    
    # Signal to send user messages to main worker
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the chat panel UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("ATLAS CHAT")
        header.setFont(QFont("Orbitron", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                color: #00FFCC;
                background-color: rgba(0, 0, 0, 0.5);
                border: 2px solid #00FFCC;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Roboto", 11))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                border: 2px solid rgba(0, 255, 204, 0.3);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_display, stretch=1)
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your command...")
        self.input_box.setFont(QFont("Roboto", 12))
        self.input_box.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                border: 2px solid #00FFCC;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00FFFF;
                background-color: rgba(0, 0, 0, 0.9);
            }
        """)
        self.input_box.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_box)
        
        # Send button
        self.send_button = QPushButton("SEND")
        self.send_button.setFont(QFont("Orbitron", 11, QFont.Bold))
        self.send_button.setFixedSize(80, 45)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFCC,
                    stop:1 #00FFFF
                );
                color: #000000;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFFF,
                    stop:1 #00FFCC
                );
            }
            QPushButton:pressed {
                background: #00bebe;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Clear button
        clear_button = QPushButton("Clear Chat")
        clear_button.setFont(QFont("Roboto", 10))
        clear_button.setFixedHeight(30)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 107, 53, 0.3);
                color: #FF6B35;
                border: 1px solid #FF6B35;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 107, 53, 0.5);
            }
        """)
        clear_button.clicked.connect(self.clear_chat)
        layout.addWidget(clear_button)
        
        self.setLayout(layout)
        
        # Add welcome message
        self.add_atlas_message("Hello! I'm Atlas. Type your commands here or use voice! 🤖")
        
    def send_message(self):
        """Send user message"""
        message = self.input_box.text().strip()
        if not message:
            return
            
        # Add user message to chat
        self.add_user_message(message)
        
        # Clear input
        self.input_box.clear()
        
        # Emit signal to main worker
        self.message_sent.emit(message)
        
    def add_user_message(self, message):
        """Add user message matching Atlas style"""
        timestamp = datetime.now().strftime("%H:%M")
        message = message.replace('<', '&lt;').replace('>', '&gt;')
        
        html = f"""
        <div style='text-align: right; margin: 12px 0;'>
            <div style='display: inline-block; max-width: 70%;'>
                <div style='font-size: 9px; color: #888; margin-bottom: 3px; text-align: right;'>
                    {timestamp}
                </div>
                <div style='
                    background-color: rgba(255, 141, 0, 0.15);
                    border: 2px solid #FF8D00;
                    border-radius: 12px;
                    padding: 10px 14px;
                    text-align: left;
                '>
                    <div style='color: #FF8D00; font-size: 11px; font-weight: bold; margin-bottom: 3px;'>
                        You
                    </div>
                    <div style='color: #FFFFFF; font-size: 12px; line-height: 1.4;'>
                        {message}
                    </div>
                </div>
            </div>
        </div>
        """
        
        self.chat_display.append(html)
        self.scroll_to_bottom()
        
    def add_atlas_message(self, message, status="done"):
        """Add Atlas response matching Atlas style"""
        timestamp = datetime.now().strftime("%H:%M")
        message = message.replace('<', '&lt;').replace('>', '&gt;')
        
        # Status colors
        if status == "done":
            status_icon = "✓"
            status_color = "#00FF88"
        elif status == "processing":
            status_icon = "⏳"
            status_color = "#FFA500"
        else:
            status_icon = "❌"
            status_color = "#FF6B35"
        
        html = f"""
        <div style='text-align: left; margin: 12px 0;'>
            <div style='display: inline-block; max-width: 70%;'>
                <div style='font-size: 9px; color: #888; margin-bottom: 3px;'>
                    {timestamp}
                </div>
                <div style='
                    background-color: rgba(0, 255, 204, 0.15);
                    border: 2px solid #00FFCC;
                    border-radius: 12px;
                    padding: 10px 14px;
                    text-align: left;
                '>
                    <div style='margin-bottom: 3px;'>
                        <span style='color: #00FFCC; font-size: 11px; font-weight: bold;'>
                            Atlas
                        </span>
                        <span style='color: {status_color}; font-size: 13px; margin-left: 5px;'>
                            {status_icon}
                        </span>
                    </div>
                    <div style='color: #FFFFFF; font-size: 12px; line-height: 1.4;'>
                        {message}
                    </div>
                </div>
            </div>
        </div>
        """
        
        self.chat_display.append(html)
        self.scroll_to_bottom()
        
    def add_task_status(self, task, status):
        """Add task status matching Atlas style"""
        task = task.replace('<', '&lt;').replace('>', '&gt;')
        
        if status == "done":
            status_text = "✓ Done"
            color = "#00FF88"
        elif status == "processing":
            status_text = "⏳ Processing"
            color = "#FFA500"
        else:
            status_text = "❌ Failed"
            color = "#FF6B35"
        
        html = f"""
        <div style='text-align: center; margin: 8px 0;'>
            <div style='
                display: inline-block;
                background-color: rgba(0, 0, 0, 0.6);
                border: 1px solid {color};
                border-radius: 15px;
                padding: 6px 12px;
            '>
                <span style='color: {color}; font-size: 11px; font-weight: bold;'>
                    {task} - {status_text}
                </span>
            </div>
        </div>
        """
        
        self.chat_display.append(html)
        self.scroll_to_bottom()
        
    def scroll_to_bottom(self):
        """Auto-scroll to bottom of chat"""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.clear()
        self.add_atlas_message("Chat cleared! Ready for new commands. 🚀")


if __name__ == "__main__":
    # Test the chat panel
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    chat = ChatPanel()
    chat.setWindowTitle("Atlas Chat Panel Test")
    chat.resize(400, 600)
    chat.setStyleSheet("background-color: #0A0E27;")
    chat.show()
    
    # Test messages
    QTimer.singleShot(1000, lambda: chat.add_user_message("Open YouTube"))
    QTimer.singleShot(1500, lambda: chat.add_atlas_message("Opening YouTube...", "processing"))
    QTimer.singleShot(2000, lambda: chat.add_task_status("Open YouTube", "done"))
    QTimer.singleShot(2100, lambda: chat.add_atlas_message("YouTube opened successfully!", "done"))
    
    sys.exit(app.exec_())
