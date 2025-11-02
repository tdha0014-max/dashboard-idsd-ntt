import os
import ast
import sys
import subprocess

# ===== Fungsi cek requirements =====
def parse_requirements(file="requirements.txt"):
    reqs = {}
    if not os.path.exists(file):
        print(f"❌ File {file} tidak ditemukan!")
        return reqs
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "==" in line:
                    pkg, ver = line.split("==")
                    reqs[pkg.lower()] = ver
                else:
                    reqs[line.lower()] = None
    return reqs

# ===== Fungsi cek import di script utama =====
def get_imports(file="idsd_dashboard_ntt.py"):
    imports = set()
    if not os.path.exists(file):
        print(f"❌ File utama {file} tidak ditemukan!")
        return imports
    with open(file, "r") as f:
        node = ast.parse(f.read(), filename=file)
        for n in ast.walk(node):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    imports.add(alias.name.split(".")[0].lower())
            elif isinstance(n, ast.ImportFrom):
                if n.module:
                    imports.add(n.module.split(".")[0].lower())
    return imports

# ===== Fungsi cek kecocokan imports & requirements =====
def check_imports_vs_requirements(imports, reqs):
    missing = []
    for imp in imports:
        if imp not in reqs and imp not in sys.builtin_module_names:
            missing.append(imp)
    return missing

# ===== Fungsi cek file data =====
def check_data_files(files):
    missing = [f for f in files if not os.path.exists(f)]
    return missing

# ===== Fungsi install dependencies sementara untuk cek =====
def test_install_requirements(file="requirements.txt"):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", "-r", file], check=True)
        print("✅ Semua library di requirements.txt bisa diinstall.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ada library di requirements.txt yang gagal diinstall.")
        return False

# ===== Main =====
if __name__ == "__main__":
    print("===== Pengecekan Deploy Streamlit =====\n")

    # 1️⃣ Cek requirements
    reqs = parse_requirements()
    print(f"📌 {len(reqs)} library di requirements.txt ditemukan.")
    test_install_requirements()

    # 2️⃣ Cek imports
    imports = get_imports()
    print(f"📌 {len(imports)} import ditemukan di script utama.")
    missing_libs = check_imports_vs_requirements(imports, reqs)
    if missing_libs:
        print("⚠️ Library berikut digunakan di script tapi tidak ada di requirements.txt:")
        for lib in missing_libs:
            print(f"   - {lib}")
    else:
        print("✅ Semua library di script ada di requirements.txt.\n")

    # 3️⃣ Cek file data penting
    data_files = [
        "data/idsd_data_2023.csv",
        "data/geojson_kecamatan_ntt_official.geojson"
    ]
    missing_files = check_data_files(data_files)
    if missing_files:
        print("⚠️ File data berikut tidak ditemukan di repo:")
        for f in missing_files:
            print(f"   - {f}")
    else:
        print("✅ Semua file data penting ditemukan.\n")

    # 4️⃣ Summary
    if not missing_libs and not missing_files:
        print("🎉 Repo siap deploy ke Streamlit Cloud!")
    else:
        print("❌ Repo perlu diperbaiki sebelum deploy.")
