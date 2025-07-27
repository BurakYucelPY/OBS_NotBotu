from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Tarayıcı arkada çalışıyor ama bize gözükmüyor bunla 
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# e-devlet için tc ve şifre
tc = "154********"
sifre = "K********"

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
# e-devlet ile giriş yapıyorsan ve çok fazla denersen muhtemelen bu yazı gelmeyecek bot kontrolüne takılıcaksın 1 saat içinde max 3 defa kullan. İnternetin iyi olmalı :)

# Iframe'e geçiş yap (eğer varsa)
iframe = wait.until(EC.presence_of_element_located((By.ID, "IFRAME1")))
driver.switch_to.frame(iframe)

# Tablodaki satırları bekle
wait.until(EC.presence_of_element_located((By.ID, "grd_not_listesi")))
time.sleep(2)

# Satırları al
satirlar = driver.find_elements(By.XPATH, "//table[@id='grd_not_listesi']//tr")

# konsol için görsel ıvır zıvır
print("\n📘 Notlar Listesi:")
print("-" * 80)
for satir in satirlar:
    hucreler = satir.find_elements(By.XPATH, ".//td")
    if len(hucreler) >= 5:
        ders_kodu = hucreler[1].text.strip()
        ders_adi = hucreler[2].text.strip()
        not_bilgisi = hucreler[4].text.strip()
        print(f"{ders_kodu} | {ders_adi:<50} | {not_bilgisi}")

# Iframe'den çıkış ve kapat
driver.switch_to.default_content()
driver.quit()

# Enter'a basınca kapan
input("Kapatmak için Enter'a basın...")
