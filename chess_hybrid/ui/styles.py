STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}
QLabel {
    color: #e0e0e0;
    font-size: 12px;
}
QGroupBox {
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    margin-top: 15px;
    font-weight: bold;
    color: #aaaaaa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px;
}
QPushButton {
    background-color: #3e3e3e;
    color: #ffffff;
    border: none;
    padding: 5px 10px;
    border-radius: 3px;
    font-weight: bold;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #4e4e4e;
}
QPushButton:pressed {
    background-color: #2e2e2e;
}
QComboBox {
    background-color: #2e2e2e;
    color: #ffffff;
    border: 1px solid #3e3e3e;
    padding: 3px;
    border-radius: 3px;
    font-size: 12px;
}
QCheckBox {
    color: #e0e0e0;
    font-size: 12px;
}

/* Specific Button Styles */
QPushButton#primaryBtn {
    background-color: #2196F3;
}
QPushButton#primaryBtn:hover {
    background-color: #42A5F5;
}

QPushButton#successBtn {
    background-color: #4CAF50;
}
QPushButton#successBtn:hover {
    background-color: #66BB6A;
}

QPushButton#dangerBtn {
    background-color: #F44336;
}
QPushButton#dangerBtn:hover {
    background-color: #EF5350;
}

QPushButton#warningBtn {
    background-color: #FF9800;
    color: #000000;
}
QPushButton#warningBtn:hover {
    background-color: #FFB74D;
}

QPushButton#infoBtn {
    background-color: #00BCD4;
    color: #000000;
}

/* Tab Widget Styles */
QTabWidget::pane {
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    background-color: #1e1e1e;
}
QTabBar::tab {
    background-color: #2e2e2e;
    color: #aaaaaa;
    padding: 8px 15px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #3e3e3e;
    color: #ffffff;
    font-weight: bold;
}
QTabBar::tab:hover {
    background-color: #3e3e3e;
}

/* Placeholder Label */
QLabel#placeholder {
    color: #555555;
    font-size: 18px;
    font-weight: bold;
}
"""
