"""
My PSC Knowledge - Fully Working Mock Test Engine & Fixed Screen Transitions
+ Self Study Assist (Voice Q&A) Feature
Framework: Kivy
"""

import os
import json
import random
import difflib

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle

# UI Themes Configuration
LIGHT_BG = (1, 1, 1, 1)
DARK_BG = (0.1, 0.12, 0.18, 1)

DARK_BLUE = (0.05, 0.23, 0.48, 1)
MID_BLUE = (0.08, 0.23, 0.48, 1)
LIGHT_BLUE_CARD = (0.95, 0.95, 0.98, 1)
DARK_BLUE_CARD = (0.15, 0.18, 0.26, 1)

TEXT_LIGHT = (0.1, 0.1, 0.1, 1)
TEXT_DARK = (0.95, 0.95, 0.95, 1)

GREEN = (0.1, 0.6, 0.2, 1)
RED = (0.8, 0.2, 0.2, 1)
YELLOW = (0.9, 0.7, 0.0, 1)

LANG_DATA = {
    "English": {
        "title": "My PSC Knowledge",
        "add_q": "+   Add Question",
        "practice": ">   Practice",
        "mock": "#   Mock Test",
        "fav": "* Favourite",
        "settings": "o   Settings",
        "save": "Save",
        "back": "Back",
        "next": "Next Question",
        "q_count": "Total Questions Added:",
        "dark_mode": "Dark Mode",
        "lang": "Language",
        "saved_list_lbl": "What are the questions saved:",
        "no_qs": "No questions saved in App yet!"
    },
    "Malayalam": {
        "title": "മൈ PSC നോളഡ്ജ്",
        "add_q": "+   ചോദ്യം ചേർക്കുക",
        "practice": ">   പ്രാക്ടീസ്",
        "mock": "#   മോക്ക് ടെസ്റ്റ്",
        "fav": "* ഫേവറിറ്റ്സ്",
        "settings": "ോ   സെറ്റിങ്സ്",
        "save": "സേവ് ചെയ്യുക",
        "back": "തിരികെ",
        "next": "അടുത്ത ചോദ്യം",
        "q_count": "ആകെ ചേർത്ത ചോദ്യങ്ങൾ:",
        "dark_mode": "ഡാർക്ക് മോഡ്",
        "lang": "ഭാഷ",
        "saved_list_lbl": "സേവ് ചെയ്ത ചോദ്യങ്ങൾ താഴെ:",
        "no_qs": "ചോദ്യങ്ങൾ ഒന്നും സേവ് ചെയ്തിട്ടില്ല!"
    }
}

def find_file(filename_contains, search_roots, exact_names=None):
    exact_names = exact_names or []
    for root in search_roots:
        if not os.path.isdir(root):
            continue
        try:
            for dirpath, dirnames, filenames in os.walk(root):
                depth = dirpath[len(root):].count(os.sep)
                if depth > 4:
                    dirnames[:] = []
                    continue
                for fn in filenames:
                    if fn in exact_names:
                        return os.path.join(dirpath, fn)
                    low = fn.lower()
                    if any(part.lower() in low for part in filename_contains) and fn.lower().endswith((".ttf", ".otf")):
                        return os.path.join(dirpath, fn)
        except PermissionError:
            continue
    return None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEARCH_ROOTS = [SCRIPT_DIR, "/storage/emulated/0/Download", "/storage/emulated/0/Android/media", "/storage/emulated/0/Pictures", "/storage/emulated/0"]

LOGO_PATH = os.path.join(SCRIPT_DIR, "logo.png")
MAL_FONT = find_file(["malayalam"], SEARCH_ROOTS, exact_names=["NotoSansMalayalam-Regular.ttf"])


# ==========================================================================
# VOICE ENGINE  -  Android TTS (read question aloud) + Speech-to-Text (mic)
# ==========================================================================
ANDROID = False
try:
    from jnius import autoclass, PythonJavaClass, java_method
    from android import activity
    ANDROID = True
except Exception:
    ANDROID = False


if ANDROID:
    class TTSInitListener(PythonJavaClass):
        __javainterfaces__ = ['android/speech/tts/TextToSpeech$OnInitListener']
        __javacontext__ = 'app'

        def __init__(self, callback):
            super().__init__()
            self.callback = callback

        @java_method('(I)V')
        def onInit(self, status):
            self.callback(status)

    class JavaRunnable(PythonJavaClass):
        __javainterfaces__ = ['java/lang/Runnable']
        __javacontext__ = 'app'

        def __init__(self, func):
            super().__init__()
            self.func = func

        @java_method('()V')
        def run(self):
            try:
                self.func()
            except Exception as e:
                print("JavaRunnable error:", e)

    class SpeechListener(PythonJavaClass):
        __javainterfaces__ = ['android/speech/RecognitionListener']
        __javacontext__ = 'app'

        def __init__(self, on_results, on_error):
            super().__init__()
            self.on_results = on_results
            self.on_error = on_error

        @java_method('(Landroid/os/Bundle;)V')
        def onReadyForSpeech(self, params):
            pass

        @java_method('()V')
        def onBeginningOfSpeech(self):
            pass

        @java_method('(F)V')
        def onRmsChanged(self, rmsdB):
            pass

        @java_method('([B)V')
        def onBufferReceived(self, buffer):
            pass

        @java_method('()V')
        def onEndOfSpeech(self):
            pass

        @java_method('(I)V')
        def onError(self, error):
            self.on_error(error)

        @java_method('(Landroid/os/Bundle;)V')
        def onResults(self, results):
            try:
                SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
                matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                text = matches.get(0) if matches and matches.size() > 0 else None
            except Exception as e:
                print("onResults parse failed:", e)
                text = None
            self.on_results(text)

        @java_method('(Landroid/os/Bundle;)V')
        def onPartialResults(self, partialResults):
            pass

        @java_method('(ILandroid/os/Bundle;)V')
        def onEvent(self, eventType, params):
            pass


class VoiceEngine:
    def __init__(self):
        self.tts = None
        self.tts_ready = False
        self._pending_speech = None
        self._pending_lang = "en-IN"
        self._activity = None
        self.recognizer = None
        self.listener = None
        self.stt_callback = None
        self.init_error = None

        if ANDROID:
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.RECORD_AUDIO])
            except Exception as e:
                print("Permission request failed:", e)
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
                self._activity = PythonActivity.mActivity
                self._tts_listener = TTSInitListener(self._on_tts_init)
                self.tts = TextToSpeech(self._activity, self._tts_listener)
            except Exception as e:
                self.init_error = str(e)
                print("VoiceEngine init failed:", e)

    def status_text(self):
        if not ANDROID:
            return "jnius/android modules not found (pip install pyjnius in Pydroid3)"
        if self.init_error:
            return f"Init error: {self.init_error}"
        if not self._activity:
            return "No Activity reference (PythonActivity not found)"
        if not self.tts:
            return "TTS object not created"
        if not self.tts_ready:
            return "TTS engine still initializing..."
        return "Voice engine OK"

    def _on_tts_init(self, status):
        self.tts_ready = (status == 0)
        if self.tts_ready and self._pending_speech:
            text, lang = self._pending_speech, self._pending_lang
            self._pending_speech = None
            self.speak(text, lang)

    def speak(self, text, lang_code="en-IN"):
        if not text:
            return
        if not (ANDROID and self.tts):
            print("[TTS unavailable - would say]:", text)
            return
        if not self.tts_ready:
            self._pending_speech = text
            self._pending_lang = lang_code
            return
        try:
            Locale = autoclass('java.util.Locale')
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
            loc = Locale("ml", "IN") if lang_code.startswith("ml") else Locale("en", "IN")
            result = self.tts.setLanguage(loc)
            if result < 0:
                self.tts.setLanguage(Locale("en", "IN"))
            self.tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, None)
        except Exception as e:
            print("TTS speak failed:", e)

    def listen(self, callback, lang_code="ml-IN"):
        self.stt_callback = callback
        if not ANDROID or not self._activity:
            callback(None)
            return

        def _start():
            try:
                SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
                RecognizerIntent = autoclass('android.speech.RecognizerIntent')
                Intent = autoclass('android.content.Intent')

                if self.recognizer is None:
                    self.recognizer = SpeechRecognizer.createSpeechRecognizer(self._activity)
                    self.listener = SpeechListener(self._on_speech_results, self._on_speech_error)
                    self.recognizer.setRecognitionListener(self.listener)

                intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang_code)
                intent.putExtra("android.speech.extra.PREFER_OFFLINE", True)
                intent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, False)
                self.recognizer.startListening(intent)
            except Exception as e:
                print("STT start failed:", e)
                Clock.schedule_once(lambda dt: callback(None))

        try:
            self._activity.runOnUiThread(JavaRunnable(_start))
        except Exception as e:
            print("STT setup failed:", e)
            callback(None)

    def _on_speech_results(self, text):
        cb = self.stt_callback
        if cb:
            Clock.schedule_once(lambda dt: cb(text))

    def _on_speech_error(self, error_code):
        print("Speech recognition error code:", error_code)
        cb = self.stt_callback
        if cb:
            Clock.schedule_once(lambda dt: cb(None))


def answers_match(user_text, correct_text):
    if not user_text or not correct_text:
        return False
    a = user_text.strip().lower()
    b = correct_text.strip().lower()
    if a == b:
        return True
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    return ratio >= 0.65


class RoundedButton(Button):
    def __init__(self, bg_color=MID_BLUE, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_name = MAL_FONT
        with self.canvas.before:
            self.paint_color = Color(*bg_color)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def change_color(self, new_color):
        self.paint_color.rgba = new_color


class FieldLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = DARK_BLUE
        self.bold = True
        self.font_size = "17sp"
        self.font_name = MAL_FONT
        self.size_hint_y = None
        self.height = "30dp"
        self.halign = "left"
        self.valign = "middle"
        self.bind(size=lambda *a: setattr(self, "text_size", self.size))


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_base_bg, size=self.update_base_bg)

    def update_base_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.bg_color.rgba = DARK_BG if app.dark_mode else LIGHT_BG


class SplashScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        self.add_widget(root)

        if os.path.exists(LOGO_PATH):
            self.logo = Image(source=LOGO_PATH, size_hint=(0.5, 0.5), pos_hint={"center_x": 0.5, "center_y": 0.62}, opacity=0)
            root.add_widget(self.logo)
        else:
            self.logo = Label(text="📚", font_size="90sp", size_hint=(0.5, 0.5), pos_hint={"center_x": 0.5, "center_y": 0.62}, opacity=0)
            root.add_widget(self.logo)

        self.title = Label(text="My PSC Knowledge", font_size="30sp", bold=True, font_name=MAL_FONT, color=DARK_BLUE, size_hint=(1, 0.08), pos_hint={"center_x": 0.5, "y": 0.32}, opacity=0)
        root.add_widget(self.title)

        self.tagline = Label(text="Practice.  Study.  Success", font_size="18sp", font_name=MAL_FONT, color=(0.4, 0.4, 0.4, 1), size_hint=(1, 0.06), pos_hint={"center_x": 0.5, "y": 0.25}, opacity=0)
        root.add_widget(self.tagline)

        self.get_started = RoundedButton(text="Get Started", font_size="20sp", size_hint=(0.6, 0.08), pos_hint={"center_x": 0.5, "y": 0.08}, opacity=0)
        self.get_started.disabled = True
        self.get_started.bind(on_release=self.go_next)
        root.add_widget(self.get_started)
        Clock.schedule_once(self.start_animation, 0.1)

    def start_animation(self, *args):
        app = App.get_running_app()
        self.title.color = TEXT_DARK if app.dark_mode else DARK_BLUE
        Animation(opacity=1, duration=1.0, t="out_quad").start(self.logo)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.7).start(self.title), 0.5)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.7).start(self.tagline), 0.8)
        def enable_button(dt):
            self.get_started.disabled = False
            Animation(opacity=1, duration=0.6).start(self.get_started)
        Clock.schedule_once(enable_button, 1.2)

    def go_next(self, *args):
        self.manager.current = "home"


class HomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer = FloatLayout()
        self.add_widget(self.outer)
        self.heading = Label(text="", font_size="26sp", bold=True, font_name=MAL_FONT, color=DARK_BLUE, size_hint=(1, 0.08), pos_hint={"center_x": 0.5, "top": 0.98})
        self.outer.add_widget(self.heading)
        self.menu_layout = BoxLayout(orientation="vertical", spacing=18, padding=[30, 0, 30, 40], size_hint=(1, 0.75), pos_hint={"center_x": 0.5, "center_y": 0.45})
        self.outer.add_widget(self.menu_layout)
        self.bind(on_enter=self.update_ui)

    def update_ui(self, *args):
        app = App.get_running_app()
        lang = app.lang
        self.heading.text = LANG_DATA[lang]["title"]
        self.heading.color = TEXT_DARK if app.dark_mode else DARK_BLUE

        self.menu_layout.clear_widgets()
        items = [
            (LANG_DATA[lang]["add_q"], "add_question"),
            (LANG_DATA[lang]["practice"], "practice"),
            (LANG_DATA[lang]["mock"], "mock_test"),
            (LANG_DATA[lang]["fav"], "favourite_view"),
            (LANG_DATA[lang]["settings"], "settings_screen"),
        ]
        for label, screen_name in items:
            btn = RoundedButton(text="  " + label, font_size="22sp", size_hint_y=None, height="58dp")
            btn.halign = "left"
            btn.valign = "middle"
            btn.bind(size=lambda inst, val, b=btn: setattr(b, "text_size", (val[0]-40, val[1])))
            if screen_name:
                btn.bind(on_release=lambda inst, s=screen_name: self.go_to(s))
            self.menu_layout.add_widget(btn)

    def go_to(self, screen_name):
        self.manager.current = screen_name


class PracticeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer = FloatLayout()
        self.add_widget(self.outer)
        self.bind(on_enter=self.setup_view)

    def setup_view(self, *args):
        self.outer.clear_widgets()
        app = App.get_running_app()
        lang = app.lang

        heading = Label(text=LANG_DATA[lang]["practice"], font_size="26sp", bold=True, font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else DARK_BLUE, size_hint=(1, 0.08), pos_hint={"center_x": 0.5, "top": 0.98})
        self.outer.add_widget(heading)

        menu = BoxLayout(orientation="vertical", spacing=20, padding=[40, 0, 40, 40], size_hint=(1, 0.5), pos_hint={"center_x": 0.5, "center_y": 0.45})
        btn_self = RoundedButton(text="  Self Study Assist", font_size="22sp")
        btn_prac = RoundedButton(text="  Practice MCQ", font_size="22sp")
        btn_back = RoundedButton(text="  " + LANG_DATA[lang]["back"], font_size="22sp")

        btn_self.bind(on_release=lambda x: setattr(self.manager, 'current', 'self_study'))
        btn_prac.bind(on_release=lambda x: setattr(self.manager, 'current', 'mcq_practice'))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))

        menu.add_widget(btn_self)
        menu.add_widget(btn_prac)
        menu.add_widget(btn_back)
        self.outer.add_widget(menu)


class SelfStudyScreen(BaseScreen):
    MAX_ATTEMPTS = 4

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer = FloatLayout()
        self.add_widget(self.outer)
        self.current_q = None
        self.attempts = 0
        self.locked = False
        self.voice = None
        self.bind(on_enter=self.setup_view)

    def setup_view(self, *args):
        self.outer.clear_widgets()
        app = App.get_running_app()
        self.attempts = 0
        self.locked = False
        self.bg_color.rgba = DARK_BG if app.dark_mode else LIGHT_BG

        if getattr(self, "_status_poll_event", None):
            Clock.unschedule(self._status_poll_event)
            self._status_poll_event = None

        if self.voice is None:
            if not hasattr(app, "voice_engine"):
                app.voice_engine = VoiceEngine()
            self.voice = app.voice_engine

        if not app.questions:
            lbl = Label(text="Add some questions first!", font_name=MAL_FONT,
                        color=TEXT_DARK if app.dark_mode else DARK_BLUE,
                        pos_hint={"center_x": 0.5, "center_y": 0.5})
            self.outer.add_widget(lbl)
            return

        header = BoxLayout(size_hint=(1, 0.08), pos_hint={"top": 1}, padding=[10, 10, 10, 10])
        back_btn = RoundedButton(text="<", size_hint=(0.15, 1), font_size="20sp")
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'practice'))
        header.add_widget(back_btn)
        header.add_widget(Label(text="Self Study Assist", font_size="20sp", bold=True,
                                 font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.outer.add_widget(header)

        self.lbl_attempts = Label(text=f"Attempts left: {self.MAX_ATTEMPTS}", font_size="14sp",
                                   color=(0.5, 0.5, 0.5, 1), size_hint=(0.9, 0.04),
                                   pos_hint={"center_x": 0.5, "top": 0.90})
        self.outer.add_widget(self.lbl_attempts)

        self.lbl_voice_status = Label(text=f"Voice: {self.voice.status_text()}", font_size="11sp",
                                       color=(0.6, 0.6, 0.6, 1), size_hint=(0.9, 0.03),
                                       pos_hint={"center_x": 0.5, "top": 0.86})
        self.outer.add_widget(self.lbl_voice_status)
        
        self._status_poll_count = 0
        self._status_poll_event = Clock.schedule_interval(self._poll_voice_status, 1)

        scroll = ScrollView(size_hint=(0.9, 0.22), pos_hint={"center_x": 0.5, "top": 0.82})
        self.lbl_question = Label(text="", font_size="19sp", bold=True, font_name=MAL_FONT,
                                   color=TEXT_DARK if app.dark_mode else DARK_BLUE,
                                   size_hint_y=None, halign="center", valign="middle")
        self.lbl_question.bind(size=lambda *a: setattr(self.lbl_question, "text_size", (self.lbl_question.width, None)))
        scroll.add_widget(self.lbl_question)
        self.outer.add_widget(scroll)

        self.lbl_feedback = Label(text="", font_size="16sp", font_name=MAL_FONT, bold=True,
                                   color=(0.5, 0.5, 0.5, 1), size_hint=(0.9, 0.08),
                                   pos_hint={"center_x": 0.5, "top": 0.56})
        self.outer.add_widget(self.lbl_feedback)

        btn_row = BoxLayout(orientation="horizontal", spacing=15, size_hint=(0.85, 0.09),
                             pos_hint={"center_x": 0.5, "top": 0.46})
        self.btn_listen = RoundedButton(text="🔊 Listen Again", font_size="16sp", bg_color=MID_BLUE)
        self.btn_listen.bind(on_release=lambda x: self.speak_question())
        self.btn_mic = RoundedButton(text="🎤 Speak Answer", font_size="16sp", bg_color=GREEN)
        self.btn_mic.bind(on_release=lambda x: self.start_listening())
        btn_row.add_widget(self.btn_listen)
        btn_row.add_widget(self.btn_mic)
        self.outer.add_widget(btn_row)

        self.typed_input = TextInput(hint_text="Or type your answer here", multiline=False,
                                      size_hint=(0.85, 0.06), pos_hint={"center_x": 0.5, "top": 0.34},
                                      font_name=MAL_FONT)
        self.btn_submit_typed = RoundedButton(text="Submit Typed Answer", font_size="14sp",
                                               size_hint=(0.85, 0.06), pos_hint={"center_x": 0.5, "top": 0.27},
                                               bg_color=MID_BLUE)
        self.btn_submit_typed.bind(on_release=lambda x: self.check_answer(self.typed_input.text))
        self.outer.add_widget(self.typed_input)
        self.outer.add_widget(self.btn_submit_typed)

        self.btn_show_answer = RoundedButton(text="📖 Show Answer", font_size="16sp",
                                              size_hint=(0.85, 0.07), pos_hint={"center_x": 0.5, "y": 0.11},
                                              bg_color=YELLOW)
        self.btn_show_answer.bind(on_release=lambda x: self.reveal_answer())
        self.btn_show_answer.opacity = 0
        self.btn_show_answer.disabled = True
        self.outer.add_widget(self.btn_show_answer)

        self.btn_next = RoundedButton(text="⏭️ Next Question", font_size="16sp",
                                       size_hint=(0.85, 0.07), pos_hint={"center_x": 0.5, "y": 0.02},
                                       bg_color=DARK_BLUE)
        self.btn_next.bind(on_release=lambda x: self.setup_view())
        self.btn_next.opacity = 0
        self.btn_next.disabled = True
        self.outer.add_widget(self.btn_next)

        self.current_q = random.choice(app.questions)
        self.lbl_question.text = self.current_q.get("question", "")
        Clock.schedule_once(lambda dt: self.speak_question(), 1.2)

    def _poll_voice_status(self, dt):
        self._status_poll_count += 1
        status = self.voice.status_text()
        self.lbl_voice_status.text = f"Voice: {status}"
        if status == "Voice engine OK" or self._status_poll_count >= 15:
            if self._status_poll_event:
                Clock.unschedule(self._status_poll_event)
                self._status_poll_event = None

    def speak_question(self):
        if self.locked or not self.current_q:
            return
        app = App.get_running_app()
        lang_code = "ml-IN" if app.lang == "Malayalam" else "en-IN"
        self.voice.speak(self.current_q.get("question", ""), lang_code)

    def start_listening(self):
        if self.locked:
            return
        self.lbl_feedback.text = "Listening..."
        self.lbl_feedback.color = MID_BLUE
        app = App.get_running_app()
        lang_code = "ml-IN" if app.lang == "Malayalam" else "en-IN"
        self.voice.listen(self.on_voice_result, lang_code)

    def on_voice_result(self, text):
        if text is None:
            self.lbl_feedback.text = "Couldn't hear you - try again or type below."
            self.lbl_feedback.color = RED
            return
        self.typed_input.text = text
        self.check_answer(text)

    def check_answer(self, user_text):
        if self.locked or not self.current_q:
            return
        correct = self.current_q.get("answer", "")
        if answers_match(user_text, correct):
            self.on_correct()
        else:
            self.on_wrong()

    def on_correct(self):
        self.locked = True
        self.bg_color.rgba = GREEN
        self.lbl_feedback.text = "✅ Correct!"
        self.lbl_feedback.color = (1, 1, 1, 1)
        self.btn_mic.disabled = True
        self.btn_submit_typed.disabled = True
        self.btn_next.opacity = 1
        self.btn_next.disabled = False

    def on_wrong(self):
        self.attempts += 1
        remaining = self.MAX_ATTEMPTS - self.attempts
        app = App.get_running_app()
        self.typed_input.text = ""
        if remaining > 0:
            self.lbl_attempts.text = f"Attempts left: {remaining}"
            self.lbl_feedback.text = "❌ Wrong, try again"
            self.lbl_feedback.color = RED
            lang_code = "ml-IN" if app.lang == "Malayalam" else "en-IN"
            msg = "തെറ്റാണ്, വീണ്ടും ശ്രമിക്കൂ" if app.lang == "Malayalam" else "Wrong answer, try again"
            self.voice.speak(msg, lang_code)
        else:
            self.locked = True
            self.lbl_attempts.text = "Attempts left: 0"
            self.lbl_feedback.text = "❌ Out of attempts"
            self.lbl_feedback.color = RED
            self.btn_mic.disabled = True
            self.btn_submit_typed.disabled = True
            app.add_to_improve(self.current_q)
            self.btn_show_answer.opacity = 1
            self.btn_show_answer.disabled = False
            self.btn_next.opacity = 1
            self.btn_next.disabled = False

    def reveal_answer(self):
        app = App.get_running_app()
        correct = self.current_q.get("answer", "")
        self.lbl_feedback.text = f"Answer: {correct}"
        self.lbl_feedback.color = YELLOW
        lang_code = "ml-IN" if app.lang == "Malayalam" else "en-IN"
        self.voice.speak(correct, lang_code)


class McqPracticeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_q = None
        self.correct_ans = ""
        self.option_buttons = []
        self.outer = FloatLayout()
        self.add_widget(self.outer)
        self.bind(on_enter=self.setup_quiz)

    def setup_quiz(self, *args):
        self.outer.clear_widgets()
        self.option_buttons = []
        app = App.get_running_app()
        lang = app.lang

        header = BoxLayout(size_hint=(1, 0.08), pos_hint={"top": 1}, padding=[10, 10, 10, 10])
        back_btn = RoundedButton(text="<", size_hint=(0.15, 1), font_size="20sp")
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'practice'))
        header.add_widget(back_btn)
        header.add_widget(Label(text="Practice Mode", font_size="22sp", bold=True, font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.outer.add_widget(header)

        self.lbl_topic = Label(text="", font_size="14sp", color=(0.5, 0.5, 0.5, 1), size_hint=(0.9, 0.04), pos_hint={"center_x": 0.5, "top": 0.91}, font_name=MAL_FONT)
        self.outer.add_widget(self.lbl_topic)

        scroll = ScrollView(size_hint=(0.9, 0.22), pos_hint={"center_x": 0.5, "top": 0.87})
        self.lbl_question = Label(text="Loading...", font_size="19sp", bold=True, color=TEXT_DARK if app.dark_mode else DARK_BLUE, size_hint_y=None, font_name=MAL_FONT, halign="center", valign="middle")
        self.lbl_question.bind(size=lambda *a: setattr(self.lbl_question, "text_size", (self.lbl_question.width, None)))
        scroll.add_widget(self.lbl_question)
        self.outer.add_widget(scroll)

        self.options_layout = BoxLayout(orientation="vertical", spacing=12, size_hint=(0.9, 0.45), pos_hint={"center_x": 0.5, "center_y": 0.38})
        for i in range(4):
            btn = RoundedButton(text="", font_size="16sp")
            btn.bind(on_release=self.check_answer)
            self.option_buttons.append(btn)
            self.options_layout.add_widget(btn)
        self.outer.add_widget(self.options_layout)

        self.btn_next = RoundedButton(text=LANG_DATA[lang]["next"], font_size="18sp", size_hint=(0.6, 0.07), pos_hint={"center_x": 0.5, "y": 0.03}, bg_color=GREEN)
        self.btn_next.bind(on_release=self.next_question)
        self.outer.add_widget(self.btn_next)

        if len(app.questions) < 4:
            self.lbl_question.text = "Min. 4 questions required to generate options!"
            for btn in self.option_buttons:
                btn.opacity = 0
                btn.disabled = True
            self.btn_next.disabled = True
        else:
            self.next_question()

    def next_question(self, *args):
        app = App.get_running_app()
        for btn in self.option_buttons:
            btn.change_color(MID_BLUE)
            btn.disabled = False
        self.current_q = random.choice(app.questions)
        self.correct_ans = self.current_q.get('answer', '').strip()
        self.lbl_topic.text = f"Topic: {self.current_q.get('topic')} | Category: {self.current_q.get('category')}"
        self.lbl_question.text = self.current_q.get('question', '')
        all_other_answers = [q.get('answer', '').strip() for q in app.questions if q.get('answer', '').strip() != self.correct_ans]
        if len(set(all_other_answers)) >= 3:
            fake_options = random.sample(list(set(all_other_answers)), 3)
        else:
            fake_options = (all_other_answers * 3)[:3]
        options = fake_options + [self.correct_ans]
        random.shuffle(options)
        prefixes = ["A)  ", "B)  ", "C)  ", "D)  "]
        for i, btn in enumerate(self.option_buttons):
            btn.text = prefixes[i] + options[i]
            btn.real_val = options[i]

    def check_answer(self, instance):
        for btn in self.option_buttons:
            btn.disabled = True
        if instance.real_val == self.correct_ans:
            instance.change_color(GREEN)
        else:
            instance.change_color(RED)
            for btn in self.option_buttons:
                if btn.real_val == self.correct_ans:
                    btn.change_color(GREEN)


class MockTestScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer = FloatLayout()
        self.add_widget(self.outer)
        self.bind(on_enter=self.show_dashboard)

    def show_dashboard(self, *args):
        self.outer.clear_widgets()
        app = App.get_running_app()
        lang = app.lang

        header = BoxLayout(size_hint=(1, 0.08), pos_hint={"top": 1}, padding=[10, 10, 10, 10])
        back_btn = RoundedButton(text="<", size_hint=(0.15, 1), font_size="20sp")
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back_btn)
        header.add_widget(Label(text=LANG_DATA[lang]["mock"], font_size="22sp", bold=True, font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.outer.add_widget(header)

        self.menu_box = BoxLayout(orientation="vertical", spacing=20, padding=[40, 0, 40, 0], size_hint=(1, 0.3), pos_hint={"center_x": 0.5, "center_y": 0.5})

        btn_start = RoundedButton(text=">   Start Test (100 Qs / 90 Mins)", font_size="18sp", bg_color=GREEN)
        btn_start.bind(on_release=self.start_mock_test_process)
        self.menu_box.add_widget(btn_start)

        self.outer.add_widget(self.menu_box)

    def start_mock_test_process(self, *args):
        app = App.get_running_app()
        if len(app.questions) < 4:
            self.menu_box.clear_widgets()

            error_lbl = Label(
                text="Requires at least 4 questions total\nto generate choices for a test!",
                font_size="16sp", color=RED, font_name=MAL_FONT,
                halign="center", size_hint_y=0.6
            )
            error_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

            retry_btn = RoundedButton(text="🔄 Clear Warning & Try Again", font_size="16sp", size_hint_y=0.4, bg_color=MID_BLUE)
            retry_btn.bind(on_release=self.show_dashboard)

            self.menu_box.add_widget(error_lbl)
            self.menu_box.add_widget(retry_btn)
        else:
            self.manager.current = "mock_exam"


class MockExamScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exam_questions = []
        self.current_idx = 0
        self.time_remaining = 5400
        self.timer_event = None
        self.option_buttons = []

        self.outer = FloatLayout()
        self.add_widget(self.outer)

    def on_enter(self, *args):
        app = App.get_running_app()
        self.outer.clear_widgets()
        self.option_buttons = []
        self.current_idx = 0
        self.time_remaining = 5400

        self.exam_questions = list(app.questions)
        random.shuffle(self.exam_questions)
        if len(self.exam_questions) > 100:
            self.exam_questions = self.exam_questions[:100]

        header = BoxLayout(size_hint=(1, 0.08), pos_hint={"top": 1}, padding=[15, 5, 15, 5])
        exit_btn = RoundedButton(text="Exit", size_hint=(0.18, 1), bg_color=RED, font_size="14sp")
        exit_btn.bind(on_release=self.exit_exam)
        header.add_widget(exit_btn)

        self.lbl_progress = Label(text="Q: 1/100", font_size="16sp", bold=True, color=TEXT_DARK if app.dark_mode else DARK_BLUE)
        header.add_widget(self.lbl_progress)

        self.lbl_timer = Label(text="90:00", font_size="16sp", bold=True, color=YELLOW)
        header.add_widget(self.lbl_timer)
        self.outer.add_widget(header)

        scroll = ScrollView(size_hint=(0.9, 0.25), pos_hint={"center_x": 0.5, "top": 0.90})
        self.lbl_q_text = Label(text="", font_size="19sp", bold=True, color=TEXT_DARK if app.dark_mode else DARK_BLUE, size_hint_y=None, font_name=MAL_FONT, halign="center", valign="middle")
        self.lbl_q_text.bind(size=lambda *a: setattr(self.lbl_q_text, "text_size", (self.lbl_q_text.width, None)))
        scroll.add_widget(self.lbl_q_text)
        self.outer.add_widget(scroll)

        self.options_layout = BoxLayout(orientation="vertical", spacing=12, size_hint=(0.9, 0.44), pos_hint={"center_x": 0.5, "center_y": 0.36})
        for i in range(4):
            btn = RoundedButton(text="", font_size="15sp")
            btn.bind(on_release=self.select_option)
            self.option_buttons.append(btn)
            self.options_layout.add_widget(btn)
        self.outer.add_widget(self.options_layout)

        self.btn_next = RoundedButton(text="Next Question >", font_size="18sp", size_hint=(0.6, 0.07), pos_hint={"center_x": 0.5, "y": 0.04}, bg_color=MID_BLUE)
        self.btn_next.bind(on_release=self.load_next_question)
        self.outer.add_widget(self.btn_next)

        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        self.display_question()

    def display_question(self):
        app = App.get_running_app()
        q_data = self.exam_questions[self.current_idx]
        self.lbl_progress.text = f"Q: {self.current_idx + 1}/{len(self.exam_questions)}"
        self.lbl_q_text.text = q_data.get('question', '')

        for btn in self.option_buttons:
            btn.change_color(MID_BLUE)
            btn.disabled = False

        correct = q_data.get('answer', '').strip()
        all_alts = [q.get('answer', '').strip() for q in app.questions if q.get('answer', '').strip() != correct]
        if len(set(all_alts)) >= 3:
            choices = random.sample(list(set(all_alts)), 3)
        else:
            choices = (all_alts * 3)[:3]
        choices.append(correct)
        random.shuffle(choices)

        prefixes = ["A) ", "B) ", "C) ", "D) "]
        for i, btn in enumerate(self.option_buttons):
            btn.text = prefixes[i] + choices[i]
            btn.real_val = choices[i]
            btn.correct_val = correct

    def select_option(self, instance):
        for btn in self.option_buttons:
            btn.disabled = True
        if instance.real_val == instance.correct_val:
            instance.change_color(GREEN)
        else:
            instance.change_color(RED)
            for btn in self.option_buttons:
                if btn.real_val == btn.correct_val:
                    btn.change_color(GREEN)

    def load_next_question(self, *args):
        if self.current_idx < len(self.exam_questions) - 1:
            self.current_idx += 1
            self.display_question()
        else:
            self.exit_exam()

    def update_timer(self, dt):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            mins, secs = divmod(self.time_remaining, 60)
            self.lbl_timer.text = f"{mins:02d}:{secs:02d}"
        else:
            self.exit_exam()

    def exit_exam(self, *args):
        if self.timer_event:
            Clock.unschedule(self.timer_event)
        self.manager.current = "mock_test"


class FavouriteViewScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer = FloatLayout()
        self.add_widget(self.outer)
        self.view_mode = "fav"
        self.bind(on_enter=self.load_fav_list)

    def load_fav_list(self, *args):
        self.outer.clear_widgets()
        app = App.get_running_app()
        lang = app.lang

        header = BoxLayout(size_hint=(1, 0.08), pos_hint={"top": 1}, padding=[10, 10, 10, 10])
        back_btn = RoundedButton(text="<", size_hint=(0.15, 1), font_size="20sp")
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back_btn)
        title = LANG_DATA[lang]["fav"] if self.view_mode == "fav" else "📈 Improve List"
        header.add_widget(Label(text=title, font_size="20sp", bold=True, font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.outer.add_widget(header)

        tab_row = BoxLayout(orientation="horizontal", spacing=10, size_hint=(0.9, 0.07), pos_hint={"center_x": 0.5, "top": 0.90})
        btn_fav_tab = RoundedButton(text="⭐ Favourites", font_size="14sp",
                                     bg_color=DARK_BLUE if self.view_mode == "fav" else MID_BLUE)
        btn_fav_tab.bind(on_release=lambda x: self.switch_mode("fav"))
        btn_improve_tab = RoundedButton(text="📈 Improve", font_size="14sp",
                                         bg_color=DARK_BLUE if self.view_mode == "improve" else MID_BLUE)
        btn_improve_tab.bind(on_release=lambda x: self.switch_mode("improve"))
        tab_row.add_widget(btn_fav_tab)
        tab_row.add_widget(btn_improve_tab)
        self.outer.add_widget(tab_row)

        current_list = app.favourites if self.view_mode == "fav" else app.improve_questions

        if not current_list:
            empty_text = "No favourite questions yet!" if self.view_mode == "fav" else "No questions in your Improve list yet!"
            lbl = Label(text=empty_text, font_size="18sp", color=TEXT_DARK if app.dark_mode else DARK_BLUE, font_name=MAL_FONT, pos_hint={"center_x": 0.5, "center_y": 0.45})
            self.outer.add_widget(lbl)
            return

        scroll = ScrollView(size_hint=(1, 0.79), pos_hint={"center_x": 0.5, "top": 0.81})
        list_layout = GridLayout(cols=1, spacing=15, size_hint_y=None, padding=[20, 10, 20, 10])
        list_layout.bind(minimum_height=list_layout.setter('height'))

        for idx, item in enumerate(current_list):
            card = BoxLayout(orientation="vertical", size_hint_y=None, height="130dp", spacing=5, padding=[12, 8, 12, 8])
            with card.canvas.before:
                Color(*(DARK_BLUE_CARD if app.dark_mode else LIGHT_BLUE_CARD))
                RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
            card.bind(pos=lambda inst, val: setattr(inst.canvas.before.children[-1], 'pos', val),
                      size=lambda inst, val: setattr(inst.canvas.before.children[-1], 'size', val))

            lbl_q = Label(text=f"Q{idx+1}: {item['question']}", font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else DARK_BLUE, size_hint_y=0.5, bold=True, halign="left", valign="top")
            lbl_q.bind(size=lambda *a, l=lbl_q: setattr(l, "text_size", (l.width, None)))

            lbl_a = Label(text=f"Ans: {item['answer']}", font_name=MAL_FONT, color=GREEN, size_hint_y=0.3, halign="left", valign="middle")
            lbl_a.bind(size=lambda *a, l=lbl_a: setattr(l, "text_size", (l.width, None)))

            remove_btn = RoundedButton(text="❌ Remove", bg_color=RED, size_hint_y=0.3)
            remove_btn.bind(on_release=lambda inst, q=item: self.remove_item(q))

            card.add_widget(lbl_q)
            card.add_widget(lbl_a)
            card.add_widget(remove_btn)
            list_layout.add_widget(card)

        scroll.add_widget(list_layout)
        self.outer.add_widget(scroll)

    def switch_mode(self, mode):
        self.view_mode = mode
        self.load_fav_list()

    def remove_item(self, q_data):
        app = App.get_running_app()
        if self.view_mode == "fav":
            app.toggle_favourite(q_data)
        else:
            app.remove_from_improve(q_data)
        self.load_fav_list()


class AddQuestionScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer = FloatLayout()
        self.add_widget(self.outer)
        self.bind(on_enter=self.build_form)

    def build_form(self, *args):
        self.outer.clear_widgets()
        app = App.get_running_app()
        lang = app.lang

        header = BoxLayout(size_hint=(1, 0.08), pos_hint={"top": 1}, padding=[10, 10, 10, 10])
        back_btn = RoundedButton(text="<", size_hint=(0.15, 1), font_size="20sp")
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back_btn)
        header.add_widget(Label(text=LANG_DATA[lang]["add_q"], font_size="22sp", bold=True, font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.outer.add_widget(header)

        scroll = ScrollView(size_hint=(1, 0.9), pos_hint={"center_x": 0.5, "y": 0})
        form = GridLayout(cols=1, spacing=10, padding=[25, 10, 25, 10], size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        form.add_widget(FieldLabel(text="Question", color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.question_input = TextInput(hint_text="Type question", multiline=True, size_hint_y=None, height="80dp", font_name=MAL_FONT)
        form.add_widget(self.question_input)

        form.add_widget(FieldLabel(text="Answer", color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.answer_input = TextInput(hint_text="Type answer", multiline=True, size_hint_y=None, height="60dp", font_name=MAL_FONT)
        form.add_widget(self.answer_input)

        form.add_widget(FieldLabel(text="Topic", color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.topic_input = Spinner(text="History", values=["History", "Geography", "Constitution", "GK"], size_hint_y=None, height="44dp", font_name=MAL_FONT)
        form.add_widget(self.topic_input)

        form.add_widget(FieldLabel(text="Category", color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.category_input = Spinner(text="GK", values=["GK", "Special Topic"], size_hint_y=None, height="44dp", font_name=MAL_FONT)
        form.add_widget(self.category_input)

        self.status_label = Label(text="", font_name=MAL_FONT, color=(0, 0.6, 0, 1), size_hint_y=None, height="30dp")
        form.add_widget(self.status_label)

        save_btn = RoundedButton(text=LANG_DATA[lang]["save"], font_size="20sp", size_hint_y=None, height="50dp", bg_color=MID_BLUE)
        save_btn.bind(on_release=self.save_question)
        form.add_widget(save_btn)

        scroll.add_widget(form)
        self.outer.add_widget(scroll)

    def save_question(self, *args):
        q_txt = self.question_input.text.strip()
        a_txt = self.answer_input.text.strip()
        if not q_txt:
            return
        
        entry = {
            "question": q_txt, 
            "answer": a_txt, 
            "topic": self.topic_input.text, 
            "category": self.category_input.text
        }
        app = App.get_running_app()
        app.add_question(entry)
        
        # ===================================================================
        # ADDED: Automatically sync "Special Topic" items into Favourites (`favourites.json`)
        # ===================================================================
        if entry["category"] == "Special Topic":
            if not app.is_favourited(entry):
                app.toggle_favourite(entry)

        self.question_input.text = ""
        self.answer_input.text = ""
        self.status_label.text = "Saved successfully!"


class SettingsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer = FloatLayout()
        self.add_widget(self.outer)
        self.bind(on_enter=self.load_settings_view)

    def load_settings_view(self, *args):
        self.outer.clear_widgets()
        app = App.get_running_app()
        lang = app.lang

        header = BoxLayout(size_hint=(1, 0.08), pos_hint={"top": 1}, padding=[10, 10, 10, 10])
        back_btn = RoundedButton(text="<", size_hint=(0.15, 1), font_size="20sp")
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back_btn)
        header.add_widget(Label(text=LANG_DATA[lang]["settings"], font_size="22sp", bold=True, font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else DARK_BLUE))
        self.outer.add_widget(header)

        scroll = ScrollView(size_hint=(1, 0.9), pos_hint={"center_x": 0.5, "y": 0})
        container = GridLayout(cols=1, spacing=20, padding=[20, 15, 20, 15], size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))

        dark_box = BoxLayout(orientation="horizontal", size_hint_y=None, height="50dp", padding=[5, 5, 5, 5])
        lbl_dm = Label(text=LANG_DATA[lang]["dark_mode"], font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else TEXT_LIGHT, font_size="18sp", halign="left", size_hint_x=0.7)
        lbl_dm.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        cb_dm = CheckBox(active=app.dark_mode, size_hint_x=0.3)
        cb_dm.bind(active=self.toggle_dark_mode)
        dark_box.add_widget(lbl_dm)
        dark_box.add_widget(cb_dm)
        container.add_widget(dark_box)

        lang_box = BoxLayout(orientation="horizontal", size_hint_y=None, height="50dp", padding=[5, 5, 5, 5])
        lbl_lang = Label(text=LANG_DATA[lang]["lang"], font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else TEXT_LIGHT, font_size="18sp", halign="left", size_hint_x=0.5)
        lbl_lang.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        sp_lang = Spinner(text=app.lang, values=["English", "Malayalam"], size_hint_x=0.5, font_name=MAL_FONT)
        sp_lang.bind(text=self.change_app_language)
        lang_box.add_widget(lbl_lang)
        lang_box.add_widget(sp_lang)
        container.add_widget(lang_box)

        container.add_widget(Label(text="--------------------------------------------------", color=(0.5,0.5,0.5,1), size_hint_y=None, height="15dp"))

        stats_lbl = Label(text=f"{LANG_DATA[lang]['q_count']}  [b]{len(app.questions)}[/b]", markup=True, font_name=MAL_FONT, color=GREEN if app.dark_mode else DARK_BLUE, font_size="20sp", size_hint_y=None, height="40dp", halign="center")
        container.add_widget(stats_lbl)

        list_hdr = Label(text=LANG_DATA[lang]["saved_list_lbl"], font_name=MAL_FONT, bold=True, color=TEXT_DARK if app.dark_mode else DARK_BLUE, font_size="16sp", size_hint_y=None, height="30dp", halign="left")
        list_hdr.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        container.add_widget(list_hdr)

        if not app.questions:
            container.add_widget(Label(text=LANG_DATA[lang]["no_qs"], font_name=MAL_FONT, color=(0.6,0.6,0.6,1), size_hint_y=None, height="40dp"))
        else:
            for idx, item in enumerate(app.questions):
                card = BoxLayout(orientation="vertical", size_hint_y=None, height="135dp", spacing=5, padding=[12, 8, 12, 8])
                with card.canvas.before:
                    Color(*(DARK_BLUE_CARD if app.dark_mode else LIGHT_BLUE_CARD))
                    RoundedRectangle(pos=card.pos, size=card.size, radius=[10])
                card.bind(pos=lambda inst, val: setattr(inst.canvas.before.children[-1], 'pos', val),
                          size=lambda inst, val: setattr(inst.canvas.before.children[-1], 'size', val))

                lbl_q = Label(text=f"Q{idx+1}: {item['question']}", font_name=MAL_FONT, color=TEXT_DARK if app.dark_mode else DARK_BLUE, bold=True, font_size="15sp", halign="left", valign="top", size_hint_y=0.45)
                lbl_q.bind(size=lambda *a, l=lbl_q: setattr(l, "text_size", (l.width, None)))
                lbl_a = Label(text=f"A: {item['answer']}", font_name=MAL_FONT, color=GREEN, font_size="13sp", halign="left", valign="middle", size_hint_y=0.25)
                lbl_a.bind(size=lambda *a, l=lbl_a: setattr(l, "text_size", (l.width, None)))

                card.add_widget(lbl_q)
                card.add_widget(lbl_a)

                btn_row = BoxLayout(orientation="horizontal", size_hint_y=0.3, spacing=10)

                is_fav = app.is_favourited(item)
                fav_text = "⭐ Favorited" if is_fav else "⭐ Favorite"
                fav_btn = RoundedButton(text=fav_text, bg_color=YELLOW if is_fav else MID_BLUE, size_hint_x=0.6)
                fav_btn.bind(on_release=lambda inst, q=item: self.toggle_fav_settings(q, inst))

                del_icon_btn = RoundedButton(text="🗑️", bg_color=RED, size_hint_x=0.4)
                del_icon_btn.bind(on_release=lambda inst, q=item: self.delete_question_and_refresh(q))

                btn_row.add_widget(fav_btn)
                btn_row.add_widget(del_icon_btn)
                card.add_widget(btn_row)

                container.add_widget(card)

        scroll.add_widget(container)
        self.outer.add_widget(scroll)

    def toggle_dark_mode(self, checkbox, value):
        app = App.get_running_app()
        app.dark_mode = value
        app.save_settings_state()
        self.load_settings_view()

    def change_app_language(self, spinner, value):
        app = App.get_running_app()
        app.lang = value
        app.save_settings_state()
        self.load_settings_view()

    def toggle_fav_settings(self, q_data, btn_inst):
        app = App.get_running_app()
        app.toggle_favourite(q_data)
        if app.is_favourited(q_data):
            btn_inst.text = "⭐ Favorited"
            btn_inst.change_color(YELLOW)
        else:
            btn_inst.text = "⭐ Favorite"
            btn_inst.change_color(MID_BLUE)

    def delete_question_and_refresh(self, q_data):
        app = App.get_running_app()
        app.remove_question(q_data)
        self.load_settings_view()


class MyPSCApp(App):
    def build(self):
        Window.clearcolor = LIGHT_BG

        self.data_file = os.path.join(self.user_data_dir, "questions.json")
        self.fav_file = os.path.join(self.user_data_dir, "favourites.json")
        self.improve_file = os.path.join(self.user_data_dir, "improve.json")
        self.cfg_file = os.path.join(self.user_data_dir, "config.json")

        self.questions = self.load_data(self.data_file)
        self.favourites = self.load_data(self.fav_file)
        self.improve_questions = self.load_data(self.improve_file)

        config = self.load_data(self.cfg_file)
        self.dark_mode = config.get("dark_mode", False) if isinstance(config, dict) else False
        self.lang = config.get("lang", "English") if isinstance(config, dict) else "English"

        Window.clearcolor = DARK_BG if self.dark_mode else LIGHT_BG

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(PracticeScreen(name="practice"))
        sm.add_widget(SelfStudyScreen(name="self_study"))
        sm.add_widget(McqPracticeScreen(name="mcq_practice"))
        sm.add_widget(MockTestScreen(name="mock_test"))
        sm.add_widget(MockExamScreen(name="mock_exam"))
        sm.add_widget(AddQuestionScreen(name="add_question"))
        sm.add_widget(FavouriteViewScreen(name="favourite_view"))
        sm.add_widget(SettingsScreen(name="settings_screen"))
        return sm

    def load_data(self, filepath):
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {} if "config" in filepath else []
        return {} if "config" in filepath else []

    def save_all_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=2)
        with open(self.fav_file, "w", encoding="utf-8") as f:
            json.dump(self.favourites, f, ensure_ascii=False, indent=2)
        with open(self.improve_file, "w", encoding="utf-8") as f:
            json.dump(self.improve_questions, f, ensure_ascii=False, indent=2)

    def save_settings_state(self):
        with open(self.cfg_file, "w", encoding="utf-8") as f:
            json.dump({"dark_mode": self.dark_mode, "lang": self.lang}, f, ensure_ascii=False, indent=2)

    def add_question(self, entry):
        self.questions.append(entry)
        self.save_all_data()

    def remove_question(self, entry):
        self.questions = [q for q in self.questions if q['question'] != entry['question']]
        self.favourites = [f for f in self.favourites if f['question'] != entry['question']]
        self.improve_questions = [i for i in self.improve_questions if i['question'] != entry['question']]
        self.save_all_data()

    def is_favourited(self, entry):
        return any(f['question'] == entry['question'] for f in self.favourites)

    def toggle_favourite(self, entry):
        if self.is_favourited(entry):
            self.favourites = [f for f in self.favourites if f['question'] != entry['question']]
        else:
            self.favourites.append(entry)
        self.save_all_data()

    def add_to_improve(self, entry):
        if not any(i['question'] == entry['question'] for i in self.improve_questions):
            self.improve_questions.append(entry)
            self.save_all_data()

    def remove_from_improve(self, entry):
        self.improve_questions = [i for i in self.improve_questions if i['question'] != entry['question']]
        self.save_all_data()


if __name__ == "__main__":
    MyPSCApp().run()
