[app]

title = 2048
package.name = game2048
package.domain = org.hgus.game2048

source.dir = .
source.include_exts = py,json,png,jpg,kv,atlas
source.include_patterns = main.py,game_utils.py,config.json
source.exclude_exts = spec,md,bat,sh
source.exclude_dirs = .venv,venv,.git,.buildozer,bin,docs,__pycache__
source.exclude_patterns = setup.*,Dockerfile,.gitignore

version = 1.0.0

requirements = python3,kivy==2.2.1

orientation = portrait
fullscreen = 0

android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a,armeabi-v7a
android.enable_androidx = True
android.wakelock = False

# Uncomment when you add assets:
# android.icon.filename = %(source.dir)s/data/icon.png
# android.presplash_filename = %(source.dir)s/data/presplash.png

[buildozer]

log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
