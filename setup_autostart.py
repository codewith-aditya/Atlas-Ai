"""
Atlas Auto-Start Setup Script
This script helps you set up Atlas to start automatically with Windows
"""

import os
import sys
import winreg
import shutil

def add_to_startup():
    """Add Atlas to Windows startup"""
    try:
        # Get current script directory
        atlas_dir = os.path.dirname(os.path.abspath(__file__))
        startup_script = os.path.join(atlas_dir, "START_ATLAS.bat")
        
        # Get Windows startup folder
        startup_folder = os.path.join(
            os.environ['APPDATA'],
            r'Microsoft\Windows\Start Menu\Programs\Startup'
        )
        
        # Create shortcut in startup folder
        shortcut_path = os.path.join(startup_folder, "Atlas.bat")
        
        # Copy the startup script to startup folder
        if os.path.exists(startup_script):
            shutil.copy2(startup_script, shortcut_path)
            print("✅ SUCCESS! Atlas added to Windows startup!")
            print(f"📁 Startup location: {shortcut_path}")
            print("\n🎉 Atlas will now start automatically when Windows boots!")
            return True
        else:
            print(f"❌ ERROR: START_ATLAS.bat not found at {startup_script}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to add to startup: {e}")
        return False

def remove_from_startup():
    """Remove Atlas from Windows startup"""
    try:
        startup_folder = os.path.join(
            os.environ['APPDATA'],
            r'Microsoft\Windows\Start Menu\Programs\Startup'
        )
        
        shortcut_path = os.path.join(startup_folder, "Atlas.bat")
        
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            print("✅ Atlas removed from Windows startup!")
            return True
        else:
            print("ℹ️ Atlas is not in startup folder")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to remove from startup: {e}")
        return False

def check_startup_status():
    """Check if Atlas is in startup"""
    startup_folder = os.path.join(
        os.environ['APPDATA'],
        r'Microsoft\Windows\Start Menu\Programs\Startup'
    )
    
    shortcut_path = os.path.join(startup_folder, "Atlas.bat")
    
    if os.path.exists(shortcut_path):
        print("✅ Atlas is currently in Windows startup")
        return True
    else:
        print("❌ Atlas is NOT in Windows startup")
        return False

def main():
    """Main menu"""
    print("="*60)
    print("    ATLAS - Auto-Start Setup")
    print("="*60)
    print()
    
    # Check current status
    check_startup_status()
    print()
    
    print("What would you like to do?")
    print("1. Add Atlas to Windows startup")
    print("2. Remove Atlas from Windows startup")
    print("3. Check startup status")
    print("4. Exit")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🔧 Adding Atlas to startup...")
        add_to_startup()
    elif choice == "2":
        print("\n🔧 Removing Atlas from startup...")
        remove_from_startup()
    elif choice == "3":
        print("\n🔍 Checking status...")
        check_startup_status()
    elif choice == "4":
        print("\n👋 Goodbye!")
        return
    else:
        print("\n❌ Invalid choice!")
    
    print("\n" + "="*60)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
