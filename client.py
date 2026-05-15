import sys
import socketio
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal, QObject

class SocketSignals(QObject):
    update_received = pyqtSignal(str)

class CollaborativeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCollab Edit")
        self.setGeometry(100, 100, 800, 600)

        # Networking
        self.sio = socketio.Client()
        self.signals = SocketSignals()
        self.doc_id = "default_room"
        
        # UI Setup
        self.init_ui()
        self.setup_sockets()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Disconnected")
        layout.addWidget(self.status_label)

        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Start typing...")
        self.text_editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_editor)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def setup_sockets(self):
        self.signals.update_received.connect(self.apply_update)

        @self.sio.on('connect')
        def on_connect():
            self.status_label.setText(f"Connected to Room: {self.doc_id}")
            self.sio.emit('join_doc', self.doc_id)

        @self.sio.on('update_text')
        def on_update_text(data):
            self.signals.update_received.emit(data)

        try:
            self.sio.connect('http://localhost:5000')
        except:
            self.status_label.setText("Connection Failed")

    def on_text_changed(self):
        # Prevent circular updates: only send if the user is the one typing
        if self.text_editor.hasFocus():
            content = self.text_editor.toPlainText()
            self.sio.emit('edit_text', {'doc_id': self.doc_id, 'content': content})

    def apply_update(self, content):
        # Block signals so setting text doesn't trigger 'on_text_changed' again
        self.text_editor.blockSignals(True)
        cursor_pos = self.text_editor.textCursor().position()
        self.text_editor.setPlainText(content)
        
        # Restore cursor position
        cursor = self.text_editor.textCursor()
        cursor.setPosition(min(cursor_pos, len(content)))
        self.text_editor.setTextCursor(cursor)
        
        self.text_editor.blockSignals(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CollaborativeEditor()
    window.show()
    sys.exit(app.exec())