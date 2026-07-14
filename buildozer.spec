[app]

# (str) Title of your application
title = Mpsck

# (str) Package name
package.name = mpsck

# (str) Package domain (needed for android packaging)
package.domain = org

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application version 
version = 0.1

# (list) List of requirements separated by a comma
requirements = python3==3.10.12, hostpython3==3.10.12, kivy, pyjnius, plyer

# (str) Supported orientations (valid options are: landscape, portrait, all)
orientation = portrait

# (list) Permissions
# android.permissions = INTERNET

# (int) Android API to use (Target SDK)
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25c

# (bool) Use --private data directory for the app
android.private_storage = True

# (list) Android architectures to build for
android.archs = armeabi-v7a, arm64-v8a

# (bool) Allow backup
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
