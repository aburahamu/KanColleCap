import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json, os, datetime
import mss
import pygetwindow as gw
import subprocess

CONFIG_PATH = 'config.json'

# 設定読み込み
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

save_dir = config['save_dir']
hensei = config['hensei']
kichi = config['kichi']

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

def make_image_label(parent, index, w, h, label_text, is_fleet):
    frame = tk.Frame(parent, width=w, height=h)
    frame.pack_propagate(False)
    label = tk.Label(frame, text=label_text, bg='white')
    label.pack(fill='both', expand=True)

    def on_click(event=None):
        if (is_fleet and fleet_images[index]) or (not is_fleet and kichi_images[index]):
            label.config(image='', text=str(index+1))
            if is_fleet:
                fleet_images[index] = None
            else:
                kichi_images[index] = None
        else:
            area = hensei if is_fleet else kichi
            img = capture_area(area)
            if img:
                img.thumbnail((w, h))
                tk_img = ImageTk.PhotoImage(img)
                label.config(image=tk_img, text='')
                label.image = tk_img
                if is_fleet:
                    fleet_images[index] = img
                else:
                    kichi_images[index] = img

    label.bind("<Button-1>", on_click)
    return frame

# クリア・保存ボタン（艦隊）
def clear_fleet():
    for i in range(12):
        fleet_images[i] = None
        for widget in fleet_frame.grid_slaves():
            if isinstance(widget, tk.Frame):
                for lbl in widget.winfo_children():
                    lbl.config(image='', text=str(i+1))

def save_fleet():
    imgs = [img for img in fleet_images if img]
    if not imgs: return
    total_w = sum(img.width for img in imgs)
    max_h = max(img.height for img in imgs)
    combined = Image.new('RGB', (total_w, max_h))
    x = 0
    for img in imgs:
        combined.paste(img, (x, 0))
        x += img.width
    filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_kantai.png')
    combined.save(os.path.join(save_dir, filename))

# クリア・保存ボタン（基地）
def clear_kichi():
    for i in range(3):
        kichi_images[i] = None
        for widget in kichi_frame.grid_slaves():
            if isinstance(widget, tk.Frame):
                for lbl in widget.winfo_children():
                    lbl.config(image='', text=str(i+1))

def save_kichi():
    imgs = [img for img in kichi_images if img]
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
    if os.path.isdir(config['save_dir']):
        subprocess.Popen(f'explorer "{config["save_dir"]}"')

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
    
# GUI初期化
root = tk.Tk()
root.title("KanColleCap")
root.geometry("600x270")

fleet_images = [None]*12
kichi_images = [None]*3

# オプションエリア
option_frame = tk.LabelFrame(root, text="", padx=10, pady=2)
option_frame.place(x=5, y=0)

# 艦隊エリア
fleet_frame = tk.LabelFrame(root, text="艦隊", padx=10, pady=5)
fleet_frame.place(x=5, y=40)
fleet_w = hensei['view_width']
fleet_h = hensei['view_height']

for i in range(12):
    make_image_label(fleet_frame, i, fleet_w, fleet_h, str(i+1), True).grid(row=get_rowNum(i), column=get_columnNum(i), padx=2, pady=2)

# 基地航空隊エリア
kichi_frame = tk.LabelFrame(root, text="基地航空隊", padx=10, pady=5)
kichi_frame.place(x=290, y=40)
kichi_w = kichi['view_width']
kichi_h = kichi['view_height']

for i in range(3):
    make_image_label(kichi_frame, i, kichi_w, kichi_h, str(i+1), False).grid(row=0, column=i, padx=2)

tk.Button(option_frame, text="SetFolder", command=set_folder).grid(row=0, column=0, padx=30)
tk.Button(option_frame, text="OpenFolder", command=open_folder).grid(row=0, column=1, padx=30)

tk.Button(fleet_frame, text="クリア", command=clear_fleet).grid(row=3, column=0, pady=5)
tk.Button(fleet_frame, text="保存", command=save_fleet).grid(row=3, column=3, pady=5)

tk.Button(kichi_frame, text="クリア", command=clear_kichi).grid(row=1, column=0, pady=5)
tk.Button(kichi_frame, text="保存", command=save_kichi).grid(row=1, column=2, pady=5)

root.mainloop()