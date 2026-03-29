import sys
import re
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QTextEdit, QProgressBar, QCheckBox
)
from PyQt5.QtGui import QFont


# -------------------------------
# Logic Functions
# -------------------------------
def check_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search("[A-Z]", password):
        score += 1
    if re.search("[0-9]", password):
        score += 1
    if re.search("[@#$%^&+=]", password):
        score += 1
    return score


def strength_feedback(score):
    if score == 0:
        return "Very Weak ❌"
    elif score == 1:
        return "Weak ❌"
    elif score == 2:
        return "Moderate ⚠️"
    elif score == 3:
        return "Strong 👍"
    else:
        return "Very Strong 🔥"


def estimate_crack_time(password):
    guesses_per_sec = 1_000_000
    possible_chars = 26

    if re.search("[A-Z]", password):
        possible_chars += 26
    if re.search("[0-9]", password):
        possible_chars += 10
    if re.search("[@#$%^&+=]", password):
        possible_chars += 10

    combinations = possible_chars ** len(password)
    seconds = combinations / guesses_per_sec
    return round(seconds / 60, 2)


def suggestions(password):
    tips = []
    if len(password) < 8:
        tips.append("Use at least 8 characters")
    if not re.search("[A-Z]", password):
        tips.append("Add uppercase letters")
    if not re.search("[0-9]", password):
        tips.append("Include numbers")
    if not re.search("[@#$%^&+=]", password):
        tips.append("Use special characters")
    return tips


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def crack_password(hash_value):
    try:
        with open("wordlist.txt", "r") as file:
            for word in file:
                word = word.strip()
                if hash_password(word) == hash_value:
                    return word
    except FileNotFoundError:
        return "Wordlist file missing"
    return None


# -------------------------------
# PyQt App
# -------------------------------
class PasswordApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🔐 Password Analyzer Pro")
        self.setGeometry(200, 200, 450, 550)

        layout = QVBoxLayout()

        title = QLabel("🔐 Password Security Analyzer")
        title.setFont(QFont("Arial", 16))
        layout.addWidget(title)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter your password...")
        self.input.setEchoMode(QLineEdit.Password)
        self.input.textChanged.connect(self.live_update)  # LIVE UPDATE
        layout.addWidget(self.input)

        # 👁️ Show Password Toggle
        self.show_checkbox = QCheckBox("Show Password")
        self.show_checkbox.stateChanged.connect(self.toggle_password)
        layout.addWidget(self.show_checkbox)

        self.progress = QProgressBar()
        self.progress.setMaximum(4)
        layout.addWidget(self.progress)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.button = QPushButton("Analyze Password")
        self.button.clicked.connect(self.analyze_password)
        layout.addWidget(self.button)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

        # 🎨 DARK THEME
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: #e2e8f0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #22c55e;
                color: black;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QTextEdit {
                background-color: #1e293b;
                border-radius: 6px;
                padding: 8px;
            }
            QProgressBar {
                background-color: #1e293b;
                border-radius: 5px;
                text-align: center;
            }
        """)

    # 👁️ Toggle Password Visibility
    def toggle_password(self):
        if self.show_checkbox.isChecked():
            self.input.setEchoMode(QLineEdit.Normal)
        else:
            self.input.setEchoMode(QLineEdit.Password)

    # ⚡ Live Strength Update
    def live_update(self):
        password = self.input.text()
        if not password:
            self.progress.setValue(0)
            self.result_label.setText("")
            return

        score = check_strength(password)
        self.progress.setValue(score)

        colors = ["#ef4444", "#f97316", "#facc15", "#22c55e"]
        color = colors[score-1] if score > 0 else "#ef4444"

        self.progress.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)

        self.result_label.setText(f"Strength: {strength_feedback(score)}")

    # 🔍 Full Analysis Button
    def analyze_password(self):
        password = self.input.text()

        if not password:
            self.output.setText("⚠️ Please enter a password")
            return

        result_text = ""

        time = estimate_crack_time(password)
        result_text += f"⏱ Estimated crack time: {time} minutes\n\n"

        tips = suggestions(password)
        if tips:
            result_text += "💡 Suggestions:\n"
            for tip in tips:
                result_text += f"- {tip}\n"
            result_text += "\n"

        hashed = hash_password(password)
        cracked = crack_password(hashed)

        if cracked == "Wordlist file missing":
            result_text += "⚠️ wordlist.txt not found\n"
        elif cracked:
            result_text += f"🚨 Password cracked using dictionary attack: {cracked}\n"
        else:
            score = check_strength(password)
            if score <= 1:
                result_text += "🚨 Weak password — easily guessable\n"
            else:
                result_text += "🟢 Not found in common password list (may still be vulnerable)\n"

        self.output.setText(result_text)


# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordApp()
    window.show()
    sys.exit(app.exec_())