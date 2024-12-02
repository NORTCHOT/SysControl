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
import winapps
import time
import traceback


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
    
def toggle_regedit(enable=True):
    key = reg.HKEY_CURRENT_USER
    sub_key = r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
    value_name = "DisableRegistryTools"
    ensure_registry_key_exists(key, sub_key)
    with reg.OpenKey(key, sub_key, 0, reg.KEY_WRITE) as reg_key:
        reg.SetValueEx(reg_key, value_name, 0, reg.REG_DWORD, 0 if enable else 1)
    action = "включен" if enable else "отключен"
    messagebox.showinfo("Информация", f"Редактор реестра {action}.")

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
                    errors.append(f"Файл: {file_path}\nОшибка: {str(e)}\n")
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    errors.append(f"Директория: {dir_path}\nОшибка: {str(e)}\n")
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

def get_installed_programs():
    programs = {}
    try:
        for app in winapps.list_installed():
            if app.name not in programs:
                version = app.version if app.version else 'Неизвестно'
                install_location = app.install_location if app.install_location else 'Неизвестно'
                install_date = app.install_date.strftime('%d.%m.%Y') if app.install_date else 'Неизвестно'
                programs[app.name] = (version, install_date, install_location)
        return [(name, *details) for name, details in programs.items()]
    except Exception as e:
        messagebox.showerror("Упс!", f"Ошибка получения данных об установленных программах: {str(e)}")
        return []

def get_network_info():
    try:
        ipconfig_output = subprocess.check_output(["ipconfig", "/all"], encoding='cp866', creationflags=subprocess.CREATE_NO_WINDOW)
        network_info_output = subprocess.check_output(["PowerShell", "-Command", "Get-NetAdapter | Select-Object Name, InterfaceDescription, MacAddress, Status, LinkSpeed, InterfaceIndex | Format-Table -AutoSize"], encoding='cp866', creationflags=subprocess.CREATE_NO_WINDOW)
        return f"{ipconfig_output}\n\n{network_info_output}"
    except Exception as e:
        return f"Ошибка получения данных о сети: {str(e)}"

def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("О программе")
    about_window.geometry("400x300")
    about_window.iconbitmap("icon.ico")

    logo_path = "icon.png"
    if os.path.exists(logo_path):
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((100, 100))
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(about_window, image=logo_photo, bg="#2d2d2d")
        logo_label.image = logo_photo
        logo_label.pack(pady=(20, 10))

    title_label = tk.Label(about_window, text="SysControl Update 4", font=header_font, fg="#ffffff", bg="#2d2d2d")
    title_label.pack()

    info_text = (
        "Made by NRT Corp.\n"
        "\n" # Можно было как то по другому? В прочем, работает, ну и ладно
        "Создано: NORTCHOT\n"
        "Бета тестеры: Klodska(KlodskaTeam), Kanat, Twaiger, martinwin10b1903"
    )
    info_label = tk.Label(about_window, text=info_text, font=footer_font, fg="#ffffff", bg="#2d2d2d", justify="left")
    info_label.pack(pady=10, anchor="w", padx=20)

def show_external_tools():														
    tools = [													
        ("KVRT", "Антивирус от Лаборатории Касперского без всего, кроме самого антивируса", "programs/KVRT.exe"),
        ("Process Hacker 2", "Замена диспетчеру задач с множеством полезных функций", "programs/ph/ProcessHacker.exe"),
        ("Screen Resizer", "Простая программа от KlodskaTeam для изменения разрешения экрана(Только того, которое поддерживает видеокарта)", "programs/SR.exe")
    ]														
														
    tools_window = tk.Toplevel(root)														
    tools_window.title("Запуск сторонних утилит")													
    tools_window.geometry("750x300")														
    tools_window.iconbitmap("icon.ico")														
														
    for tool in tools:														
        btn = tk.Button(tools_window, text=tool[0], command=lambda exe=tool[2]: subprocess.Popen(exe), font=body_font, bg=button_bg, fg=button_fg)
        btn.pack(pady=5, fill="x")														
														
        desc_label = tk.Label(tools_window, text=tool[1],font=footer_font, bg="#2d2d2d", fg="#ffffff")
        desc_label.pack(pady=2)														


def show_system_info():
    def fetch_system_info():
        try:
            system_info_button.config(text="Собираю информацию...", state=tk.DISABLED)
            root.update_idletasks()

            systeminfo_output = subprocess.check_output(["systeminfo"], encoding='cp866', creationflags=subprocess.CREATE_NO_WINDOW)
            system_info_button.config(text="Собираю информацию... (Система)")
            root.update_idletasks()

            dxdiag_output = get_dxdiag_info()
            system_info_button.config(text="Собираю информацию... (DxDiag)")
            root.update_idletasks()

            installed_programs = get_installed_programs()
            system_info_button.config(text="Собираю информацию... (Программы)")
            root.update_idletasks()

            network_info_output = get_network_info()
            system_info_button.config(text="Собираю информацию... (Сеть)")
            root.update_idletasks()

            info_window = tk.Toplevel(root)
            info_window.title("Информация о системе")
            info_window.geometry("950x600")
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

            programs_tab = ttk.Frame(notebook)
            notebook.add(programs_tab, text='Установленные программы')

            # Создаём фрейм для размещения дерева и полосы прокрутки
            programs_frame = ttk.Frame(programs_tab)
            programs_frame.pack(side=tk.TOP, fill="both", expand=True)

            # Размещаем дерево программ в фрейме
            programs_tree = ttk.Treeview(programs_frame, columns=("Index", "Name", "Version", "InstallDate", "Location"), show='headings')
            programs_tree.heading("Index", text="№")
            programs_tree.heading("Name", text="Название программы")
            programs_tree.heading("Version", text="Версия")
            programs_tree.heading("InstallDate", text="Дата установки")
            programs_tree.heading("Location", text="Путь установки")

            for idx, program in enumerate(installed_programs, start=1):
                programs_tree.insert("", "end", values=(idx,) + program)

            programs_tree.pack(side=tk.LEFT, fill="both", expand=True)

            # Размещаем полосу прокрутки в фрейме
            programs_scroll = ttk.Scrollbar(programs_frame, orient="vertical", command=programs_tree.yview)
            programs_scroll.pack(side=tk.RIGHT, fill="y")
            programs_tree.config(yscrollcommand=programs_scroll.set)

            # Добавляем памятку внизу вкладки
            note_label = tk.Label(programs_tab, text="*Здесь могут отображаться не все программы", font=footer_font, bg="#333", fg="#fff", justify="left")
            note_label.pack(side=tk.BOTTOM, anchor="w", padx=5, pady=5)

            network_tab = ttk.Frame(notebook)
            notebook.add(network_tab, text='Сеть')

            network_text = tk.Text(network_tab, wrap="word", font=body_font, bg="#333", fg="#fff")
            network_text.insert("1.0", network_info_output)
            network_text.config(state=tk.DISABLED)
            network_text.pack(side=tk.LEFT, fill="both", expand=True)

            network_scroll = ttk.Scrollbar(network_tab, command=network_text.yview)
            network_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            network_text.config(yscrollcommand=network_scroll.set)

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
root.geometry("700x630")
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
    ("Включить редактор реестра", lambda: toggle_regedit(True)),
    ("Отключить редактор реестра", lambda: toggle_regedit(False)),
    ("Очистить корзину", clear_recycle_bin),
    ("Очистить папку TEMP", clear_temp),
    ("Информация о системе", show_system_info),
    ("Перезагрузка ПК", reboot_pc),
    ("О программе", show_about),
    ("Запуск сторонних утилит", show_external_tools)
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
root.grid_rowconfigure(5, weight=1)

footer_label = tk.Label(root, text="Made by NRT Corp. for you :)", font=footer_font, anchor="e", bg="#2d2d2d", fg="#ffffff")
footer_label.grid(row=7, column=0, columnspan=2, padx=20, pady=10, sticky="e")

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
