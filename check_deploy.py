import subprocess
import sys
import os


# ===== Cek requirements =====
def check_requirements(file="requirements.txt"):
    if not os.path.exists(file):
        print(f"❌ File {file} tidak ditemukan!")
        return False
    print(f"✅ File {file} ditemukan.")

    # Install dependencies secara "check-only"
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", "-r", file], check=True)
        print("✅ Semua library di requirements.txt bisa diinstall.")
    except subprocess.CalledProcessError:
        print("❌ Ada library di requirements.txt yang gagal diinstall.")
        return False
    return True


# ===== Cek file utama =====
def check_main_file(file="idsd_dashboard_ntt.py"):
    if not os.path.exists(file):
        print(f"❌ File utama {file} tidak ditemukan di repo!")
        return False
    print(f"✅ File utama {file} ditemukan.")
    return True


# ===== Cek file data penting =====
def check_data_files(files):
    all_ok = True
    for f in files:
        if not os.path.exists(f):
            print(f"❌ File data {f} tidak ditemukan.")
            all_ok = False
        else:
            print(f"✅ File data {f} ditemukan.")
    return all_ok


# ===== Main check =====
if __name__ == "__main__":
    print("===== Pengecekan sebelum deploy =====")
    requirements_ok = check_requirements()
    main_ok = check_main_file()
    data_ok = check_data_files([
        "data/idsd_data_2023.csv",
        "data/geojson_kecamatan_ntt_official.geojson"
    ])

    if requirements_ok and main_ok and data_ok:
        print("\n🎉 Semua file dan dependency siap untuk deploy Streamlit Cloud!")
    else:
        print("\n⚠️ Pengecekan menemukan masalah. Periksa kembali file/data/dependency Anda.")
