import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import font, messagebox, ttk
import winreg as reg
from ttkbootstrap import Style
import threading
import ctypes
from PIL import Image, ImageTk

def check_admin_rights():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    if not is_admin:
        messagebox.showerror("Упс!", "Программа должна быть запущена от имени администратора.")
        sys.exit()

def restart_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)

def ensure_registry_key_exists(key, sub_key):
    try:
        reg.OpenKey(key, sub_key)
    except FileNotFoundError:
        reg.CreateKey(key, sub_key)

def toggle_task_manager(enable=True):
    key = reg.HKEY_CURRENT_USER
    sub_key = r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
    value_name = "DisableTaskMgr"
    ensure_registry_key_exists(key, sub_key)
    with reg.OpenKey(key, sub_key, 0, reg.KEY_WRITE) as reg_key:
        reg.SetValueEx(reg_key, value_name, 0, reg.REG_DWORD, 0 if enable else 1)
    action = "включен" if enable else "отключен"
    messagebox.showinfo("Информация", f"Диспетчер задач {action}.")

def toggle_cmd(enable=True):
    key = reg.HKEY_CURRENT_USER
    sub_key = r"Software\\Policies\\Microsoft\\Windows\\System"
    value_name = "DisableCMD"
    ensure_registry_key_exists(key, sub_key)
    with reg.OpenKey(key, sub_key, 0, reg.KEY_WRITE) as reg_key:
        reg.SetValueEx(reg_key, value_name, 0, reg.REG_DWORD, 0 if enable else 1)
    action = "включена" if enable else "отключена"
    messagebox.showinfo("Информация", f"Командная строка {action}.")

def log_errors(errors):
    with open("errors.log", "w") as log_file:
        for error in errors:
            log_file.write(error + "\n")
            
def clear_temp():
    temp_dirs = [os.getenv('TEMP'), r'C:\Windows\Temp']
    errors = []
    for temp_dir in temp_dirs:
        for root, dirs, files in os.walk(temp_dir):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                except Exception as e:
                    errors.append(f"File: {file_path}\nError: {str(e)}")
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    errors.append(f"Directory: {dir_path}\nError: {str(e)}")
    if errors:
        if len(errors) > 10:
            log_errors(errors)
            messagebox.showerror("Упс!", "Папки TEMP были очищены с ошибками, которых слишком много. Подробности сохранены в errors.log.")
        else:
            messagebox.showerror("Упс!", "\n".join(errors))
    else:
        messagebox.showinfo("Информация", "Папки TEMP очищены.")

def clear_recycle_bin():
    try:
        subprocess.run("PowerShell.exe -NoProfile -Command Clear-RecycleBin -Force", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        messagebox.showinfo("Информация", "Корзина очищена")
    except Exception as e:
        messagebox.showerror("Упс!", str(e))

def get_dxdiag_info():
    try:
        dxdiag_process = subprocess.Popen(["dxdiag", "/t", "dxdiag.txt"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dxdiag_process.wait()
        with open("dxdiag.txt", "r", encoding="cp866") as file:
            dxdiag_data = file.read()
        os.remove("dxdiag.txt")
        return dxdiag_data
    except Exception as e:
        return f"Ошибка получения данных DxDiag: {str(e)}"


def show_system_info():
    def fetch_system_info():
        try:
            system_info_button.config(text="Собираю информацию...", state=tk.DISABLED)
            root.update_idletasks()

            systeminfo_output = subprocess.check_output(["systeminfo"], encoding='cp866', creationflags=subprocess.CREATE_NO_WINDOW)

            dxdiag_output = get_dxdiag_info()


            info_window = tk.Toplevel(root)
            info_window.title("Информация о системе")
            info_window.geometry("900x600")
            info_window.iconbitmap("icon.ico")

            notebook = ttk.Notebook(info_window)
            notebook.pack(fill='both', expand=True)

            system_tab = ttk.Frame(notebook)
            notebook.add(system_tab, text='Информация о системе')

            system_text = tk.Text(system_tab, wrap="word", font=body_font, bg="#333", fg="#fff")
            system_text.insert("1.0", systeminfo_output)
            system_text.config(state=tk.DISABLED)
            system_text.pack(side=tk.LEFT, fill="both", expand=True)

            system_scroll = ttk.Scrollbar(system_tab, command=system_text.yview)
            system_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            system_text.config(yscrollcommand=system_scroll.set)

            hardware_tab = ttk.Frame(notebook)
            notebook.add(hardware_tab, text='Оборудование')

            hardware_text = tk.Text(hardware_tab, wrap="word", font=body_font, bg="#333", fg="#fff")
            hardware_text.insert("1.0", dxdiag_output)
            hardware_text.config(state=tk.DISABLED)
            hardware_text.pack(side=tk.LEFT, fill="both", expand=True)

            hardware_scroll = ttk.Scrollbar(hardware_tab, command=hardware_text.yview)
            hardware_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            hardware_text.config(yscrollcommand=hardware_scroll.set)

            

        finally:
            system_info_button.config(text="Информация о системе", state=tk.NORMAL)

    threading.Thread(target=fetch_system_info).start()

def reboot_pc():
    try:
        subprocess.run("shutdown /r /t 0", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        messagebox.showerror("Упс!", str(e))

style = Style('darkly')
root = style.master
root.title("SysControl")
root.geometry("600x400")
root.iconbitmap("icon.ico")

header_font = font.Font(family="Google Sans", size=16, weight="bold")
body_font = font.Font(family="Google Sans", size=12)
footer_font = font.Font(family="Google Sans", size=10, slant="italic")

button_bg = "#444444"
button_fg = "#ffffff"

header_frame = tk.Frame(root, bg="#2d2d2d")
header_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="w")

icon_label = tk.Label(header_frame, image=None, bg="#2d2d2d")
icon_label.grid(row=0, column=0, padx=(0, 10))

header_label = tk.Label(header_frame, text="SysControl", font=header_font, anchor="w", bg="#2d2d2d", fg="#ffffff")
header_label.grid(row=0, column=1)

buttons = [
    ("Включить диспетчер задач", lambda: toggle_task_manager(True)),
    ("Отключить диспетчер задач", lambda: toggle_task_manager(False)),
    ("Включить командную строку", lambda: toggle_cmd(True)),
    ("Отключить командную строку", lambda: toggle_cmd(False)),
    ("Очистить корзину", clear_recycle_bin),
    ("Очистить папку TEMP", clear_temp),
    ("Информация о системе", show_system_info),
    ("Перезагрузка ПК", reboot_pc)
]

system_info_button = None

for idx, (text, command) in enumerate(buttons):
    btn = tk.Button(root, text=text, command=command, font=body_font, bg=button_bg, fg=button_fg)
    row, col = divmod(idx, 2)
    btn.grid(row=row + 1, column=col, padx=20, pady=10, sticky="nsew", ipadx=10, ipady=5)
    if text == "Информация о системе":
        system_info_button = btn

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)

footer_label = tk.Label(root, text="Made by NRT Corp. for you :)", font=footer_font, anchor="e", bg="#2d2d2d", fg="#ffffff")
footer_label.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky="e")

icon_path = "icon.png"
if os.path.exists(icon_path):
    pil_image = Image.open(icon_path)
    pil_image = pil_image.resize((100, 100))
    app_icon = ImageTk.PhotoImage(pil_image)
    icon_label.config(image=app_icon)
    icon_label.image = app_icon

if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        restart_as_admin()
    else:
        root.mainloop()