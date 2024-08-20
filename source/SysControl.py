import os
import shutil
import subprocess
import tkinter as tk
from tkinter import font, messagebox
import winreg as reg
from ttkbootstrap import Style
import threading

def ensure_registry_key_exists(key, sub_key):
    try:
        reg.OpenKey(key, sub_key)
    except FileNotFoundError:
        reg.CreateKey(key, sub_key)

def toggle_task_manager(enable=True):
    key = reg.HKEY_CURRENT_USER
    sub_key = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "DisableTaskMgr"
    ensure_registry_key_exists(key, sub_key)
    with reg.OpenKey(key, sub_key, 0, reg.KEY_WRITE) as reg_key:
        reg.SetValueEx(reg_key, value_name, 0, reg.REG_DWORD, 0 if enable else 1)
    action = "включен" if enable else "отключен"
    messagebox.showinfo("Результат", f"Диспетчер задач {action}.")

def toggle_cmd(enable=True):
    key = reg.HKEY_CURRENT_USER
    sub_key = r"Software\Policies\Microsoft\Windows\System"
    value_name = "DisableCMD"
    ensure_registry_key_exists(key, sub_key)
    with reg.OpenKey(key, sub_key, 0, reg.KEY_WRITE) as reg_key:
        reg.SetValueEx(reg_key, value_name, 0, reg.REG_DWORD, 0 if enable else 1)
    action = "включена" if enable else "отключена"
    messagebox.showinfo("Результат", f"Командная строка {action}.")

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
        error_message = "Папки TEMP были очищены с ошибками:\n\n" + "\n".join(errors)
        messagebox.showerror("Ошибки при очистке", error_message)
    else:
        messagebox.showinfo("Результат", "Папки TEMP очищены")

def clear_recycle_bin():
    try:
        subprocess.run("PowerShell.exe -NoProfile -Command Clear-RecycleBin -Force",
                       shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        messagebox.showinfo("Результат", "Корзина очищена")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def show_system_info():
    def fetch_system_info():
        try:
            system_info_button.config(text="Подождите...", state=tk.DISABLED)
            root.update_idletasks()

            process = subprocess.Popen(["systeminfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, encoding='cp866', creationflags=subprocess.CREATE_NO_WINDOW)
            output, _ = process.communicate()

            info_window = tk.Toplevel(root)
            info_window.title("Информация о системе")
            info_window.geometry("600x500")

            info_label = tk.Label(info_window, text="Системная информация", font=header_font, bg="#2d2d2d", fg="#ffffff")
            info_label.pack(pady=10)

            info_text = tk.Text(info_window, wrap="word", font=body_font, bg="#333", fg="#fff")
            info_text.insert("1.0", output)
            info_text.config(state=tk.DISABLED)
            info_text.pack(padx=10, pady=10, fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            system_info_button.config(text="Информация о системе", state=tk.NORMAL)

    threading.Thread(target=fetch_system_info).start()

def reboot_pc():
    try:
        subprocess.run("shutdown /r /t 0", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

style = Style('darkly')
root = style.master
root.title("SysControl")
root.geometry("600x400")

header_font = font.Font(family="Google Sans", size=16, weight="bold")
body_font = font.Font(family="Google Sans", size=12)
footer_font = font.Font(family="Google Sans", size=10, slant="italic")

button_bg = "#444444"
button_fg = "#ffffff"

header_label = tk.Label(root, text="SysControl", font=header_font, anchor="w", bg="#2d2d2d", fg="#ffffff")
header_label.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="w")

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
    btn.grid(row=row + 1, column=col, padx=20, pady=10, sticky="ew", ipadx=10, ipady=5)

    if text == "Информация о системе":
        system_info_button = btn

footer_label = tk.Label(root, text="Made by NRT Corp. for you :)", font=footer_font, anchor="e", bg="#2d2d2d", fg="#ffffff")
footer_label.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky="e")

root.mainloop()
