from pyngrok import ngrok
import subprocess
import time

# Start streamlit
streamlit_process = subprocess.Popen([
    "streamlit", "run", "idsd_dashboard_ntt.py",
    "--server.port", "8501"
])

# Wait for streamlit to start
time.sleep(5)

# Create ngrok tunnel
public_url = ngrok.connect(8501)
print("=" * 70)
print("🌐 Dashboard sudah online!")
print("=" * 70)
print(f"URL Publik: {public_url}")
print("=" * 70)
print("Tekan Ctrl+C untuk stop")
print("=" * 70)

try:
    streamlit_process.wait()
except KeyboardInterrupt:
    streamlit_process.terminate()
    ngrok.kill()