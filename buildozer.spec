[app]
title = Mbabu Scan
package.name = mbabu_scan
package.domain = com.mbabu

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,pt

version = 1.0

entrypoint = main.py

requirements = python3,kivy,kivymd,pillow,numpy,plyer,opencv-python

orientation = portrait

presplash.color = #f5f5f5

android.minapi = 21
android.api = 33
android.ndk = 25b
android.archs = arm64-v8a

android.permissions = CAMERA,INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,VIBRATE

android.features = android.hardware.camera,android.hardware.camera.autofocus

fullscreen = 0

log_level = 1

[buildozer]
build_dir = .buildozer
bin_dir = ./bin
