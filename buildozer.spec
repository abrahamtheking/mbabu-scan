[app]

# Infos de base
title = Mbabu Scan
package.name = mbabu_scan
package.domain = com.mbabu

# Fichiers source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,pt

# Version
version = 1.0.0

# Point d'entrée
entrypoint = main.py

# Requirements — tout ce dont l'app a besoin
requirements = python3,\
    kivy==2.3.0,\
    kivymd==1.2.0,\
    pillow,\
    numpy,\
    opencv-python,\
    torch,\
    torchvision,\
    ultralytics,\
    plyer

# Orientation
orientation = portrait

# Icône et splash (place tes fichiers ici ou retire ces lignes)
# icon.filename = %(source.dir)s/assets/icon.png
# presplash.filename = %(source.dir)s/assets/splash.png

# Couleur du splash
presplash.color = #f5f5f5

# Android
android.minapi = 26
android.api = 33
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a

# Permissions nécessaires
android.permissions = CAMERA,\
    READ_EXTERNAL_STORAGE,\
    WRITE_EXTERNAL_STORAGE,\
    INTERNET,\
    RECEIVE_BOOT_COMPLETED,\
    VIBRATE

# Features Android
android.features = android.hardware.camera,\
    android.hardware.camera.autofocus

# Permet l'installation depuis sources inconnues (APK direct)
android.accept_sdk_license = True

# Mode fullscreen (cache la barre de statut Android)
fullscreen = 0

# Log level (0=erreur, 1=info, 2=debug)
log_level = 1

[buildozer]

# Dossier de build
build_dir = .buildozer

# Dossier de sortie APK
bin_dir = ./bin

# Niveau de log buildozer
log_level = 2

# Mise à jour auto du build si le code change
warn_on_root = 1
