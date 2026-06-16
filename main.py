import os
import tempfile
from datetime import datetime, timedelta
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.progressbar import MDProgressBar
from ultralytics import YOLO
import cv2
import numpy as np

Window.size = (360, 640)

try:
    from plyer import notification, filechooser
    NOTIF_AVAILABLE = True
    FILECHOOSER_AVAILABLE = True
except ImportError:
    NOTIF_AVAILABLE = False
    FILECHOOSER_AVAILABLE = False

# ── Palette sobre ──────────────────────────────────────────────────────────────
# Vert : #3a7d44  (moins saturé que le précédent #2e7d32)
# Bleu  : #3a5f8a
# Fond  : #f5f5f5
# Carte : #ffffff  bordure #e8e8e8
# Texte secondaire : #757575
# Accent aujourd'hui : #e8a020  (ambre doux, non agressif)
# ───────────────────────────────────────────────────────────────────────────────

KV = '''
ScreenManager:
    CameraScreen:
    ResultScreen:
    CalendarScreen:

# ══════════════════════════════════════════════════════
#  ÉCRAN PRINCIPAL
# ══════════════════════════════════════════════════════
<CameraScreen>:
    name: 'camera'

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.961, 0.961, 0.961, 1

        MDTopAppBar:
            title: "Mbabu Scan"
            elevation: 0
            md_bg_color: 0.227, 0.490, 0.267, 1
            specific_text_color: 1, 1, 1, 1
            right_action_items: [["refresh", lambda x: app.reset_counts()]]
            left_action_items: [["menu", lambda x: None]]

        ScrollView:
            do_scroll_x: False

            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: [16, 16, 16, 24]
                spacing: 12

                # ── Carte Hero ──────────────────────────────
                MDCard:
                    size_hint_y: None
                    height: 84
                    radius: [14]
                    elevation: 0
                    md_bg_color: 1, 1, 1, 1
                    line_color: 0.910, 0.910, 0.910, 1

                    MDBoxLayout:
                        orientation: 'horizontal'
                        padding: [14, 0, 14, 0]
                        spacing: 12

                        MDBoxLayout:
                            size_hint: None, None
                            size: 44, 44
                            md_bg_color: 0.918, 0.961, 0.918, 1
                            radius: [10]
                            MDIcon:
                                icon: "bug-outline"
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: 0.227, 0.490, 0.267, 1
                                font_size: "22sp"
                                pos_hint: {"center_y": 0.5}

                        MDBoxLayout:
                            orientation: 'vertical'
                            padding: [0, 16, 0, 16]
                            spacing: 2

                            MDLabel:
                                text: "Identification par IA"
                                font_style: "Subtitle2"
                                bold: True
                                theme_text_color: "Primary"
                                size_hint_y: None
                                height: self.texture_size[1]

                            MDLabel:
                                text: "Analysez un charançon mposé via photo"
                                font_style: "Caption"
                                theme_text_color: "Secondary"
                                size_hint_y: None
                                height: self.texture_size[1]

                # ── Compteurs ───────────────────────────────
                MDBoxLayout:
                    adaptive_height: True
                    spacing: 10

                    MDCard:
                        size_hint: 0.5, None
                        height: 96
                        radius: [14]
                        elevation: 0
                        md_bg_color: 1, 1, 1, 1
                        line_color: 0.910, 0.910, 0.910, 1

                        MDBoxLayout:
                            orientation: 'vertical'
                            padding: [14, 12, 14, 12]
                            spacing: 2

                            MDBoxLayout:
                                adaptive_height: True
                                spacing: 5
                                size_hint_y: None
                                height: 20

                                MDIcon:
                                    icon: "gender-male"
                                    theme_text_color: "Custom"
                                    text_color: 0.227, 0.490, 0.267, 1
                                    font_size: "15sp"
                                    size_hint: None, None
                                    size: 18, 18

                                MDLabel:
                                    text: "Mâles"
                                    font_style: "Caption"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: self.texture_size[1]

                            MDLabel:
                                text: str(app.male_count)
                                font_style: "H4"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 0.227, 0.490, 0.267, 1
                                size_hint_y: 1

                            MDLabel:
                                text: "scans"
                                font_style: "Caption"
                                theme_text_color: "Hint"
                                size_hint_y: None
                                height: self.texture_size[1]

                    MDCard:
                        size_hint: 0.5, None
                        height: 96
                        radius: [14]
                        elevation: 0
                        md_bg_color: 1, 1, 1, 1
                        line_color: 0.910, 0.910, 0.910, 1

                        MDBoxLayout:
                            orientation: 'vertical'
                            padding: [14, 12, 14, 12]
                            spacing: 2

                            MDBoxLayout:
                                adaptive_height: True
                                spacing: 5
                                size_hint_y: None
                                height: 20

                                MDIcon:
                                    icon: "gender-female"
                                    theme_text_color: "Custom"
                                    text_color: 0.690, 0.400, 0.110, 1
                                    font_size: "15sp"
                                    size_hint: None, None
                                    size: 18, 18

                                MDLabel:
                                    text: "Femelles"
                                    font_style: "Caption"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: self.texture_size[1]

                            MDLabel:
                                text: str(app.female_count)
                                font_style: "H4"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 0.690, 0.400, 0.110, 1
                                size_hint_y: 1

                            MDLabel:
                                text: "scans"
                                font_style: "Caption"
                                theme_text_color: "Hint"
                                size_hint_y: None
                                height: self.texture_size[1]

                # ── Boutons d'action ────────────────────────
                MDCard:
                    size_hint_y: None
                    height: 72
                    radius: [14]
                    elevation: 0
                    md_bg_color: 0.227, 0.490, 0.267, 1
                    on_release: app.open_camera_or_gallery()

                    MDBoxLayout:
                        orientation: 'horizontal'
                        padding: [18, 0, 18, 0]
                        spacing: 14

                        MDIcon:
                            icon: "camera-outline"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            font_size: "26sp"
                            size_hint: None, None
                            size: 32, 32
                            pos_hint: {"center_y": 0.5}

                        MDBoxLayout:
                            orientation: 'vertical'
                            padding: [0, 14, 0, 14]
                            spacing: 1

                            MDLabel:
                                text: "Prendre ou choisir une photo"
                                font_style: "Subtitle2"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1
                                size_hint_y: None
                                height: self.texture_size[1]

                            MDLabel:
                                text: "Appareil photo · Galerie"
                                font_style: "Caption"
                                theme_text_color: "Custom"
                                text_color: 0.84, 0.95, 0.84, 1
                                size_hint_y: None
                                height: self.texture_size[1]

                        MDIcon:
                            icon: "chevron-right"
                            theme_text_color: "Custom"
                            text_color: 0.84, 0.95, 0.84, 1
                            font_size: "20sp"
                            size_hint: None, None
                            size: 24, 24
                            pos_hint: {"center_y": 0.5}

                MDCard:
                    size_hint_y: None
                    height: 56
                    radius: [14]
                    elevation: 0
                    md_bg_color: 1, 1, 1, 1
                    line_color: 0.227, 0.490, 0.267, 1
                    on_release: app.load_calendar()

                    MDBoxLayout:
                        orientation: 'horizontal'
                        padding: [18, 0, 18, 0]
                        spacing: 14

                        MDIcon:
                            icon: "calendar-month-outline"
                            theme_text_color: "Custom"
                            text_color: 0.227, 0.490, 0.267, 1
                            font_size: "20sp"
                            size_hint: None, None
                            size: 24, 24
                            pos_hint: {"center_y": 0.5}

                        MDLabel:
                            text: "Calendrier de production"
                            font_style: "Button"
                            theme_text_color: "Custom"
                            text_color: 0.227, 0.490, 0.267, 1
                            size_hint_y: None
                            height: self.texture_size[1]
                            pos_hint: {"center_y": 0.5}

                        MDIcon:
                            icon: "chevron-right"
                            theme_text_color: "Custom"
                            text_color: 0.680, 0.680, 0.680, 1
                            font_size: "18sp"
                            size_hint: None, None
                            size: 20, 20
                            pos_hint: {"center_y": 0.5}

                # ── Conseils ────────────────────────────────
                MDLabel:
                    text: "CONSEILS DE SCAN"
                    font_style: "Overline"
                    theme_text_color: "Hint"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDCard:
                    size_hint_y: None
                    height: 176
                    radius: [14]
                    elevation: 0
                    md_bg_color: 1, 1, 1, 1
                    line_color: 0.910, 0.910, 0.910, 1

                    MDBoxLayout:
                        orientation: 'vertical'
                        padding: [14, 14, 14, 14]
                        spacing: 10

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: 10
                            MDIcon:
                                icon: "crop-free"
                                theme_text_color: "Custom"
                                text_color: 0.227, 0.490, 0.267, 1
                                font_size: "17sp"
                                size_hint: None, None
                                size: 20, 20
                            MDLabel:
                                text: "Photo de profil pour une détection précise"
                                font_style: "Caption"
                                theme_text_color: "Secondary"
                                size_hint_y: None
                                height: self.texture_size[1]

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: 10
                            MDIcon:
                                icon: "white-balance-sunny"
                                theme_text_color: "Custom"
                                text_color: 0.227, 0.490, 0.267, 1
                                font_size: "17sp"
                                size_hint: None, None
                                size: 20, 20
                            MDLabel:
                                text: "Lumière naturelle, sans ombres dures"
                                font_style: "Caption"
                                theme_text_color: "Secondary"
                                size_hint_y: None
                                height: self.texture_size[1]

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: 10
                            MDIcon:
                                icon: "focus-field"
                                theme_text_color: "Custom"
                                text_color: 0.227, 0.490, 0.267, 1
                                font_size: "17sp"
                                size_hint: None, None
                                size: 20, 20
                            MDLabel:
                                text: "Appareil stable et bien mis au point"
                                font_style: "Caption"
                                theme_text_color: "Secondary"
                                size_hint_y: None
                                height: self.texture_size[1]

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: 10
                            MDIcon:
                                icon: "image-filter-center-focus-weak"
                                theme_text_color: "Custom"
                                text_color: 0.227, 0.490, 0.267, 1
                                font_size: "17sp"
                                size_hint: None, None
                                size: 20, 20
                            MDLabel:
                                text: "Fond uni et contrasté"
                                font_style: "Caption"
                                theme_text_color: "Secondary"
                                size_hint_y: None
                                height: self.texture_size[1]

                MDLabel:
                    text: "Mbabu Scan v1.0 · Analyse par réseau de neurones"
                    halign: "center"
                    font_style: "Caption"
                    theme_text_color: "Hint"
                    size_hint_y: None
                    height: 28

# ══════════════════════════════════════════════════════
#  ÉCRAN RÉSULTAT
# ══════════════════════════════════════════════════════
<ResultScreen>:
    name: 'result'

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.961, 0.961, 0.961, 1

        MDTopAppBar:
            title: "Résultat"
            elevation: 0
            md_bg_color: 0.227, 0.490, 0.267, 1
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: app.go_back()]]

        MDBoxLayout:
            orientation: 'vertical'
            padding: [16, 16, 16, 16]
            spacing: 12

            MDCard:
                size_hint_y: None
                height: 200
                radius: [14]
                elevation: 0
                md_bg_color: 0.08, 0.08, 0.08, 1
                FitImage:
                    id: result_image
                    radius: [14]

            MDCard:
                size_hint_y: None
                height: 130
                radius: [14]
                elevation: 0
                md_bg_color: 1, 1, 1, 1
                line_color: 0.910, 0.910, 0.910, 1

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: [20, 14, 20, 14]
                    spacing: 4

                    MDLabel:
                        text: "RÉSULTAT"
                        halign: "center"
                        font_style: "Overline"
                        theme_text_color: "Hint"
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDLabel:
                        id: result_label
                        text: ""
                        halign: "center"
                        font_style: "H3"
                        bold: True

                    MDLabel:
                        id: confidence_label
                        text: ""
                        halign: "center"
                        font_style: "Caption"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: self.texture_size[1]

            MDCard:
                size_hint_y: None
                height: 130
                radius: [14]
                elevation: 0
                md_bg_color: 1, 1, 1, 1
                line_color: 0.910, 0.910, 0.910, 1

                MDBoxLayout:
                    orientation: 'vertical'
                    padding: [14, 12, 14, 12]
                    spacing: 6

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: 6
                        MDIcon:
                            icon: "chart-bar"
                            theme_text_color: "Custom"
                            text_color: 0.227, 0.490, 0.267, 1
                            font_size: "16sp"
                            size_hint: None, None
                            size: 18, 18
                        MDLabel:
                            text: "Facteurs analysés"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Primary"
                            size_hint_y: None
                            height: self.texture_size[1]

                    MDLabel:
                        id: factor1_label
                        text: ""
                        font_style: "Caption"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDLabel:
                        id: factor2_label
                        text: ""
                        font_style: "Caption"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDLabel:
                        id: factor3_label
                        text: ""
                        font_style: "Caption"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: self.texture_size[1]

            MDCard:
                size_hint_y: None
                height: 56
                radius: [14]
                elevation: 0
                md_bg_color: 0.227, 0.490, 0.267, 1
                on_release: app.open_camera_or_gallery()

                MDBoxLayout:
                    orientation: 'horizontal'
                    padding: [18, 0, 18, 0]
                    spacing: 12

                    MDIcon:
                        icon: "camera-outline"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_size: "20sp"
                        size_hint: None, None
                        size: 24, 24
                        pos_hint: {"center_y": 0.5}

                    MDLabel:
                        text: "Nouveau scan"
                        font_style: "Button"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        size_hint_y: None
                        height: self.texture_size[1]
                        pos_hint: {"center_y": 0.5}

# ══════════════════════════════════════════════════════
#  ÉCRAN CALENDRIER
# ══════════════════════════════════════════════════════
<CalendarScreen>:
    name: 'calendar'

    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.961, 0.961, 0.961, 1

        MDTopAppBar:
            title: "Production Mpose"
            elevation: 0
            md_bg_color: 0.227, 0.373, 0.541, 1
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: app.go_home()]]
            right_action_items: [["plus", lambda x: app.add_cycle_dialog()]]

        ScrollView:
            do_scroll_x: False

            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: [16, 16, 16, 24]
                spacing: 12

                # ── Tâches du jour ──────────────────────────
                MDLabel:
                    text: "TÂCHES DU JOUR"
                    font_style: "Overline"
                    theme_text_color: "Hint"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDCard:
                    id: tasks_card
                    size_hint_y: None
                    height: 64
                    radius: [14]
                    elevation: 0
                    md_bg_color: 0.996, 0.980, 0.933, 1
                    line_color: 0.910, 0.816, 0.612, 1

                    MDBoxLayout:
                        orientation: 'horizontal'
                        padding: [14, 0, 14, 0]
                        spacing: 10

                        MDIcon:
                            icon: "bell-outline"
                            theme_text_color: "Custom"
                            text_color: 0.690, 0.500, 0.110, 1
                            font_size: "18sp"
                            size_hint: None, None
                            size: 22, 22
                            pos_hint: {"center_y": 0.5}

                        MDLabel:
                            id: tasks_label
                            text: "Aucune tâche pour aujourd'hui"
                            font_style: "Body2"
                            theme_text_color: "Custom"
                            text_color: 0.420, 0.310, 0.050, 1
                            pos_hint: {"center_y": 0.5}

                # ── Cycles ──────────────────────────────────
                MDLabel:
                    text: "CYCLES ACTIFS"
                    font_style: "Overline"
                    theme_text_color: "Hint"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDBoxLayout:
                    id: calendar_container
                    orientation: "vertical"
                    adaptive_height: True
                    spacing: 10

                # ── Bouton ajouter ──────────────────────────
                MDCard:
                    size_hint_y: None
                    height: 52
                    radius: [14]
                    elevation: 0
                    md_bg_color: 1, 1, 1, 1
                    line_color: 0.227, 0.373, 0.541, 1
                    on_release: app.add_cycle_dialog()

                    MDBoxLayout:
                        orientation: 'horizontal'
                        padding: [18, 0, 18, 0]
                        spacing: 10

                        MDIcon:
                            icon: "plus-circle-outline"
                            theme_text_color: "Custom"
                            text_color: 0.227, 0.373, 0.541, 1
                            font_size: "20sp"
                            size_hint: None, None
                            size: 24, 24
                            pos_hint: {"center_y": 0.5}

                        MDLabel:
                            text: "Ajouter un nouveau cycle"
                            font_style: "Button"
                            theme_text_color: "Custom"
                            text_color: 0.227, 0.373, 0.541, 1
                            size_hint_y: None
                            height: self.texture_size[1]
                            pos_hint: {"center_y": 0.5}

                MDLabel:
                    text: "Rappel automatique la veille de chaque étape"
                    halign: "center"
                    font_style: "Caption"
                    theme_text_color: "Hint"
                    size_hint_y: None
                    height: 28
'''


class CameraScreen(Screen):
    pass


class ResultScreen(Screen):
    pass


class CalendarScreen(Screen):
    pass


# ── Icônes par étape ───────────────────────────────────────────────────────────
STEP_ICONS = {
    "J03": "water-check-outline",
    "J10": "account-remove-outline",
    "J15": "magnify",
    "J20": "food-variant",
    "J25": "trending-up",
    "J30": "cart-outline",
    "J35": "check-decagram-outline",
    "J40": "cog-outline",
    "J45": "transfer",
}

# Couleur sobre (vert doux) pour barre de progression et dots
GREEN_SOFT  = (0.227, 0.490, 0.267, 1)
GREEN_DONE  = (0.227, 0.490, 0.267, 1)
AMBER_TODAY = (0.690, 0.500, 0.110, 1)
GRAY_FUTURE = (0.780, 0.780, 0.780, 1)
WHITE       = (1, 1, 1, 1)
CARD_BORDER = (0.910, 0.910, 0.910, 1)


class CharanconApp(MDApp):
    male_count   = NumericProperty(0)
    female_count = NumericProperty(0)

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style     = "Light"
        self.theme_cls.material_style  = "M3"
        self.file_manager = None

        self.store = JsonStore("production.json")
        if not self.store.exists("cycles"):
            self.store.put("cycles", data=[])

        self.load_counts()

        Clock.schedule_interval(lambda dt: self.check_notifications(), 3600)
        Clock.schedule_once(lambda dt: self.check_notifications(), 10)

        try:
            self.model = YOLO('best.pt')
            print("Modèle chargé")
        except Exception as e:
            print(f"Modèle non chargé : {e}")
            self.model = None

        return Builder.load_string(KV)

    # ── Compteurs ──────────────────────────────────────────────────────────────

    def load_counts(self):
        if self.store.exists("counts"):
            d = self.store.get("counts")
            self.male_count   = d.get("male", 0)
            self.female_count = d.get("female", 0)

    def save_counts(self):
        self.store.put("counts", male=self.male_count, female=self.female_count)

    def reset_counts(self, *args):
        self.male_count = self.female_count = 0
        self.save_counts()

    # ── Navigation ─────────────────────────────────────────────────────────────

    def go_back(self):
        self.root.current = 'camera'

    def go_home(self):
        self.root.current = 'camera'

    # ── Ouverture appareil photo / galerie ─────────────────────────────────────

    def open_camera_or_gallery(self):
        """
        Sur Android/iOS : utilise plyer.filechooser pour ouvrir l'appareil photo
        ou la galerie nativement.
        Sur desktop (dev) : fallback vers le gestionnaire de fichiers KivyMD.
        """
        if FILECHOOSER_AVAILABLE:
            try:
                filechooser.open_file(
                    on_selection=self._on_filechooser_selection,
                    filters=["*.jpg", "*.jpeg", "*.png"],
                    use_camera=False,   # mettre True pour forcer l'appareil photo
                )
                return
            except Exception as e:
                print(f"filechooser non disponible : {e}")
        # Fallback desktop
        self._open_file_manager_fallback()

    def _on_filechooser_selection(self, selection):
        if not selection:
            return
        path = selection[0]
        try:
            with open(path, 'rb') as f:
                self.analyze(f.read())
        except Exception as e:
            self.show_error(f"Erreur chargement : {e}")

    def _open_file_manager_fallback(self):
        self.file_manager = MDFileManager(
            exit_manager=self._exit_file_manager,
            select_path=self._select_path_fallback,
            preview=True,
        )
        self.file_manager.show(os.path.expanduser("~/Pictures"))

    def _exit_file_manager(self, *args):
        if self.file_manager:
            self.file_manager.close()

    def _select_path_fallback(self, path):
        self._exit_file_manager()
        try:
            with open(path, 'rb') as f:
                self.analyze(f.read())
        except Exception as e:
            self.show_error(f"Erreur chargement : {e}")

    # ── Planning ───────────────────────────────────────────────────────────────

    def generate_schedule(self, start_date):
        offsets = {"J03": 3, "J10": 10, "J15": 15, "J20": 20,
                   "J25": 25, "J30": 30, "J35": 35, "J40": 40, "J45": 45}
        return {k: start_date + timedelta(days=v) for k, v in offsets.items()}

    def get_actions_dict(self):
        return {
            "J03": "Contrôle humidité",
            "J10": "Retrait géniteurs",
            "J15": "Contrôle croissance",
            "J20": "Contrôle alimentation",
            "J25": "Engraissement",
            "J30": "Récolte / Vente",
            "J35": "Contrôle qualité",
            "J40": "Préparation transformation",
            "J45": "Transformation géniteurs",
        }

    def get_current_step(self, planning):
        now = datetime.now()
        for step, date in planning.items():
            if now < date:
                return step
        return "Terminé"

    def get_progress(self, start_date):
        days_elapsed = (datetime.now() - start_date).days
        return min(100, max(0, int(days_elapsed / 45 * 100)))

    # ── Calendrier ─────────────────────────────────────────────────────────────

    def load_calendar(self):
        self.root.current = "calendar"
        container = self.root.get_screen("calendar").ids.calendar_container
        container.clear_widgets()

        cycles       = self.store.get("cycles")["data"]
        actions_dict = self.get_actions_dict()

        if not cycles:
            empty = MDCard(
                orientation="vertical",
                adaptive_height=True,
                padding="20dp",
                radius=[14],
                md_bg_color=WHITE,
                elevation=0,
                line_color=CARD_BORDER,
            )
            empty.add_widget(MDLabel(
                text="Aucun cycle.\nAppuyez sur  +  pour en créer un.",
                halign="center",
                theme_text_color="Secondary",
                font_style="Body2",
            ))
            container.add_widget(empty)
        else:
            for idx, cycle in enumerate(cycles):
                start        = datetime.strptime(cycle["date"], "%d/%m/%Y")
                planning     = self.generate_schedule(start)
                progress     = self.get_progress(start)
                current_step = self.get_current_step(planning)
                end_date     = planning["J45"].strftime("%d/%m/%Y")

                card = MDCard(
                    orientation="vertical",
                    adaptive_height=True,
                    radius=[14],
                    elevation=0,
                    md_bg_color=WHITE,
                    line_color=CARD_BORDER,
                )

                # ── En-tête du cycle ────────────────────────
                header = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=64,
                    padding=[14, 0, 14, 0],
                    spacing=10,
                )

                icon_box = MDBoxLayout(
                    size_hint=(None, None),
                    size=(38, 38),
                    radius=[10],
                )
                icon_box.md_bg_color = (0.910, 0.941, 0.910, 1)
                icon_lbl = MDIcon(
                    icon="sprout",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=GREEN_SOFT,
                    font_size="20sp",
                )
                icon_box.add_widget(icon_lbl)

                info_box = MDBoxLayout(orientation="vertical", spacing=2,
                                       padding=[0, 12, 0, 12])
                info_box.add_widget(MDLabel(
                    text=f"Mise en bac : {cycle['date']}",
                    font_style="Subtitle2", bold=True,
                    theme_text_color="Primary",
                    size_hint_y=None, height=22,
                ))
                info_box.add_widget(MDLabel(
                    text=f"{cycle['bacs']} bac{'s' if cycle['bacs'] > 1 else ''}  ·  Fin : {end_date}",
                    font_style="Caption",
                    theme_text_color="Secondary",
                    size_hint_y=None, height=18,
                ))

                badge = MDLabel(
                    text=current_step if current_step == "Terminé" else "En cours",
                    font_style="Caption",
                    size_hint=(None, None),
                    size=(72, 24),
                )
                badge.bold = True
                if current_step == "Terminé":
                    badge.theme_text_color = "Custom"
                    badge.text_color = (0.400, 0.400, 0.400, 1)
                else:
                    badge.theme_text_color = "Custom"
                    badge.text_color = GREEN_SOFT

                header.add_widget(icon_box)
                header.add_widget(info_box)
                header.add_widget(badge)
                card.add_widget(header)

                # ── Séparateur ──────────────────────────────
                sep = MDBoxLayout(size_hint_y=None, height=1,
                                  md_bg_color=CARD_BORDER)
                card.add_widget(sep)

                # ── Barre de progression ────────────────────
                prog_box = MDBoxLayout(
                    orientation="vertical",
                    size_hint_y=None, height=52,
                    padding=[14, 10, 14, 10], spacing=6,
                )
                prog_row = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None, height=16,
                )
                prog_row.add_widget(MDLabel(
                    text="Progression",
                    font_style="Caption",
                    theme_text_color="Hint",
                    size_hint_y=None, height=16,
                ))
                prog_row.add_widget(MDLabel(
                    text=f"{progress} %",
                    font_style="Caption",
                    bold=True,
                    halign="right",
                    theme_text_color="Custom",
                    text_color=GREEN_SOFT,
                    size_hint_y=None, height=16,
                ))
                prog_box.add_widget(prog_row)

                bar = MDProgressBar(
                    value=progress,
                    size_hint_y=None, height=6,
                )
                bar.color = GREEN_SOFT
                prog_box.add_widget(bar)
                card.add_widget(prog_box)

                # ── Séparateur ──────────────────────────────
                card.add_widget(MDBoxLayout(size_hint_y=None, height=1,
                                            md_bg_color=CARD_BORDER))

                # ── Timeline des étapes ─────────────────────
                steps_box = MDBoxLayout(
                    orientation="vertical",
                    adaptive_height=True,
                    padding=[14, 10, 14, 10],
                    spacing=4,
                )

                today = datetime.now().date()
                for step, date in planning.items():
                    action    = actions_dict.get(step, step)
                    date_str  = date.strftime("%d/%m")
                    is_done   = date.date() < today
                    is_today  = date.date() == today
                    step_icon = STEP_ICONS.get(step, "circle-small")

                    row = MDBoxLayout(
                        orientation="horizontal",
                        size_hint_y=None, height=34,
                        spacing=10,
                    )

                    # Icône de statut
                    if is_done:
                        status_icon = MDIcon(
                            icon="check-circle-outline",
                            theme_text_color="Custom",
                            text_color=GREEN_DONE,
                            font_size="16sp",
                            size_hint=(None, None), size=(20, 20),
                        )
                    elif is_today:
                        status_icon = MDIcon(
                            icon="circle-slice-8",
                            theme_text_color="Custom",
                            text_color=AMBER_TODAY,
                            font_size="16sp",
                            size_hint=(None, None), size=(20, 20),
                        )
                    else:
                        status_icon = MDIcon(
                            icon="circle-outline",
                            theme_text_color="Custom",
                            text_color=GRAY_FUTURE,
                            font_size="16sp",
                            size_hint=(None, None), size=(20, 20),
                        )

                    # Icône de l'action
                    action_icon = MDIcon(
                        icon=step_icon,
                        theme_text_color="Custom",
                        text_color=(
                            GREEN_DONE if is_done else
                            AMBER_TODAY if is_today else
                            GRAY_FUTURE
                        ),
                        font_size="15sp",
                        size_hint=(None, None), size=(18, 18),
                    )

                    # Label du step (J03…)
                    step_lbl = MDLabel(
                        text=step,
                        font_style="Caption",
                        bold=is_today,
                        size_hint=(None, None), size=(32, 34),
                        theme_text_color="Custom",
                        text_color=(
                            (0.300, 0.300, 0.300, 1) if is_done else
                            AMBER_TODAY if is_today else
                            GRAY_FUTURE
                        ),
                    )

                    # Label de l'action
                    action_lbl = MDLabel(
                        text=f"{action}  ←  Aujourd'hui" if is_today else action,
                        font_style="Caption",
                        bold=is_today,
                        theme_text_color="Custom",
                        text_color=(
                            (0.300, 0.300, 0.300, 1) if is_done else
                            AMBER_TODAY if is_today else
                            (0.420, 0.420, 0.420, 1)
                        ),
                        size_hint_y=None, height=34,
                    )

                    # Date à droite
                    date_lbl = MDLabel(
                        text=date_str,
                        font_style="Caption",
                        halign="right",
                        theme_text_color="Hint",
                        size_hint=(None, None), size=(40, 34),
                    )

                    row.add_widget(status_icon)
                    row.add_widget(action_icon)
                    row.add_widget(step_lbl)
                    row.add_widget(action_lbl)
                    row.add_widget(date_lbl)
                    steps_box.add_widget(row)

                card.add_widget(steps_box)

                # ── Pied : bouton supprimer ─────────────────
                card.add_widget(MDBoxLayout(size_hint_y=None, height=1,
                                            md_bg_color=CARD_BORDER))

                footer = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None, height=42,
                    padding=[10, 0, 10, 0],
                )
                del_btn = MDFlatButton(
                    text="Supprimer ce cycle",
                    theme_text_color="Custom",
                    text_color=(0.700, 0.200, 0.200, 1),
                    size_hint=(None, None),
                    size=(200, 42),
                )
                del_btn.bind(on_release=lambda x, i=idx: self.delete_cycle(i))
                footer.add_widget(del_btn)
                card.add_widget(footer)

                container.add_widget(card)

        self.update_today_tasks()

    def delete_cycle(self, idx):
        cycles = self.store.get("cycles")["data"]
        if 0 <= idx < len(cycles):
            cycles.pop(idx)
            self.store.put("cycles", data=cycles)
            self.load_calendar()

    def update_today_tasks(self):
        today        = datetime.now().date()
        cycles       = self.store.get("cycles")["data"]
        actions_dict = self.get_actions_dict()
        tasks        = []

        for cycle in cycles:
            start    = datetime.strptime(cycle["date"], "%d/%m/%Y")
            planning = self.generate_schedule(start)
            for step, date in planning.items():
                if date.date() == today:
                    action = actions_dict.get(step, "Contrôle")
                    tasks.append(f"{step} : {action}  (bac du {cycle['date']})")

        lbl = self.root.get_screen("calendar").ids.tasks_label
        lbl.text = "\n".join(tasks) if tasks else "Aucune tâche pour aujourd'hui"

    # ── Notifications ──────────────────────────────────────────────────────────

    def add_cycle_dialog(self):
        content = MDBoxLayout(
            orientation='vertical', spacing='12dp',
            size_hint_y=None, height='160dp', padding='20dp',
        )
        self.date_field = MDTextField(
            hint_text="Date de mise en bac (JJ/MM/AAAA)",
            helper_text="Format : 15/06/2024",
            helper_text_mode="on_focus", mode="rectangle",
        )
        self.bacs_field = MDTextField(
            hint_text="Nombre de bacs",
            helper_text_mode="on_focus", mode="rectangle",
        )
        content.add_widget(self.date_field)
        content.add_widget(self.bacs_field)

        self._cycle_dialog = MDDialog(
            title="Nouveau cycle",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="ANNULER",
                             on_release=lambda x: self._cycle_dialog.dismiss()),
                MDRaisedButton(text="VALIDER",
                               on_release=lambda x: self.save_cycle(self._cycle_dialog)),
            ],
        )
        self._cycle_dialog.open()

    def save_cycle(self, dialog):
        try:
            date_text = self.date_field.text.strip()
            nb_bacs   = int(self.bacs_field.text.strip())
            datetime.strptime(date_text, "%d/%m/%Y")

            cycles = self.store.get("cycles")["data"]
            cycles.append({
                "date": date_text,
                "bacs": nb_bacs,
                "created_at": datetime.now().isoformat(),
            })
            self.store.put("cycles", data=cycles)
            dialog.dismiss()
            self.load_calendar()
        except ValueError:
            self.show_error("Format invalide. Utilisez JJ/MM/AAAA et un entier pour les bacs.")

    def check_notifications(self):
        if not NOTIF_AVAILABLE:
            return
        tomorrow     = datetime.now().date() + timedelta(days=1)
        cycles       = self.store.get("cycles")["data"]
        actions_dict = self.get_actions_dict()
        for cycle in cycles:
            start    = datetime.strptime(cycle["date"], "%d/%m/%Y")
            planning = self.generate_schedule(start)
            for step, date in planning.items():
                if date.date() == tomorrow:
                    action = actions_dict.get(step, "Contrôle")
                    try:
                        notification.notify(
                            title="Production Mpose",
                            message=f"Demain : {action}\nBac du {cycle['date']}",
                            timeout=10,
                        )
                    except Exception:
                        pass

    # ── Analyse IA ─────────────────────────────────────────────────────────────

    def _extract_morphology(self, mask, img):
        try:
            if len(mask.shape) == 3:
                mask = mask[:, :, 0]
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return None, None, None, None
            c = max(contours, key=cv2.contourArea)
            rect = cv2.minAreaRect(c)
            w, h = rect[1]
            if w == 0 or h == 0:
                return None, None, None, None
            longueur = max(w, h)
            largeur  = min(w, h)
            ratio    = longueur / largeur
            M = cv2.moments(c)
            if M["m00"] == 0:
                return None, None, None, None
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            dists = [(np.sqrt((p[0]-cx)**2 + (p[1]-cy)**2), p) for p in c[:, 0, :]]
            if not dists:
                return None, None, None, None
            tip  = max(dists, key=lambda x: x[0])[1]
            size = int(largeur)
            x1 = max(0, int(tip[0]-size)); x2 = min(mask.shape[1], int(tip[0]+size))
            y1 = max(0, int(tip[1]-size)); y2 = min(mask.shape[0], int(tip[1]+size))
            return ratio, mask[y1:y2, x1:x2], img[y1:y2, x1:x2], (c, tip)
        except Exception as e:
            print(f"Erreur morphologie : {e}")
            return None, None, None, None

    def _classify(self, ratio, tip_mask, tip_img):
        ms = fs = 0
        if ratio < 2.8:   ms += 3
        elif ratio > 3.5: fs += 3
        else:             ms += 1; fs += 1

        if tip_img is None or tip_mask is None or tip_img.size == 0:
            return ms, fs

        gray = cv2.cvtColor(tip_img, cv2.COLOR_BGR2GRAY) if len(tip_img.shape) == 3 else tip_img
        px   = tip_mask > 0
        mv   = gray[px]
        if len(mv) == 0:
            return ms, fs

        lap_var = np.var(cv2.Laplacian(gray, cv2.CV_64F)[px]) if len(gray[px]) > 0 else 0
        ms += 1 if lap_var > 40 else 0; fs += 0 if lap_var > 40 else 1

        ed = np.mean(cv2.Canny(gray, 50, 150)[px] > 0) if len(mv) > 0 else 0
        ms += 1 if ed > 0.08 else 0; fs += 0 if ed > 0.08 else 1

        relief = np.std(mv) if len(mv) > 0 else 0
        ms += 1 if relief > 25 else 0; fs += 0 if relief > 25 else 1

        h, w   = tip_mask.shape
        rs     = int(w * 0.8)
        tw     = np.sum(tip_mask[:, rs:] > 0) / h if rs < w and h > 0 else 0
        ms += 1 if tw > 18 else 0; fs += 0 if tw > 18 else 1

        return ms, fs

    def analyze(self, data):
        try:
            bgr = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if bgr is None or self.model is None:
                self.show_error("Impossible de charger l'image ou le modèle.")
                return

            results = self.model(bgr, verbose=False)
            if not results or results[0].masks is None:
                self.show_error("Aucun individu détecté sur la photo.")
                return

            boxes = results[0].boxes
            if boxes is None or len(boxes) == 0:
                self.show_error("Aucune détection exploitable.")
                return

            best_idx = int(boxes.conf.argmax())
            mask = results[0].masks.data[best_idx].cpu().numpy()
            mask = cv2.resize(mask, (bgr.shape[1], bgr.shape[0]),
                              interpolation=cv2.INTER_NEAREST)
            mask = (mask > 0.5).astype(np.uint8) * 255

            ratio, tip_mask, tip_img, _ = self._extract_morphology(mask, bgr)
            if ratio is None:
                self.show_error("Analyse impossible sur cette image.")
                return

            ms, fs = self._classify(ratio, tip_mask, tip_img)

            if ms > fs:
                sexe = "MÂLE";    color = GREEN_SOFT;              cv_c = (47, 125, 47)
                self.male_count  += 1; conf = 85
                f1, f2, f3 = "• Morphologie compacte détectée", "• Texture de surface : structurée", "• Forme générale : court et large"
            elif fs > ms:
                sexe = "FEMELLE"; color = (0.690, 0.400, 0.110, 1); cv_c = (20, 100, 190)
                self.female_count += 1; conf = 85
                f1, f2, f3 = "• Morphologie allongée détectée", "• Texture de surface : lisse", "• Forme générale : long et fin"
            else:
                sexe = "INCERTAIN"; color = (0.45, 0.45, 0.45, 1); cv_c = (120, 120, 120)
                conf = 50
                f1, f2, f3 = "• Caractéristiques ambiguës", "• Essayez une photo de profil nette", "• Augmentez le contraste si possible"

            self.save_counts()

            x1, y1, x2, y2 = boxes.xyxy[best_idx].cpu().numpy().astype(int)
            out = bgr.copy()
            cv2.rectangle(out, (x1, y1), (x2, y2), cv_c, 2)
            cv2.putText(out, f"{sexe} {conf}%", (10, 36),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, cv_c, 2)

            tmp = os.path.join(tempfile.gettempdir(), "last_result.jpg")
            cv2.imwrite(tmp, out)

            res = self.root.get_screen('result')
            res.ids.result_image.source = tmp
            res.ids.result_image.reload()
            res.ids.result_label.text = sexe
            res.ids.result_label.theme_text_color = "Custom"
            res.ids.result_label.text_color = color
            res.ids.confidence_label.text = f"Confiance : {conf} %"
            res.ids.factor1_label.text = f1
            res.ids.factor2_label.text = f2
            res.ids.factor3_label.text = f3
            self.root.current = 'result'

        except Exception as e:
            self.show_error(str(e))

    def show_error(self, msg):
        MDDialog(title="Erreur", text=msg).open()


if __name__ == '__main__':
    CharanconApp().run()