"""
check_setup.py — run this FIRST, before python app.py, to confirm
your folder structure is correct.

Usage:
    python check_setup.py
"""
import os

print("Checking project folder structure...\n")

current_dir = os.getcwd()
print(f"You are running this from: {current_dir}\n")

required_files = ["app.py", "models.py", "requirements.txt", "seed_data.py"]
required_folders = ["templates", "static"]
required_templates = [
    "base.html", "home.html", "property_detail.html", "apply.html",
    "apply_success.html", "admin_login.html", "admin_dashboard.html",
    "add_property.html", "view_applications.html", "user_signup.html",
    "user_login.html", "my_applications.html"
]
required_static = ["style.css", "script.js"]

all_good = True

print("--- Checking root files ---")
for f in required_files:
    exists = os.path.isfile(f)
    print(f"  [{'OK' if exists else 'MISSING'}] {f}")
    if not exists:
        all_good = False

print("\n--- Checking folders ---")
for folder in required_folders:
    exists = os.path.isdir(folder)
    print(f"  [{'OK' if exists else 'MISSING'}] {folder}/")
    if not exists:
        all_good = False

print("\n--- Checking templates/ contents ---")
if os.path.isdir("templates"):
    for t in required_templates:
        path = os.path.join("templates", t)
        exists = os.path.isfile(path)
        print(f"  [{'OK' if exists else 'MISSING'}] templates/{t}")
        if not exists:
            all_good = False
else:
    print("  Cannot check - templates/ folder itself is missing.")
    all_good = False

print("\n--- Checking static/ contents ---")
if os.path.isdir("static"):
    for s in required_static:
        path = os.path.join("static", s)
        exists = os.path.isfile(path)
        print(f"  [{'OK' if exists else 'MISSING'}] static/{s}")
        if not exists:
            all_good = False
else:
    print("  Cannot check - static/ folder itself is missing.")
    all_good = False

print("\n" + "=" * 50)
if all_good:
    print("ALL GOOD. Your folder structure is correct.")
    print("You can now safely run: python app.py")
else:
    print("SOMETHING IS MISSING (see MISSING lines above).")
    print("Fix: make sure you extracted the ENTIRE zip file,")
    print("and that you are running this command from INSIDE")
    print("the 'rental_platform_with_user_accounts' folder")
    print("(the one that directly contains app.py).")
print("=" * 50)
