import tkinter as tk
from tkinter import ttk
import pygame
import os
import random
import sys
import configparser
from screeninfo import get_monitors

if getattr(sys, 'frozen', False):
    # PyInstallerでビルドされた実行ファイルの場合
    exe_dir = os.path.dirname(sys.executable) + '\\'
else:
    # 通常のPythonスクリプトとして実行されている場合
    exe_dir = os.path.dirname(os.path.abspath(__file__)) + '\\'

# フォルダのファイル名を取得する関数
def get_mp3_files():
    files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")]
    files.sort()
    return files

# 停止していたファイル名を取得する関数
def get_current_filename():
    files = get_mp3_files()
    if 0 <= current_file_index < len(files):
        return files[current_file_index]
    return ""

# 曲を再生する関数
def play_music(file_list):
    global is_playing, current_file_index, is_paused
    if not file_list:
        status_label.config(text="MP3ファイルが見つかりません")
        return

    if is_playing:
        stop_music()

    current_file_index = 0
    is_paused = False
    is_playing = True
    pause_button.config(text="⏸ 一時停止")
    play_next(file_list)

# 次の曲を再生する関数
def play_next(file_list):
    global current_file_index, is_playing, is_paused
    if current_file_index >= len(file_list):
        if is_looping:
            current_file_index = 0
        else:
            is_playing = False
            is_paused = False
            status_label.config(text="再生終了")
            return

    filename = file_list[current_file_index]
    path = os.path.join(AUDIO_DIR, filename)
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(volume_slider.get() / 100)
    pygame.mixer.music.play()

    status_label.config(text=f"再生中: {filename}")

    def check_end():
        global current_file_index
        if is_playing and not pygame.mixer.music.get_busy() and not is_paused:
            if is_single_loop:
                # 同じ曲をもう一度再生
                play_next(file_list)
            else:
                current_file_index += 1
                play_next(file_list)
        elif is_playing:
            root.after(500, check_end)

    check_end()

# 停止ボタンの処理
def stop_music():
    global is_playing, is_paused
    pygame.mixer.music.stop()
    is_playing = False
    is_paused = False
    status_label.config(text="停止中")
    pause_button.config(text="⏸ 一時停止")

# 一時停止ボタンの処理
def toggle_pause():
    global is_paused
    if is_playing:
        if not is_paused:
            pygame.mixer.music.pause()
            is_paused = True
            pause_button.config(text="▶ 再開")
            status_label.config(text="一時停止中")
        else:
            pygame.mixer.music.unpause()
            is_paused = False
            pause_button.config(text="⏸ 一時停止")
            status_label.config(text=f"再生中: {get_current_filename()}")

# 前曲再生ボタンの処理
def play_previous():
    global current_file_index, is_paused, is_playing
    files = get_mp3_files()
    if current_file_index > 0:
        current_file_index -= 1
    else:
        current_file_index = len(files) - 1
    is_paused = False
    is_playing = True
    pause_button.config(text="⏸ 一時停止")
    play_next(files)

# 次曲ボタンの処理
def play_next_manual():
    global current_file_index, is_paused, is_playing
    files = get_mp3_files()
    current_file_index += 1
    is_paused = False
    is_playing = True
    pause_button.config(text="⏸ 一時停止")
    play_next(files)

# ループ再生オンボタンの処理
def enable_loop():
    global is_looping
    is_looping = True
    loop_label.config(text="全曲ループ: ON", fg="green")

# ループ再生オフボタンの処理
def disable_loop():
    global is_looping
    is_looping = False
    loop_label.config(text="全曲ループ: OFF", fg="gray")

# 単曲ループ再生オンボタンの処理
def enable_single_loop():
    global is_single_loop
    is_single_loop = True
    single_loop_label.config(text="単曲ループ: ON", fg="green")

# 単曲ループ再生オフボタンの処理
def disable_single_loop():
    global is_single_loop
    is_single_loop = False
    single_loop_label.config(text="単曲ループ: OFF", fg="gray")

# 再生ボタンの処理
def play_ordered():
    files = get_mp3_files()
    play_music(files)

# ランダム再生ボタンの処理
def play_random():
    files = get_mp3_files()
    random.shuffle(files)
    play_music(files)

# ボリュームが変更されたときの処理
def set_volume(val):
    pygame.mixer.music.set_volume(float(val) / 100)

# クローズボタンが押されたときの処理
def on_closing():
    # ウィンドウサイズを取得
    width = root.winfo_width()
    height = root.winfo_height()

    # ウィンドウのx座標とy座標を取得
    x = '+' + str(root.winfo_x()) if root.winfo_x() > 0 else str(root.winfo_x() - get_current_monitor_width() // 2)
    y = '+' + str(root.winfo_y()) if root.winfo_y() > 0 else str(root.winfo_y())
    
    # ボリュームとループ状態を保存（volume_sliderはScaleウィジェットの変数）
    volume_val = volume_slider.get()

    config.set("Application_Settings", "window_width", str(width))
    config.set("Application_Settings", "window_height", str(height))
    config.set("Application_Settings", "window_x", str(x))
    config.set("Application_Settings", "window_y", str(y))
    config.set("Application_Settings", "loop_flag", str(is_looping).lower())  # true/false を小文字で
    config.set("Application_Settings", "volume", str(volume_val))

    # 書き込み
    with open(exe_dir + 'config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)

    # 終了処理
    pygame.mixer.music.stop()
    root.destroy()

# モニターサイズの取得
def get_current_monitor_width():
    root.update_idletasks()
    x = root.winfo_x()
    y = root.winfo_y()

    for monitor in get_monitors():
        if (monitor.x <= x < monitor.x + monitor.width) and (monitor.y <= y < monitor.y + monitor.height):
            return monitor.width

    return 0  # 該当モニターが見つからない場合

# === 設定をコンフィグファイルから読み込む ===
config = configparser.ConfigParser()
with open(exe_dir + 'config.ini', encoding='utf-8') as f:
    config.read_file(f)

# 再生フォルダの取得
AUDIO_DIR = os.path.join(exe_dir, config['User_Settings']['folder_name'])

# 初期化
pygame.mixer.init()
is_playing = False
is_paused = False
is_looping = config.getboolean('Application_Settings', 'loop_flag')
is_single_loop = False  # 単曲ループON/OFF
current_file_index = 0

# GUI構築
root = tk.Tk()
root.title("MP3プレイヤー")
root.geometry(f"{config['Application_Settings']['window_width']}x{config['Application_Settings']['window_height']}{config['Application_Settings']['window_x']}{config['Application_Settings']['window_y']}")

# アイコンを変更
root.iconbitmap(os.path.join(exe_dir, 'george.ico'))

# 一番上の再生ファイル表示
status_label = tk.Label(root, text="待機中", font=("Arial", 12))
status_label.pack(pady=10)

# ループ再生などのアプリの状態表示
status_frame = tk.Frame(root)
status_frame.pack(pady=5)

# ループ再生がONの場合
if is_looping:
    loop_label = tk.Label(status_frame, text="全曲ループ: ON", font=("Arial", 10), fg="green")
# ループ再生がOFFの場合
else:
    loop_label = tk.Label(status_frame, text="全曲ループ: OFF", font=("Arial", 10), fg="gray")
loop_label.grid(row=0, column=0, padx=10)

single_loop_label = tk.Label(status_frame, text="単曲ループ: OFF", font=("Arial", 10), fg="gray")
single_loop_label.grid(row=0, column=1, padx=10)

# 音量バーの表示
volume_flame = tk.Frame(root)
volume_flame.pack(pady=5)

prev_button = ttk.Button(volume_flame, text="⏮ 前へ", command=play_previous)
prev_button.grid(row=0, column=0, padx=5)

volume_slider = ttk.Scale(volume_flame, from_=0, to=100, orient="horizontal", command=set_volume)
volume_slider.set(int(float(config['Application_Settings']['volume'])))
volume_slider.grid(row=0, column=1, padx=5)

next_button = ttk.Button(volume_flame, text="⏭ 次へ", command=play_next_manual)
next_button.grid(row=0, column=2, padx=5)

volume_label = tk.Label(root, text="音量")
volume_label.pack()

# 1段目のボタンフレーム
button_frame1 = tk.Frame(root)
button_frame1.pack(pady=10)

play_button = ttk.Button(button_frame1, text="▶ 通常再生", command=play_ordered)
play_button.grid(row=0, column=0, padx=5)

random_button = ttk.Button(button_frame1, text="🔀 ランダム再生", command=play_random)
random_button.grid(row=0, column=1, padx=5)

pause_button = ttk.Button(button_frame1, text="⏸ 一時停止", command=toggle_pause)
pause_button.grid(row=0, column=2, padx=5)

stop_button = ttk.Button(button_frame1, text="⏹ 停止", command=stop_music)
stop_button.grid(row=0, column=3, padx=5)

# 2段目のボタンフレーム
button_frame2 = tk.Frame(root)
button_frame2.pack(pady=5)

loop_on_button = ttk.Button(button_frame2, text="🔁 ループON", command=enable_loop)
loop_on_button.grid(row=0, column=0, padx=5)

loop_off_button = ttk.Button(button_frame2, text="❌ ループOFF", command=disable_loop)
loop_off_button.grid(row=0, column=1, padx=5)

single_loop_on_btn = ttk.Button(button_frame2, text="🔂 単曲ループON", command=enable_single_loop)
single_loop_on_btn.grid(row=0, column=2, padx=5)

single_loop_off_btn = ttk.Button(button_frame2, text="❌ 単曲ループOFF", command=disable_single_loop)
single_loop_off_btn.grid(row=0, column=3, padx=5)

# ×ボタンが押されたときの処理
root.protocol("WM_DELETE_WINDOW", on_closing)

# 実行
root.mainloop()
