import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os
import sys
import datetime
import mss
import pygetwindow as gw
import subprocess

def resource_path(relative_path):
    """PyInstallerでEXE化した場合でも、正しいパスを返す"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# ゲームウィンドウ取得
def get_game_window():
    wins = gw.getWindowsWithTitle('艦隊これくしょん')
    return wins[0] if wins else None

# キャプチャ関数
def capture_area(area_config):
    win = get_game_window()
    if not win: return None
    x = int(win.left + win.width * area_config['left_point'])
    y = int(win.top + win.height * area_config['top_point'])
    w = int(win.width * area_config['width'])
    h = int(win.height * area_config['height'])
    with mss.mss() as sct:
        img = sct.grab({'left': x, 'top': y, 'width': w, 'height': h})
        return Image.frombytes('RGB', img.size, img.rgb)

# 画像ラベル作成関数
def make_image_label(parent, index, w, h, label_text, is_fleet):
    frame = tk.Frame(parent, width=w, height=h)
    frame.pack_propagate(False)
    label = tk.Label(frame, text=label_text, bg='white')
    label.pack(fill='both', expand=True)

    # ラベル管理
    if is_fleet:
        fleet_labels.append(label)
    else:
        kichi_labels.append(label)

    def on_click(event=None):
        if is_fleet:
            if fleet_images_display[index]:
                label.config(image='', text=str(index + 1))
                fleet_images_display[index] = None
                fleet_images_original[index] = None
            else:
                img = capture_area(hensei)
                if img:
                    original_img = img.copy()
                    img.thumbnail((w, h))
                    tk_img = ImageTk.PhotoImage(img)
                    label.config(image=tk_img, text='')
                    label.image = tk_img
                    fleet_images_display[index] = img
                    fleet_images_original[index] = original_img
        else:
            if kichi_images_display[index]:
                label.config(image='', text=str(index + 1))
                kichi_images_display[index] = None
                kichi_images_original[index] = None
            else:
                img = capture_area(kichi)
                if img:
                    original_img = img.copy()
                    img.thumbnail((w, h))
                    tk_img = ImageTk.PhotoImage(img)
                    label.config(image=tk_img, text='')
                    label.image = tk_img
                    kichi_images_display[index] = img
                    kichi_images_original[index] = original_img

    label.bind("<Button-1>", on_click)
    return frame

# 艦隊編成のクリア
def clear_fleet():
    for i in range(12):
        fleet_images_display[i] = None
        fleet_images_original[i] = None
        fleet_labels[i].config(image='', text=str(i+1))

# 艦隊編成の画像保存
def save_fleet():
    # 登録済み画像のインデックスを抽出
    valid_indices = [i for i, img in enumerate(fleet_images_original) if img]
    if not valid_indices:
        return

    # 使用する画像とその位置を取得
    positions = []
    cell_w = 0
    cell_h = 0
    for i in valid_indices:
        img = fleet_images_original[i]
        row = get_rowNum(i)
        col = get_columnNum(i)
        positions.append((img, row, col))
        cell_w = max(cell_w, img.width)
        cell_h = max(cell_h, img.height)

    # 使用する最大行・列を算出
    max_row = max(pos[1] for pos in positions)
    max_col = max(pos[2] for pos in positions)

    # 結合キャンバス作成
    combined = Image.new('RGB', ((max_col + 1) * cell_w, (max_row + 1) * cell_h), (255, 255, 255))

    # 貼り付け
    for img, row, col in positions:
        x = col * cell_w
        y = row * cell_h
        combined.paste(img, (x, y))

    # 保存
    filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_kantai.png')
    combined.save(os.path.join(config['save_dir'], filename))

# 基地航空隊のクリア
def clear_kichi():
    for i in range(3):
        kichi_images_display[i] = None
        kichi_images_original[i] = None
        kichi_labels[i].config(image='', text=str(i+1))

# 基地航空隊の画像保存
def save_kichi():
    imgs = [img for img in kichi_images_original if img]
    if not imgs: return
    total_w = sum(img.width for img in imgs)
    max_h = max(img.height for img in imgs)
    combined = Image.new('RGB', (total_w, max_h))
    x = 0
    for img in imgs:
        combined.paste(img, (x, 0))
        x += img.width
    filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_kichi.png')
    combined.save(os.path.join(save_dir, filename))

# フォルダ設定
def set_folder():
    folder = filedialog.askdirectory()
    if folder:
        config['save_dir'] = folder
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

def open_folder():
    folder = config.get('save_dir', '')
    if os.path.isdir(folder):
        subprocess.Popen(['explorer', os.path.normpath(folder)])

def get_columnNum(i):
    pairs = {(0, 2, 4): 0, (1, 3, 5): 1, (6, 8, 10): 2, (7, 9, 11): 3}
    for a, b, c in pairs:
        if i == a or i == b or i == c:
            return pairs[(a, b, c)]
    return None

def get_rowNum(i):
    pairs = {(0, 1): 0, (2, 3): 1, (4, 5): 2, (6, 7): 0, (8, 9): 1, (10, 11): 2}
    for a, b in pairs:
        if i == a or i == b:
            return pairs[(a, b)]
    return None

VERSION = "1.0.2"
CONFIG_PATH = resource_path('config.json')

# 設定読み込み
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

save_dir = config['save_dir']
hensei = config['hensei']
kichi = config['kichi']
fleet_labels = []
kichi_labels = []
fleet_images_display = [None] * 12
fleet_images_original = [None] * 12
kichi_images_display = [None] * 3
kichi_images_original = [None] * 3

# GUI初期化
root = tk.Tk()
root.title(f"KanColleCap")
root.geometry("600x270")

# アイコン設定（タイトルバー用）
root.iconbitmap(resource_path("icon.ico"))

fleet_images = [None]*12
kichi_images = [None]*3

# オプションエリア
option_frame = tk.LabelFrame(root, text="", padx=10, pady=2)
option_frame.place(x=5, y=0)

# インフォメーションエリア
info_frame = tk.LabelFrame(root, text="", padx=10, pady=5)
info_frame.place(x=290, y=0)

# 艦隊エリア
fleet_frame = tk.LabelFrame(root, text="艦隊", padx=10, pady=5)
fleet_frame.place(x=5, y=40)

for i in range(12):
    make_image_label(fleet_frame, i, 60, 50, str(i+1), True).grid(row=get_rowNum(i), column=get_columnNum(i), padx=2, pady=2)

# 基地航空隊エリア
kichi_frame = tk.LabelFrame(root, text="基地航空隊", padx=10, pady=5)
kichi_frame.place(x=290, y=40)

for i in range(3):
    make_image_label(kichi_frame, i, 90, 160, str(i+1), False).grid(row=0, column=i, padx=2)

tk.Label(info_frame, text=f"Version: {VERSION}").grid(row=0, column=0, sticky='w')
tk.Label(info_frame, text=f"@Aburahamu_aa").grid(row=0, column=1, sticky='w')

tk.Button(option_frame, text="SetFolder", command=set_folder).grid(row=0, column=0, padx=30)
tk.Button(option_frame, text="OpenFolder", command=open_folder).grid(row=0, column=1, padx=30)

tk.Button(fleet_frame, text="クリア", command=clear_fleet).grid(row=3, column=0, pady=5)
tk.Button(fleet_frame, text="保存", command=save_fleet).grid(row=3, column=3, pady=5)

tk.Button(kichi_frame, text="クリア", command=clear_kichi).grid(row=1, column=0, pady=5)
tk.Button(kichi_frame, text="保存", command=save_kichi).grid(row=1, column=2, pady=5)

root.mainloop()