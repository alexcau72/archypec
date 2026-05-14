DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #2b2b2b;
    color: #ffffff;
}
QPushButton {
    background-color: #3d3d3d;
    border: 1px solid #555;
    padding: 5px;
    color: white;
}
QPushButton:hover {
    background-color: #505050;
}
QLineEdit, QTextEdit {
    background-color: #3d3d3d;
    color: white;
    border: 1px solid #555;
}
QProgressBar {
    border: 1px solid #555;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #05B8CC;
}
"""

LIGHT_STYLE = """
QMainWindow, QDialog {
    background-color: #f0f0f0;
    color: #000000;
}
QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #ccc;
    padding: 5px;
}
QPushButton:hover {
    background-color: #d0d0d0;
}
QLineEdit, QTextEdit {
    background-color: white;
    border: 1px solid #ccc;
}
"""
