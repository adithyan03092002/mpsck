[app]

# (string) Title of your application
title = mpsck

# (string) Application version
version = 0.1

# (string) Package name
package.name = mpsck

# (string) Package domain (needed for android packaging)
package.domain = org.adithyan

# (string) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1,kivy-garden,pyjnius,plyer

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse, landscape-reverse
orientation = portrait

# =============================================================================
# Android specific configuration
# =============================================================================

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = RECORD_AUDIO, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (bool) Use --private data storage (True) or --dir data storage (False)
android.private_storage = True

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# android.add_jars = foo.jar

# (list) List of Java classes to add to the intent filters
# android.add_intent_filters =

# (list) Android AAR archives to add
# android.add_aars =

# (str) Bootstrap to use for android outputs
p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
