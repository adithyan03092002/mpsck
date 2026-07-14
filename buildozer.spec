[app]

# (str) Title of your application
title = My Application

# (str) Package name
package.name = myapp

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of requirements separated by a comma
# GitHub Actions-ൽ എറർ വരാതിരിക്കാൻ പൈത്തൺ വേർഷൻ ഇവിടെ ലോക്ക് ചെയ്തിട്ടുണ്ട്
requirements = python3==3.10.12, hostpython3==3.10.12, kivy, pyjnius, plyer

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (int) Presplash screen duration
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientations (valid options are: landscape, portrait, all)
orientation = portrait

# (list) Permissions
# android.permissions = INTERNET

# (int) Android API to use (Target SDK)
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
# പൈത്തൺ 3.10-ന് ഏറ്റവും അനുയോജ്യമായ NDK വേർഷനാണിത്
android.ndk = 25c

# (bool) Use --private data directory for the app
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded)
# android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded)
# android.sdk_path =

# (list) Android architectures to build for
android.archs = armeabi-v7a, arm64-v8a

# (bool) Allow backup
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
