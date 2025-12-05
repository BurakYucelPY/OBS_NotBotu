from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Tarayıcı arkada çalışıyor ama bize gözükmüyor bunla 
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# .env dosyasından bilgileri al (Kütüphane yoksa manuel oku)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

# e-devlet için tc ve şifre
tc = os.getenv("TC_KIMLIK")
sifre = os.getenv("E_DEVLET_SIFRE")

def get_grades():
    if not tc or not sifre:
        return {"error": "UYARI: .env dosyasında TC veya Şifre bulunamadı! Lütfen .env dosyasını düzenleyin."}

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 40)

        # Kendi Okul Adresinizi girin
        driver.get("https://obs.karatay.edu.tr/oibs/std/login.aspx") # okul giriş sayfası url linki
        wait.until(EC.element_to_be_clickable((By.ID, "btnEdevletLogin"))).click() # robot doğrulama var ise e-devlet ile giriş yap
        time.sleep(3)

        # e-devlet giriş bilgilerini doldur
        wait.until(EC.presence_of_element_located((By.ID, "tridField"))).send_keys(tc)
        driver.find_element(By.ID, "egpField").send_keys(sifre)
        driver.find_element(By.NAME, "submitButton").click()

        # dot listesi sayfasına git (Linkleri kendi okul sistemine göre ayarla)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//p[contains(text(),'Ders ve Dönem İşlemleri')]"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[.//p[contains(text(),'Not Listesi')]]"))).click()
        print("📌 Not Listesi'ne girildi, tablo yükleniyor...")
        
        # Iframe'e geçiş yap (eğer varsa)
        iframe = wait.until(EC.presence_of_element_located((By.ID, "IFRAME1")))
        driver.switch_to.frame(iframe)

        # Tablodaki satırları bekle
        wait.until(EC.presence_of_element_located((By.ID, "grd_not_listesi")))
        time.sleep(2)

        # Satırları al
        satirlar = driver.find_elements(By.XPATH, "//table[@id='grd_not_listesi']//tr")
        
        results = []
        for satir in satirlar:
            hucreler = satir.find_elements(By.XPATH, ".//td")
            if len(hucreler) >= 5:
                ders_kodu = hucreler[1].text.strip()
                ders_adi = hucreler[2].text.strip()
                not_bilgisi = hucreler[4].text.strip()
                results.append({
                    "ders_kodu": ders_kodu,
                    "ders_adi": ders_adi,
                    "not_bilgisi": not_bilgisi
                })
        
        driver.switch_to.default_content()
        driver.quit()
        return results

    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return {"error": str(e)}

if __name__ == "__main__":
    data = get_grades()
    if isinstance(data, dict) and "error" in data:
        print(data["error"])
    else:
        # konsol için görsel ıvır zıvır
        print("\n📘 Notlar Listesi:")
        print("-" * 80)
        for item in data:
            print(f"{item['ders_kodu']} | {item['ders_adi']:<50} | {item['not_bilgisi']}")
        
        # Enter'a basınca kapan
        input("Kapatmak için Enter'a basın...")
