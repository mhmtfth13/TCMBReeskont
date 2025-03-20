# Reeskont ve Avans Oranları Veri Çekme Projesi
Bu proje, Türkiye Cumhuriyet Merkez Bankası (TCMB) Elektronik Veri Dağıtım Sistemi'nden (EVDS) reeskont ve avans oranlarını otomatik olarak çeken ve bir MSSQL veritabanına kaydeden bir Python uygulamasıdır.

## Özellikler
- TCMB EVDS API kullanarak güncel reeskont ve avans oranlarını çekme
- Verileri MSSQL veritabanına kaydetme
- Mevcut kayıtları güncelleme ve yeni kayıtlar ekleme
- Hata durumunda loglama ve bildirim gönderme
- Windows Görev Zamanlayıcı ile otomatik çalıştırma
## Gereksinimler
- Python 3.6 veya daha yeni bir sürüm
- Aşağıdaki Python kütüphaneleri:
  * requests
  * pandas
  * pyodbc
  * MSSQL Server veritabanı
- TCMB EVDS API anahtarı
## Kurulum
- Projeyi bilgisayarınıza indirin veya klonlayın
- Gerekli Python kütüphanelerini yükleyin:
- ``` bash uv pip install requirements.txt ```
- Veritabanında gerekli tabloyu oluşturun:
  ``` sql 
  CREATE TABLE ReeskontVeAvansOranlari (
    ID int IDENTITY(1,1) PRIMARY KEY,
    Tarih date NOT NULL,
    Reeskont_Orani float NOT NULL,
    Avans_Orani float NOT NULL,
    Kayit_Zamani datetime DEFAULT GETDATE()
  );
  ```
- tcmb_main.py dosyasını açın ve aşağıdaki bilgileri güncelleyin
- API anahtarı
- Veritabanı sunucu adı
- Veritabanı adı
- Gerekirse veritabanı kullanıcı adı ve şifresi (windows auth kullanmiyorsaniz..)

## Kullanım
Scripti manuel olarak çalıştırmak için:
``` python python tcmb_main.py ```
  ### Otomatik Çalıştırma (Windows)
  - Bir .bat dosyası oluşturun (örneğin tcmb_main.bat):
  - ``` tcmb_main.bat
    @echo off
    echo EVDS Veri Çekme İşlemi Başlıyor - %date% %time%
    cd /d C:\Path\To\Your\Script\Folder
    C:\Path\To\Python\python.exe evds_veri_cek.py
    echo İşlem Tamamlandı - %date% %time%
    ```
  - Windows Görev Zamanlayıcısı'nı açın
  - "Temel Görev Oluştur" seçeneğini seçin
  - Göreve bir isim verin (örn. "EVDS Veri Çekme")
  - Tetikleyici olarak "Günlük" seçin ve bir saat belirleyin
  - Eylem olarak "Program başlat" seçin
  - Program/komut dosyası alanına .bat dosyasının tam yolunu girin
  - Görevi kaydedin
