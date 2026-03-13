import tkinter as tk
from tkinter import ttk, filedialog
import os
import subprocess
import webbrowser
import threading
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class GIMFuCKconverter:
    def __init__(self, root):
        self.root = root
        self.root.title("GIMFuCKconverter")
        self.root.geometry("1100x850")
        self.root.configure(bg="#121212")

        self.gimconv_exe = os.path.join(BASE_DIR, "gimconv.exe")
        self.gimview_exe = os.path.join(BASE_DIR, "GimView.exe")
        
        self.current_path = BASE_DIR
        self.history = [BASE_DIR]
        self.history_index = 0
        self.checked_files = set() 
        self.multi_select_mode = False 

        self.langs = {
            "English": {
                "png_gim": "PNG ➔ GIM", "gim_png": "GIM ➔ PNG", "palette": "Palette:",
                "about": "About", "lang_btn": "Language", "explorer": " Explorer",
                "select_file": "Select a file", "logs_title": " PROCESS LOGS:",
                "save_title": "Convert", "selected_text": "Selected: ",
                "multi_select": "Checked: ", "multi_btn_on": "Multi-select: ON", "multi_btn_off": "Multi-select: OFF",
                "author_text": "Application created by sklad.akrgooda"
            },
            "Русский": {
                "png_gim": "PNG ➔ GIM", "gim_png": "GIM ➔ PNG", "palette": "Палитра:",
                "about": "О приложении", "lang_btn": "Язык", "explorer": " Проводник",
                "select_file": "Выберите файл", "logs_title": " ЛОГИ ПРОЦЕССА:",
                "save_title": "Конвертация", "selected_text": "Выбрано: ",
                "multi_select": "Отмечено: ", "multi_btn_on": "Выбор нескольких: ВКЛ", "multi_btn_off": "Выбор нескольких: ВЫКЛ",
                "author_text": "Приложение создано sklad.akrgooda"
            },
            "Украинский": {
                "png_gim": "PNG ➔ GIM", "gim_png": "GIM ➔ PNG", "palette": "Палітра:",
                "about": "Про програму", "lang_btn": "Мова", "explorer": " Провідник",
                "select_file": "Оберіть файл", "logs_title": " ЛОГИ ПРОЦЕСУ:",
                "save_title": "Конвертація", "selected_text": "Обрано: ",
                "multi_select": "Відмічено: ", "multi_btn_on": "Вибір кількох: ВКЛ", "multi_btn_off": "Вибір кількох: ВИКЛ",
                "author_text": "Програма створена sklad.akrgooda"
            },
            "Португальский": {
                "png_gim": "PNG ➔ GIM", "gim_png": "GIM ➔ PNG", "palette": "Paleta:",
                "about": "Sobre", "lang_btn": "Idioma", "explorer": " Explorador",
                "select_file": "Selecione um arquivo", "logs_title": " LOGS DO PROCESSO:",
                "save_title": "Conversão", "selected_text": "Selecionado: ",
                "multi_select": "Marcados: ", "multi_btn_on": "Multi-seleção: LIG", "multi_btn_off": "Multi-seleção: DESL",
                "author_text": "Aplicativo criado por sklad.akrgooda"
            }
        }
        self.current_lang = "English"

        self.setup_styles()
        self.create_widgets()
        self.update_ui_text()
        self.populate_tree(BASE_DIR)
        
        self.log("GIMFuCKconverter Ready nya^^. Logs active.", "SUCCESS")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e", borderwidth=0)
        style.map("Treeview", background=[('selected', '#005a9e')])

    def log(self, message, log_type="INFO"):
        def _append():
            ts = datetime.now().strftime("%H:%M:%S")
            self.log_area.config(state=tk.NORMAL)
            tag = "SUCCESS" if log_type == "SUCCESS" else "ERROR" if log_type == "ERROR" else "INFO"
            self.log_area.insert(tk.END, f"[{ts}] ", "gray")
            self.log_area.insert(tk.END, f"{message}\n", tag)
            self.log_area.tag_config("SUCCESS", foreground="#00ff00")
            self.log_area.tag_config("ERROR", foreground="#ff4444")
            self.log_area.tag_config("gray", foreground="#888888")
            self.log_area.config(state=tk.DISABLED)
            self.log_area.see(tk.END)
        self.root.after(0, _append)

    def create_widgets(self):
        # ВЕРХНЯЯ ПАНЕЛЬ
        top = tk.Frame(self.root, bg="#1e1e1e", height=50)
        top.pack(side=tk.TOP, fill=tk.X)

        self.btn_png_gim = tk.Button(top, command=lambda: self.start_thread("to_gim"), bg="#2e7d32", fg="white", relief="flat", font=("Segoe UI", 9, "bold"), padx=10)
        self.btn_png_gim.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_gim_png = tk.Button(top, command=lambda: self.start_thread("to_png"), bg="#1565c0", fg="white", relief="flat", font=("Segoe UI", 9, "bold"), padx=10)
        self.btn_gim_png.pack(side=tk.LEFT, padx=5)

        self.btn_multi = tk.Button(top, command=self.toggle_multi_select, bg="#555", fg="white", relief="flat", font=("Segoe UI", 9, "bold"), padx=10)
        self.btn_multi.pack(side=tk.LEFT, padx=20)

        self.lbl_palette = tk.Label(top, bg="#1e1e1e", fg="white")
        self.lbl_palette.pack(side=tk.LEFT, padx=10)
        
        self.format_var = tk.StringVar(value="rgba8888")
        fmt = tk.OptionMenu(top, self.format_var, "rgba8888", "rgba5551", "rgba4444", "rgba5650")
        fmt.config(bg="#333", fg="white", highlightthickness=0); fmt.pack(side=tk.LEFT)

        self.btn_about = tk.Button(top, command=self.show_about, bg="#444", fg="white", relief="flat"); self.btn_about.pack(side=tk.RIGHT, padx=10)
        self.btn_lang = tk.Button(top, command=self.show_languages, bg="#444", fg="white", relief="flat"); self.btn_lang.pack(side=tk.RIGHT, padx=5)

        # НИЖНЯЯ ПАНЕЛЬ ЛОГОВ (ЖЕСТКАЯ ПРИВЯЗКА)
        self.log_container = tk.Frame(self.root, bg="#1e1e1e", height=180)
        self.log_container.pack(side=tk.BOTTOM, fill=tk.X)
        self.log_container.pack_propagate(False)

        self.lbl_logs = tk.Label(self.log_container, bg="#252525", fg="#aaa", anchor="w", padx=10)
        self.lbl_logs.pack(fill=tk.X)
        
        self.log_area = tk.Text(self.log_container, bg="black", fg="white", state=tk.DISABLED, borderwidth=0, font=("Consolas", 10))
        self.log_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc = tk.Scrollbar(self.log_container, command=self.log_area.yview); sc.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_area.config(yscrollcommand=sc.set)

        # СРЕДНЯЯ ЧАСТЬ (ПРОВОДНИК)
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#121212", bd=0, sashwidth=4)
        self.paned.pack(fill=tk.BOTH, expand=True)

        ex_f = tk.Frame(self.paned, bg="#181818")
        nav = tk.Frame(ex_f, bg="#252525")
        nav.pack(fill=tk.X)
        # ВОТ ОНИ, КНОПКИ НАВИГАЦИИ + ВЫБОР ПАПКИ
        tk.Button(nav, text=" < ", command=self.go_back, bg="#444", fg="white", relief="flat").pack(side=tk.LEFT, padx=1, pady=2)
        tk.Button(nav, text=" > ", command=self.go_forward, bg="#444", fg="white", relief="flat").pack(side=tk.LEFT, padx=1, pady=2)
        tk.Button(nav, text=" 🏠 ", command=self.go_home, bg="#444", fg="white", relief="flat").pack(side=tk.LEFT, padx=1, pady=2)
        tk.Button(nav, text=" 📁 ", command=self.browse_directory, bg="#444", fg="white", relief="flat").pack(side=tk.LEFT, padx=5, pady=2)

        self.tree = ttk.Treeview(ex_f, columns=("path"), selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Button-1>", self.on_click)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.paned.add(ex_f, width=450)

        self.status_f = tk.Frame(self.paned, bg="#121212")
        self.status_label = tk.Label(self.status_f, bg="#121212", fg="white", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(expand=True)
        self.paned.add(self.status_f)

    def browse_directory(self):
        new_dir = filedialog.askdirectory()
        if new_dir:
            self.navigate_to(new_dir)

    def toggle_multi_select(self):
        self.multi_select_mode = not self.multi_select_mode
        self.checked_files.clear()
        self.update_ui_text()
        self.populate_tree(self.current_path)

    def on_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item: return
        path = self.tree.item(item, "values")[0]
        if os.path.isdir(path): return
        if self.multi_select_mode:
            if path in self.checked_files: self.checked_files.remove(path)
            else: self.checked_files.add(path)
            self.refresh_item_text(item, path)
        else:
            self.checked_files = {path}
            self.populate_tree(self.current_path)
        
        if path.lower().endswith(".gim") and os.path.exists(self.gimview_exe):
            subprocess.Popen([self.gimview_exe, path], creationflags=0x08000000)
        elif path.lower().endswith(".png"):
            os.startfile(path)
        self.update_selection_status()

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item: return
        path = self.tree.item(item, "values")[0]
        if os.path.isdir(path): self.navigate_to(path)

    def refresh_item_text(self, item, path):
        pfx = "[✔] " if path in self.checked_files else "[  ] "
        self.tree.item(item, text=f"{pfx}{os.path.basename(path)}")

    def populate_tree(self, path):
        self.tree.delete(*self.tree.get_children())
        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for e in entries:
                if e.is_dir() or e.name.lower().endswith(('.png', '.gim')):
                    pfx = ""
                    if e.is_file() and self.multi_select_mode:
                        pfx = "[✔] " if e.path in self.checked_files else "[  ] "
                    self.tree.insert("", "end", text=f"{pfx}{e.name}", values=[e.path])
        except: pass

    def navigate_to(self, new_path, add_h=True):
        if add_h:
            self.history = self.history[:self.history_index+1]
            self.history.append(new_path)
            self.history_index = len(self.history)-1
        self.current_path = new_path
        self.populate_tree(new_path)

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.navigate_to(self.history[self.history_index], False)
    def go_forward(self):
        if self.history_index < len(self.history)-1:
            self.history_index += 1
            self.navigate_to(self.history[self.history_index], False)
    def go_home(self): self.navigate_to(BASE_DIR)

    def update_selection_status(self):
        t = self.langs[self.current_lang]
        count = len(self.checked_files)
        if count == 0: self.status_label.config(text=t["select_file"])
        elif count == 1: self.status_label.config(text=f"{t['selected_text']}{os.path.basename(list(self.checked_files)[0])}")
        else: self.status_label.config(text=f"{t['multi_select']}{count}")

    def update_ui_text(self):
        t = self.langs[self.current_lang]
        self.btn_png_gim.config(text=t["png_gim"])
        self.btn_gim_png.config(text=t["gim_png"])
        self.lbl_palette.config(text=t["palette"])
        self.btn_lang.config(text=t["lang_btn"])
        self.btn_about.config(text=t["about"])
        self.lbl_logs.config(text=t["logs_title"])
        self.btn_multi.config(text=t["multi_btn_on"] if self.multi_select_mode else t["multi_btn_off"])
        self.update_selection_status()

    def start_thread(self, mode):
        v = [p for p in self.checked_files if (mode=="to_gim" and p.endswith(".png")) or (mode=="to_png" and p.endswith(".gim"))]
        if not v: return
        dest = filedialog.askdirectory()
        if dest:
            threading.Thread(target=self.run_task, args=(v, mode, dest), daemon=True).start()

    def run_task(self, files, mode, dest):
        self.log(f"Batch conversion started for {len(files)} files...")
        fmt = self.format_var.get()
        for f in files:
            ext = ".gim" if mode=="to_gim" else ".png"
            out = os.path.join(dest, os.path.splitext(os.path.basename(f))[0] + ext)
            cmd = [self.gimconv_exe, f, "--image_format", fmt, "--pixel_order", "normal", "-o", out] if mode=="to_gim" else [self.gimconv_exe, f, "-o", out]
            try:
                subprocess.run(cmd, check=True, creationflags=0x08000000)
                self.log(f"DONE: {os.path.basename(f)}", "SUCCESS")
            except:
                self.log(f"FAIL: {os.path.basename(f)}", "ERROR")
        self.log("Batch finished.", "SUCCESS")
        self.root.after(0, lambda: self.populate_tree(self.current_path))

    def show_languages(self):
        win = tk.Toplevel(self.root); win.title("Language"); win.geometry("250x220"); win.grab_set(); win.configure(bg="#252525")
        ln = [("English", "English"), ("Русский", "Русский"), ("Украинский", "Українська"), ("Португальский", "Português")]
        for lid, lname in ln:
            tk.Button(win, text=lname, bg="#444", fg="white", relief="flat", command=lambda n=lid: [setattr(self, 'current_lang', n), self.update_ui_text(), win.destroy()]).pack(pady=5, fill=tk.X, padx=10)

    def show_about(self):
        t = self.langs[self.current_lang]
        win = tk.Toplevel(self.root); win.title(t["about"]); win.geometry("400x250"); win.configure(bg="#252525")
        tk.Label(win, text="GIMFuCKconverter", font=("Segoe UI", 16, "bold"), bg="#252525", fg="#00ff00").pack(pady=10)
        tk.Label(win, text=t["author_text"], bg="#252525", fg="white").pack()
        f = tk.Frame(win, bg="#252525"); f.pack(pady=15)
        tk.Button(f, text="GitHub", bg="#333", fg="white", width=12, command=lambda: webbrowser.open("https://github.com/akrgood")).pack(side=tk.LEFT, padx=5)
        tk.Button(f, text="Telegram", bg="#0088cc", fg="white", width=12, command=lambda: webbrowser.open("https://AKRGGXD.t.me")).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = GIMFuCKconverter(root)
    root.mainloop()