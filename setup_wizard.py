
"""
Atlas First-Time Setup Wizard
Collects user information on first run - no multiple restarts needed!
"""

import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class WelcomePage(QWizardPage):
    """Welcome page"""
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to Atlas AI Assistant")
        
        layout = QVBoxLayout()
        
        label = QLabel(
            "Welcome! Let's set up your profile.\n\n"
            "Atlas needs to know a bit about you to provide\n"
            "personalized assistance.\n\n"
            "This will only take a minute!\n\n"
            "Click 'Next' to continue."
        )
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 11))
        label.setStyleSheet("color: #00FFCC;")
        
        layout.addWidget(label)
        self.setLayout(layout)

class UserInfoPage(QWizardPage):
    """User information page"""
    def __init__(self):
        super().__init__()
        self.setTitle("Your Information")
        self.setSubTitle("Tell Atlas about yourself")
        
        layout = QVBoxLayout()
        
        # Name
        name_label = QLabel("Your Name:")
        name_label.setFont(QFont("Arial", 10, QFont.Bold))
        name_label.setStyleSheet("color: #00FFCC;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #00FFCC;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.name_input)
        
        # Age
        age_label = QLabel("\nYour Age:")
        age_label.setFont(QFont("Arial", 10, QFont.Bold))
        age_label.setStyleSheet("color: #00FFCC;")
        layout.addWidget(age_label)
        
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Enter your age")
        self.age_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #00FFCC;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.age_input)
        
        # City
        city_label = QLabel("\nYour City:")
        city_label.setFont(QFont("Arial", 10, QFont.Bold))
        city_label.setStyleSheet("color: #00FFCC;")
        layout.addWidget(city_label)
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter your city")
        self.city_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #00FFCC;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.city_input)
        
        # Interests
        interests_label = QLabel("\nYour Interests:")
        interests_label.setFont(QFont("Arial", 10, QFont.Bold))
        interests_label.setStyleSheet("color: #00FFCC;")
        layout.addWidget(interests_label)
        
        self.interests_input = QLineEdit()
        self.interests_input.setPlaceholderText("e.g., coding, music, sports")
        self.interests_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #00FFCC;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.interests_input)
        
        self.setLayout(layout)
        
        # Register required fields
        self.registerField("user_name*", self.name_input)
        self.registerField("user_age*", self.age_input)

class CompletePage(QWizardPage):
    """Completion page"""
    def __init__(self):
        super().__init__()
        self.setTitle("Setup Complete!")
        
        layout = QVBoxLayout()
        
        label = QLabel(
            "✅ Profile saved successfully!\n\n"
            "Atlas is now ready to assist you.\n\n"
            "Click 'Finish' to start Atlas."
        )
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("color: #00FFCC;")
        
        layout.addWidget(label)
        self.setLayout(layout)

class SetupWizard(QWizard):
    """Main setup wizard"""
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Atlas Setup")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setFixedSize(500, 450)
        
        # Dark theme
        self.setStyleSheet("""
            QWizard {
                background-color: #000000;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)
        
        # Add pages
        self.welcome_page = WelcomePage()
        self.user_page = UserInfoPage()
        self.complete_page = CompletePage()
        
        self.addPage(self.welcome_page)
        self.addPage(self.user_page)
        self.addPage(self.complete_page)
        
        # Connect finish button
        self.button(QWizard.FinishButton).clicked.connect(self.save_configuration)
        
    def save_configuration(self):
        """Save user information to file"""
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            materials_path = os.path.join(base_path, "materials")
            
            # Ensure materials folder exists
            os.makedirs(materials_path, exist_ok=True)
            
            # Save user details
            user_details = {
                "name": self.field('user_name'),
                "age": self.field('user_age'),
                "city": self.user_page.city_input.text().strip() or "Unknown",
                "interests": self.user_page.interests_input.text().strip() or "General"
            }
            
            import json
            user_file = os.path.join(materials_path, "user_details.json")
            with open(user_file, 'w') as f:
                json.dump(user_details, f, indent=4)
            
            # Create setup complete marker
            setup_marker = os.path.join(materials_path, ".setup_complete")
            with open(setup_marker, 'w') as f:
                f.write("Setup completed successfully")
            
            print("✅ [SETUP] User profile saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save profile: {e}")
            print(f"❌ [SETUP] Error: {e}")

def needs_setup():
    """Check if setup is needed"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    materials_path = os.path.join(base_path, "materials")
    setup_marker = os.path.join(materials_path, ".setup_complete")
    
    # Check if setup marker exists
    return not os.path.exists(setup_marker)

def run_setup_wizard():
    """Run the setup wizard"""
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    
    if wizard.exec_() == QWizard.Accepted:
        print("✅ [SETUP] Setup completed successfully!")
        return True
    else:
        print("❌ [SETUP] Setup cancelled by user")
        return False

if __name__ == "__main__":
    if needs_setup():
        print("🔧 [SETUP] Running first-time setup wizard...")
        run_setup_wizard()
    else:
        print("ℹ️ [SETUP] Setup already completed")
