import sys
import os
import traceback

print("--- LAUNCHER STARTED ---")

# 1. Add the current directory to Python's path (Fixes the "No module" error)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
print(f"Working Directory set to: {current_dir}")

try:
    print("Attempting to import GUI...")
    from gui.main_window import EduEngageApp
    print("GUI Module Imported Successfully.")
    
    print("Initializing App...")
    app = EduEngageApp()
    
    print("Starting Main Loop...")
    app.mainloop()
    
except Exception as e:
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("CRITICAL ERROR DURING STARTUP")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # This prints the exact reason why it crashed
    traceback.print_exc()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

input("Press Enter to close...")