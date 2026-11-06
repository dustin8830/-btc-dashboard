[app]

title = BTC Miner Dashboard
package.name = btcdashboard
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv

version = 1.0

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.archs = arm64-v8a
android.minapi = 23

[buildozer]

log_level = 2
warn_on_root = 1
