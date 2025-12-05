import customtkinter as ctk
import threading
from OBS import get_grades

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OBS Not Botu")
        self.geometry("900x600")
        
        # Grid konfigürasyonu
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Başlık
        self.title_label = ctk.CTkLabel(self, text="OBS Not Sistemi", font=("Roboto", 24, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20)

        # Notların gösterileceği alan (Scrollable Frame)
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Ders Notları")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=3)
        self.scrollable_frame.grid_columnconfigure(2, weight=2)

        # Buton ve Durum Çubuğu
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        self.fetch_button = ctk.CTkButton(self.bottom_frame, text="Notları Getir", command=self.start_fetching_grades)
        self.fetch_button.pack(side="right", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self.bottom_frame, text="Hazır", text_color="gray")
        self.status_label.pack(side="left", padx=10, pady=10)

    def start_fetching_grades(self):
        self.fetch_button.configure(state="disabled")
        self.status_label.configure(text="Notlar getiriliyor, lütfen bekleyin...", text_color="orange")
        
        # İşlemi ayrı bir thread'de çalıştır ki arayüz donmasın
        thread = threading.Thread(target=self.fetch_grades)
        thread.start()

    def fetch_grades(self):
        try:
            data = get_grades()
            
            # GUI güncellemesini ana thread'de yap
            self.after(0, self.update_ui, data)
        except Exception as e:
            self.after(0, self.show_error, str(e))

    def update_ui(self, data):
        # Önceki sonuçları temizle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if isinstance(data, dict) and "error" in data:
            self.show_error(data["error"])
            return

        if not data:
            label = ctk.CTkLabel(self.scrollable_frame, text="Hiç not bulunamadı.")
            label.pack(pady=10)
        else:
            # Başlıklar
            headers = ["Ders Kodu", "Ders Adı", "Not Bilgisi"]
            for i, header in enumerate(headers):
                label = ctk.CTkLabel(self.scrollable_frame, text=header, font=("Roboto", 16, "bold"))
                label.grid(row=0, column=i, padx=10, pady=10, sticky="w")

            # Verileri listele
            for idx, item in enumerate(data, start=1):
                ctk.CTkLabel(self.scrollable_frame, text=item['ders_kodu']).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.scrollable_frame, text=item['ders_adi']).grid(row=idx, column=1, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.scrollable_frame, text=item['not_bilgisi']).grid(row=idx, column=2, padx=10, pady=5, sticky="w")

        self.status_label.configure(text="İşlem tamamlandı.", text_color="green")
        self.fetch_button.configure(state="normal")

    def show_error(self, message):
        self.status_label.configure(text=f"Hata: {message}", text_color="red")
        self.fetch_button.configure(state="normal")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = App()
    app.mainloop()
