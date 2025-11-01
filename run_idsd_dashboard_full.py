import subprocess
import socket
import time
import webbrowser
from pyngrok import ngrok, exception
import pyqrcode

def find_free_port(start_port=8508, max_port=8600):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    raise RuntimeError("Tidak ada port kosong tersedia")

def start_dashboard():
    # Tutup tunnel ngrok lama jika ada
    try:
        ngrok.kill()
    except exception.PyngrokNgrokError:
        pass

    # Tentukan port kosong
    port = find_free_port()
    print(f"Menjalankan Streamlit di port: {port}")

    # Jalankan ngrok
    public_url = ngrok.connect(port)
    print(f"Ngrok URL publik: {public_url.public_url}")

    # Buka URL di browser desktop
    webbrowser.open(public_url.public_url)

    # Buat QR code untuk HP
    qr = pyqrcode.create(public_url.public_url)
    print("\nScan QR code ini dari HP untuk buka dashboard:")
    print(qr.terminal(quiet_zone=1))

    # Loop auto-restart
    while True:
        print("\nMenjalankan Streamlit...")
        process = subprocess.Popen(
            ["streamlit", "run", "idsd_dashboard_ntt.py", f"--server.port={port}"]
        )
        process.wait()
        print("Streamlit berhenti, akan restart dalam 3 detik...")
        time.sleep(3)

if __name__ == "__main__":
    start_dashboard()
