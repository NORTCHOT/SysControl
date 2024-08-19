import os
import subprocess
import tkinter as tk
from tkinter import font, messagebox
import winreg as reg
from ttkbootstrap import Style

# Функция для проверки и создания раздела реестра
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
    temp_dir = os.getenv('TEMP')
    try:
        subprocess.run(f'del /q/f/s "{temp_dir}\\*"', shell=True)
        messagebox.showinfo("Результат", "Папка TEMP очищена")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def clear_recycle_bin():
    try:
        subprocess.run("PowerShell.exe -NoProfile -Command Clear-RecycleBin -Force", shell=True)
        messagebox.showinfo("Результат", "Корзина очищена")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def show_system_info():
    try:
        # Выполнение команды systeminfo с кодировкой cp866
        process = subprocess.Popen(["systeminfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866')
        output, _ = process.communicate()

        # Создание нового окна для отображения информации
        info_window = tk.Toplevel(root)
        info_window.title("Информация о системе")
        info_window.geometry("600x500")

        # Настройка текста для отображения
        info_label = tk.Label(info_window, text="Системная информация", font=header_font, bg="#2d2d2d", fg="#ffffff")
        info_label.pack(pady=10)

        # Поле для вывода системной информации
        info_text = tk.Text(info_window, wrap="word", font=body_font, bg="#333", fg="#fff")
        info_text.insert("1.0", output)
        info_text.config(state=tk.DISABLED)  # Сделать текст неизменяемым
        info_text.pack(padx=10, pady=10, fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def reboot_pc():
    try:
        subprocess.run("shutdown /r /t 0", shell=True)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Создание главного окна
style = Style('darkly')
root = style.master
root.title("SysControl")
root.geometry("600x400")

# Шрифты
header_font = font.Font(family="Google Sans", size=16, weight="bold")
body_font = font.Font(family="Google Sans", size=12)
footer_font = font.Font(family="Google Sans", size=10, slant="italic")

# Цветовая схема
button_bg = "#444444"  # Цвет фона кнопок
button_fg = "#ffffff"  # Цвет текста кнопок

# Добавление заголовка
header_label = tk.Label(root, text="SysControl", font=header_font, anchor="w", bg="#2d2d2d", fg="#ffffff")
header_label.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="w")

# Определение кнопок и их размещение
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

# Размещение кнопок в 2 столбца
for idx, (text, command) in enumerate(buttons):
    btn = tk.Button(root, text=text, command=command, font=body_font, bg=button_bg, fg=button_fg)
    row, col = divmod(idx, 2)
    btn.grid(row=row + 1, column=col, padx=20, pady=10, sticky="ew", ipadx=10, ipady=5)

# Добавление подписи в нижнем правом углу
footer_label = tk.Label(root, text="Made by NRT Corp. for you :)", font=footer_font, anchor="e", bg="#2d2d2d", fg="#ffffff")
footer_label.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky="e")

# Запуск главного цикла приложения
root.mainloop()
