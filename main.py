# ~/projects/contenta/main.py

from PyQt6.QtWidgets import QApplication

from editor.editor_window import EditorWindow

import sys

def main():
    # Create the application
    app = QApplication(sys.argv)

    # Create and show the text editor
    editor = EditorWindow()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
