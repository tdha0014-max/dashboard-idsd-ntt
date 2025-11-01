import os
import pandas as pd

def pilih_file_csv(folder):
    # tampilkan semua file CSV di folder
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    if not files:
        print("❌ Tidak ada file CSV ditemukan di folder proyek.")
        return None

    print("\n📄 File CSV yang ditemukan:")
    for i, f in enumerate(files, start=1):
        print(f"{i}. {f}")

    # pilih file berdasarkan nomor
    try:
        pilihan = int(input("\nPilih nomor file data_2023 yang benar: "))
        return os.path.join(folder, files[pilihan - 1])
    except (ValueError, IndexError):
        print("❌ Pilihan tidak valid.")
        return None

def sesuaikan_data():
    project_dir = os.getcwd()
    downloads = os.path.expanduser("~/Downloads")

    # file 2024 langsung ambil dari Downloads
    file_2024 = os.path.join(downloads, "Data_2024.xlsx")
    if not os.path.exists(file_2024):
        print(f"❌ File tidak ditemukan: {file_2024}")
        return

    # pilih file 2023 dari folder proyek
    file_2023 = pilih_file_csv(project_dir)
    if not file_2023:
        return

    print("\n📂 Membaca file...")
    df_2024 = pd.read_excel(file_2024)
    df_2023 = pd.read_csv(file_2023)

    print("🔧 Mengubah tanda koma menjadi titik...")
    for col in df_2024.columns:
        if df_2024[col].dtype == "object":
            df_2024[col] = df_2024[col].astype(str).str.replace(",", ".", regex=False)

    print("🔢 Mengonversi nilai numerik...")
    for col in df_2024.columns:
        df_2024[col] = pd.to_numeric(df_2024[col], errors="ignore")

    print("🧩 Menyamakan struktur kolom dengan data 2023...")
    for col in df_2023.columns:
        if col not in df_2024.columns:
            df_2024[col] = 0

    df_2024 = df_2024[df_2023.columns]

    output_file = os.path.join(project_dir, "Data_2024_sesuai_2023.xlsx")
    df_2024.to_excel(output_file, index=False)

    print(f"\n✅ File '{output_file}' berhasil dibuat!")
    print("   Struktur dan urutan kolom sudah sama dengan data 2023.\n")

if __name__ == "__main__":
    sesuaikan_data()
