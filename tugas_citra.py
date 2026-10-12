
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import csv


# ============================================================
# 1. PENGATURAN FOLDER
# ============================================================

# Folder tempat gambar ijazah
folder_citra = Path("citra")

# Folder untuk menyimpan hasil
folder_hasil = Path("hasil")

# Membuat folder hasil jika belum ada
folder_hasil.mkdir(exist_ok=True)


# ============================================================
# 2. MENCARI SEMUA FILE GAMBAR
# ============================================================

ekstensi_gambar = ["*.jpg"]

daftar_file = []

for ekstensi in ekstensi_gambar:
    daftar_file.extend(folder_citra.glob(ekstensi))

# Urutkan nama file
daftar_file = sorted(daftar_file)


# Mengecek apakah gambar ditemukan
if len(daftar_file) == 0:
    print("Tidak ada gambar ditemukan!")
    print("Pastikan gambar berada di dalam folder 'citra'.")
    exit()


print("=" * 60)
print("PROGRAM ANALISIS CITRA DOKUMEN IJAZAH")
print("=" * 60)
print(f"Jumlah gambar ditemukan : {len(daftar_file)}")
print()


# ============================================================
# 3. LIST UNTUK MENYIMPAN HASIL ANALISIS
# ============================================================

hasil_analisis = []


# ============================================================
# 4. PROSES SETIAP GAMBAR
# ============================================================

for nomor, file_gambar in enumerate(daftar_file, start=1):

    print("-" * 60)
    print(f"Memproses Citra {nomor}")
    print(f"Nama file : {file_gambar.name}")

    # --------------------------------------------------------
    # Membaca gambar RGB
    # --------------------------------------------------------

    gambar_rgb = Image.open(file_gambar).convert("RGB")

    # Mengubah PIL Image menjadi array NumPy
    rgb = np.array(gambar_rgb)

    # --------------------------------------------------------
    # Konversi RGB ke Grayscale
    #
    # Rumus:
    # Gray = 0.299R + 0.587G + 0.114B
    # --------------------------------------------------------

    grayscale = (
        0.299 * rgb[:, :, 0]
        + 0.587 * rgb[:, :, 1]
        + 0.114 * rgb[:, :, 2]
    ).astype(np.uint8)

    # --------------------------------------------------------
    # Statistik grayscale
    # --------------------------------------------------------

    mean_gray = np.mean(grayscale)
    min_gray = np.min(grayscale)
    max_gray = np.max(grayscale)
    std_gray = np.std(grayscale)

    # Persentase piksel sangat gelap
    persen_gelap = np.mean(grayscale < 50) * 100

    # Persentase piksel sangat terang
    persen_terang = np.mean(grayscale > 240) * 100

    # --------------------------------------------------------
    # Statistik masing-masing kanal RGB
    # --------------------------------------------------------

    mean_r = np.mean(rgb[:, :, 0])
    mean_g = np.mean(rgb[:, :, 1])
    mean_b = np.mean(rgb[:, :, 2])

    # --------------------------------------------------------
    # Mendeteksi color cast sederhana
    # --------------------------------------------------------

    selisih_rg = abs(mean_r - mean_g)
    selisih_rb = abs(mean_r - mean_b)
    selisih_gb = abs(mean_g - mean_b)

    color_cast = "Tidak signifikan"

    if mean_g > mean_r + 15 and mean_g > mean_b + 10:
        color_cast = "Dominasi hijau"

    elif mean_r > mean_g + 15 and mean_r > mean_b + 10:
        color_cast = "Dominasi merah"

    elif mean_b > mean_r + 15 and mean_b > mean_g + 10:
        color_cast = "Dominasi biru"

    elif mean_r > mean_b + 20 and mean_g > mean_b + 20:
        color_cast = "Dominasi kuning"


    # ========================================================
    # 5. IDENTIFIKASI KONDISI CITRA
    # ========================================================

    masalah = []
    enhancement = []

    # --------------------------------------------------------
    # Terlalu gelap
    # --------------------------------------------------------

    if mean_gray < 100:
        masalah.append("Terlalu gelap")
        enhancement.append("Gamma Correction (gamma < 1)")

    # --------------------------------------------------------
    # Cenderung gelap
    # --------------------------------------------------------

    elif mean_gray < 170:
        masalah.append("Cenderung gelap")
        enhancement.append("Gamma Correction (gamma < 1)")

    # --------------------------------------------------------
    # Terlalu terang
    # --------------------------------------------------------

    if mean_gray > 230:
        masalah.append("Terlalu terang")
        enhancement.append("Gamma Correction (gamma > 1)")

    elif mean_gray > 210:
        masalah.append("Cenderung terlalu terang")
        enhancement.append("Gamma Correction (gamma > 1)")


    # --------------------------------------------------------
    # Contrast rendah
    #
    # Standar deviasi kecil menunjukkan intensitas
    # terkonsentrasi pada rentang yang sempit.
    # --------------------------------------------------------

    if std_gray < 25:
        masalah.append("Contrast relatif rendah")
        enhancement.append("Contrast Stretching")


    # --------------------------------------------------------
    # Contrast sedang
    # --------------------------------------------------------

    elif std_gray < 35:
        masalah.append("Contrast sedang")


    # --------------------------------------------------------
    # Contrast tinggi
    # --------------------------------------------------------

    else:
        masalah.append("Contrast relatif tinggi")


    # --------------------------------------------------------
    # Noise
    #
    # Pemeriksaan noise di sini hanya indikasi sederhana.
    # Deteksi visual tetap diperlukan.
    # --------------------------------------------------------

    if persen_gelap > 0.05:
        masalah.append("Terdapat piksel sangat gelap/noise")

    if persen_terang > 10:
        masalah.append("Banyak piksel sangat terang")


    # --------------------------------------------------------
    # Color cast
    # --------------------------------------------------------

    if color_cast != "Tidak signifikan":
        masalah.append(color_cast)
        enhancement.append("Color Correction")


    # --------------------------------------------------------
    # Jika contrast cukup tetapi pencahayaan ekstrem,
    # CLAHE bisa digunakan.
    # --------------------------------------------------------

    if std_gray >= 25 and std_gray < 45:
        enhancement.append("CLAHE")


    # --------------------------------------------------------
    # Menghilangkan rekomendasi duplikat
    # --------------------------------------------------------

    masalah = list(dict.fromkeys(masalah))
    enhancement = list(dict.fromkeys(enhancement))

    # Jika tidak ada enhancement
    if len(enhancement) == 0:
        enhancement.append("Tidak membutuhkan enhancement besar")


    # ========================================================
    # 6. MENAMPILKAN HASIL ANALISIS DI TERMINAL
    # ========================================================

    print(f"Mean grayscale       : {mean_gray:.2f}")
    print(f"Minimum intensitas   : {min_gray}")
    print(f"Maksimum intensitas  : {max_gray}")
    print(f"Standar deviasi      : {std_gray:.2f}")

    print(f"Mean R               : {mean_r:.2f}")
    print(f"Mean G               : {mean_g:.2f}")
    print(f"Mean B               : {mean_b:.2f}")

    print(f"Color cast            : {color_cast}")

    print("Masalah citra:")
    for m in masalah:
        print(f"  - {m}")

    print("Rekomendasi enhancement:")
    for e in enhancement:
        print(f"  - {e}")


    # ========================================================
    # 7. MENAMPILKAN CITRA RGB DAN GRAYSCALE
    # ========================================================

    plt.figure(figsize=(12, 5))

    # Citra RGB
    plt.subplot(1, 2, 1)
    plt.imshow(rgb)
    plt.title(f"Citra {nomor} - RGB")
    plt.axis("off")

    # Citra Grayscale
    plt.subplot(1, 2, 2)
    plt.imshow(grayscale, cmap="gray")
    plt.title(f"Citra {nomor} - Grayscale")
    plt.axis("off")

    plt.tight_layout()

    # Menyimpan gambar
    nama_hasil = folder_hasil / f"citra_{nomor}_rgb_grayscale.png"
    plt.savefig(nama_hasil, dpi=150, bbox_inches="tight")

    plt.show()
    plt.close()


    # ========================================================
    # 8. HISTOGRAM RGB
    # ========================================================

    plt.figure(figsize=(10, 5))

    plt.hist(
        rgb[:, :, 0].ravel(),
        bins=256,
        range=(0, 255),
        histtype="step",
        label="Red (R)"
    )

    plt.hist(
        rgb[:, :, 1].ravel(),
        bins=256,
        range=(0, 255),
        histtype="step",
        label="Green (G)"
    )

    plt.hist(
        rgb[:, :, 2].ravel(),
        bins=256,
        range=(0, 255),
        histtype="step",
        label="Blue (B)"
    )

    plt.title(f"Histogram RGB - Citra {nomor}")
    plt.xlabel("Intensitas Piksel")
    plt.ylabel("Jumlah Piksel")
    plt.legend()
    plt.grid(alpha=0.2)

    plt.tight_layout()

    nama_hist_rgb = folder_hasil / f"histogram_rgb_{nomor}.png"
    plt.savefig(nama_hist_rgb, dpi=150, bbox_inches="tight")

    plt.show()
    plt.close()


    # ========================================================
    # 9. HISTOGRAM GRAYSCALE
    # ========================================================

    plt.figure(figsize=(10, 5))

    plt.hist(
        grayscale.ravel(),
        bins=256,
        range=(0, 255)
    )

    plt.title(f"Histogram Grayscale - Citra {nomor}")
    plt.xlabel("Intensitas Piksel")
    plt.ylabel("Jumlah Piksel")

    # Garis rata-rata
    plt.axvline(
        mean_gray,
        linestyle="--",
        label=f"Mean = {mean_gray:.2f}"
    )

    plt.legend()
    plt.grid(alpha=0.2)

    plt.tight_layout()

    nama_hist_gray = folder_hasil / f"histogram_grayscale_{nomor}.png"
    plt.savefig(nama_hist_gray, dpi=150, bbox_inches="tight")

    plt.show()
    plt.close()


    # ========================================================
    # 10. SIMPAN DATA ANALISIS
    # ========================================================

    hasil_analisis.append({
        "Citra": f"Citra {nomor}",
        "Nama File": file_gambar.name,
        "Mean": round(mean_gray, 2),
        "Minimum": int(min_gray),
        "Maksimum": int(max_gray),
        "Standar Deviasi": round(std_gray, 2),
        "Mean R": round(mean_r, 2),
        "Mean G": round(mean_g, 2),
        "Mean B": round(mean_b, 2),
        "Color Cast": color_cast,
        "Masalah": "; ".join(masalah),
        "Enhancement": "; ".join(enhancement)
    })


# ============================================================
# 11. MEMBUAT FILE CSV
# ============================================================

file_csv = folder_hasil / "hasil_analisis.csv"

with open(file_csv, "w", newline="", encoding="utf-8") as file:

    fieldnames = [
        "Citra",
        "Nama File",
        "Mean",
        "Minimum",
        "Maksimum",
        "Standar Deviasi",
        "Mean R",
        "Mean G",
        "Mean B",
        "Color Cast",
        "Masalah",
        "Enhancement"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for data in hasil_analisis:
        writer.writerow(data)


# ============================================================
# 12. SELESAI
# ============================================================

print()
print("=" * 60)
print("SEMUA CITRA SELESAI DIPROSES")
print("=" * 60)

print()
print("Hasil disimpan di folder:")
print(folder_hasil)

print()
print("File analisis:")
print(file_csv)