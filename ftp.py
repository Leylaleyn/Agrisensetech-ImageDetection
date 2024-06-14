import os
import shutil
from ftplib import FTP
from hidden_constant import databaseInformation

def ftp_func(firebase_id):
    # FTP Sunucu Bilgileri
    ftp_server = databaseInformation["ftp_server"]
    ftp_user = databaseInformation["ftp_user"]
    ftp_password = databaseInformation["ftp_password"]
    ftp_directory = f"/public_html/agrisensetech/restAPI/img_weeds/{firebase_id}"

    # FTP bağlantısını oluşturun
    ftp = FTP(ftp_server)
    ftp.login(user=ftp_user, passwd=ftp_password)

    # Sunucudaki klasöre gidin
    try:
        ftp.cwd(ftp_directory)
    except Exception as err:
        if str(err.args[0].split()[0]) == "550":
            ftp.mkd(ftp_directory)
    finally:
        ftp.cwd(ftp_directory)

    # Sonuç klasöründeki dosyaları yükleyin
    local_directory = "results"

    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            local_path = os.path.join(root, filename)
            # remote_path = os.path.join(ftp_directory, filename)
            remote_path = ftp_directory + "/" + filename

            with open(local_path, 'rb') as file:
                ftp.storbinary(f'STOR {remote_path}', file)
                print(f"[INFO] Uploaded {filename}")

    ftp.quit()
    print("[INFO].. All images have been uploaded to the server")

    # Sonuç klasörünü sil
    shutil.rmtree(local_directory)
    print("[INFO].. Results folder has been deleted from the local system")
