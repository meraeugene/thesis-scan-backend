import os

# Automatically set project root relative to this config file
CAPSTONE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ^ goes up one level from the folder containing this file; adjust if needed

# Static folder (e.g., web files)
STATIC_DIR = os.path.join(CAPSTONE_ROOT, "web")

# Profile pictures folder
PROFILE_PICTURES_DIR = os.path.join(STATIC_DIR, "profilePicture")

# Ensure the profile picture directory exists
os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)
