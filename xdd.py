import sys
import subprocess
import ctypes
import threading
import customtkinter as ctk

class UniversalInstallerGUI:
    def __init__(self):
        # Sprawdzenie uprawnień administratora
        if not self.is_admin():
            self.run_as_admin()
            sys.exit()

        # Konfiguracja okna
        self.root = ctk.CTk()
        self.root.title("Universal ToolBox - Multithreaded")
        self.root.geometry("500x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Struktura danych: Kategorie -> Programy
        self.categories = {
            "Programy": [
                {
                    "name": "Spicetify (Spotify Customizer)", 
                    "cmd": "iwr -useb https://raw.githubusercontent.com/spicetify/cli/main/install.ps1 | iex", 
                    "type": "powershell"
                }
                # Tutaj możesz dodawać kolejne programy do tej kategorii
            ],
            "Narzędzia Systemowe": [
                {"name": "Wyczyść DNS", "cmd": "ipconfig /flushdns", "type": "cmd"},
                {"name": "SFC Scan", "cmd": "sfc /scannow", "type": "cmd"}
            ]
        }

        self.current_view = "menu"
        self.setup_ui()

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    def execute_command_threaded(self, cmd, cmd_type):
        """Uruchamia komendę w osobnym wątku, aby nie blokować GUI."""
        thread = threading.Thread(target=self.run_command, args=(cmd, cmd_type))
        thread.daemon = True  # Zamknie wątek, jeśli zamkniesz program
        thread.start()

    def run_command(self, cmd, cmd_type):
        """Logika wykonania komendy (uruchamiana w wątku)."""
        self.status_label.configure(text=f"Status: Przetwarzanie...", text_color="yellow")
        
        try:
            if cmd_type == "powershell":
                # Używamy -NoProfile dla czystego środowiska i -ExecutionPolicy Bypass dla skryptów z sieci
                process_args = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd]
                result = subprocess.run(process_args, capture_output=False)
            else:
                result = subprocess.run(cmd, shell=True, capture_output=False)

            if result.returncode == 0:
                self.root.after(0, lambda: self.status_label.configure(text="Status: Operacja zakończona!", text_color="green"))
            else:
                self.root.after(0, lambda: self.status_label.configure(text=f"Status: Błąd ({result.returncode})", text_color="red"))
        except Exception as e:
            self.root.after(0, lambda: self.status_label.configure(text=f"Błąd: {str(e)[:30]}...", text_color="red"))

    def clear_frame(self):
        """Usuwa wszystkie elementy z ramki przewijanej."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        """Wyświetla listę 'folderów' (kategorii)."""
        self.clear_frame()
        self.back_button.pack_forget() # Ukryj przycisk powrotu w menu głównym
        self.header.configure(text="Menu Główne")
        
        for category in self.categories.keys():
            btn = ctk.CTkButton(
                self.scroll_frame, 
                text=f"📁 {category}", 
                command=lambda c=category: self.show_category(c),
                height=50,
                fg_color="#2c3e50",
                hover_color="#34495e"
            )
            btn.pack(pady=10, padx=20, fill="x")

    def show_category(self, category_name):
        """Wyświetla programy wewnątrz wybranej kategorii."""
        self.clear_frame()
        self.header.configure(text=f"Kategoria: {category_name}")
        self.back_button.pack(pady=5, side="top") # Pokaż przycisk powrotu

        for tool in self.categories[category_name]:
            btn = ctk.CTkButton(
                self.scroll_frame, 
                text=f"🚀 {tool['name']}", 
                command=lambda t=tool: self.execute_command_threaded(t["cmd"], t["type"]),
                height=45
            )
            btn.pack(pady=5, padx=20, fill="x")

    def setup_ui(self):
        """Inicjalizacja głównego interfejsu."""
        # Nagłówek
        self.header = ctk.CTkLabel(self.root, text="Universal ToolBox", font=("Roboto", 22, "bold"))
        self.header.pack(pady=20)

        # Przycisk powrotu (domyślnie ukryty)
        self.back_button = ctk.CTkButton(self.root, text="← Powrót", command=self.show_main_menu, fg_color="gray")

        # Ramka na zawartość
        self.scroll_frame = ctk.CTkScrollableFrame(self.root, width=440, height=400)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Status
        self.status_label = ctk.CTkLabel(self.root, text="Status: Oczekiwanie", font=("Roboto", 13))
        self.status_label.pack(pady=20)

        # Uruchom menu główne
        self.show_main_menu()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = UniversalInstallerGUI()
    app.run()