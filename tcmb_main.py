import requests
import json
import pandas as pd
import pyodbc
from datetime import datetime

# Bugünün tarihini al ve formatla
today = datetime.now()
formatted_today = today.strftime("%d-%m-%Y")

# API bilgileri
api_key = "EVDS SISTEMI UZERINDEN ALMIS OLDUGUNUZ API ANAHTARI"
series = "TP.REESAVANS.RIO-TP.REESAVANS.AFO"
start_date = "01-01-2015"
end_date = formatted_today
data_format = "json"

# EVDS API'den veri çekme fonksiyonu
def get_evds_data():
    url = f"https://evds2.tcmb.gov.tr/service/evds/series={series}&startDate={start_date}&endDate={end_date}&type={data_format}"
    headers = {'key': api_key}
    
    print(f"İstek URL'si: {url}")
    print(f"İstek tarihleri: {start_date} - {end_date}")
    
    response = requests.get(url, headers=headers)
    print(f"İstek headers: {response.request.headers}")
    response.raise_for_status()
    
    return response.json()

# MSSQL veritabanına bağlanma
def connect_to_mssql():
    server = 'SUNUCU ADINIZ'  # Sunucu adınız
    database = 'VERITABANI ADINIZ'  # Veritabanı adınız
    
    # Windows kimlik doğrulaması kullanıyorsanız:
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    
    # SQL Server kimlik doğrulaması kullanıyorsanız:
    # username = 'KULLANICI_ADI'
    # password = 'SIFRE'
    # conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    return pyodbc.connect(conn_str)

# Ana kod
def main():
    response = None  # response değişkenini tanımlayalım
    
    try:
        # EVDS'den veri çekme
        print("EVDS'den veri çekiliyor...")
        data = get_evds_data()
        
        # Veriyi ekrana yazdır (debug için)
        print(json.dumps(data, indent=2))
        
        # JSON verisini DataFrame'e dönüştürme
        df = pd.DataFrame(data["items"])
        
        # Tarih sütununu datetime formatına dönüştürme
        df['Tarih'] = pd.to_datetime(df['Tarih'], format='%d-%m-%Y')
        
        # Veritabanına bağlanma
        print("MSSQL veritabanına bağlanılıyor...")
        conn = connect_to_mssql()
        cursor = conn.cursor()
        
        # Veri ekleme işlemi
        print("Veriler veritabanına aktarılıyor...")
        inserted_count = 0
        updated_count = 0
        
        for index, row in df.iterrows():
            tarih = row['Tarih'].strftime('%Y-%m-%d')
            reeskont_orani = row.get('TP_REESAVANS_RIO')
            avans_orani = row.get('TP_REESAVANS_AFO')
            
            # Eğer değerler None veya NaN ise, bu kaydı atla
            if pd.isna(reeskont_orani) or pd.isna(avans_orani):
                continue
            
            # String'den float'a dönüştür (API'den string olarak gelebilir)
            try:
                reeskont_orani = float(reeskont_orani)
                avans_orani = float(avans_orani)
            except (ValueError, TypeError):
                print(f"Uyarı: {tarih} tarihindeki değerler dönüştürülemedi. Değerler: {reeskont_orani}, {avans_orani}")
                continue
            
            # Aynı tarih için kayıt var mı kontrol et
            check_sql = "SELECT COUNT(*) FROM ReeskontVeAvansOranlari WHERE Tarih = ?"
            cursor.execute(check_sql, (tarih,))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Güncelleme yap
                update_sql = """
                UPDATE ReeskontVeAvansOranlari 
                SET Reeskont_Orani = ?, Avans_Orani = ?, Kayit_Zamani = GETDATE()
                WHERE Tarih = ?
                """
                cursor.execute(update_sql, (reeskont_orani, avans_orani, tarih))
                updated_count += 1
            else:
                # Yeni kayıt ekle
                insert_sql = """
                INSERT INTO ReeskontVeAvansOranlari (Tarih, Reeskont_Orani, Avans_Orani)
                VALUES (?, ?, ?)
                """
                cursor.execute(insert_sql, (tarih, reeskont_orani, avans_orani))
                inserted_count += 1
        
        # Değişiklikleri kaydet
        conn.commit()
        print(f"Toplam {inserted_count} yeni kayıt eklendi, {updated_count} kayıt güncellendi.")
        
        # Bağlantıyı kapat
        cursor.close()
        conn.close()
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Hatası: {e}")
        if response:  # response değişkeni tanımlanmışsa
            print(f"Yanıt içeriği: {response.text}")
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
