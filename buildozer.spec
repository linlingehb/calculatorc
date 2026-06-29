[app]

# 应用显示名称
title = 科学计算器

# 包名
package.name = calculator

# 包域名
package.domain = com.example

# 源代码目录
source.dir = .

# 包含的文件扩展名
source.include_exts = py,png,jpg,kv,atlas

# 应用版本
version = 1.0

# 依赖（Kivy 已内置 math，无需额外依赖）
requirements = python3,kivy

# 屏幕方向（竖屏）
orientation = portrait

# 全屏
fullscreen = 0

# Android 目标 API
android.api = 33
android.minapi = 24

# 自动接受 SDK 许可证（CI 构建必需）
android.accept_sdk_license = True

# CPU 架构
android.archs = arm64-v8a, armeabi-v7a

# 应用权限（科学计算器无需特殊权限）
android.permissions = 

# 保留日志（调试时可开启）
android.logcat_filters = *:S python:D

# 图标和闪屏（可选，后续可添加）
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
