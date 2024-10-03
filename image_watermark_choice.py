import cv2
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# Fungsi untuk mendapatkan warna RGB dari kode hex
def get_color_from_string(color_str):
    """Mengambil warna RGB dari input string hex (#RRGGBB)."""
    color_str = color_str.lstrip('#')  # Menghilangkan tanda '#'
    if len(color_str) != 6:
        raise ValueError("Input hex warna harus dalam format #RRGGBB.")
    
    # Mengonversi nilai hex menjadi RGB
    r = int(color_str[0:2], 16)
    g = int(color_str[2:4], 16)
    b = int(color_str[4:6], 16)
    
    return (b, g, r)  # OpenCV menggunakan format BGR, jadi kita urutkan b, g, r

def preprocess_image(image):
    """Melakukan preprocessing pada gambar."""
    gamma_corrected = adjust_gamma(image, gamma=1.2)
    sharpened_image = sharpen_image(gamma_corrected)
    return sharpened_image

def adjust_gamma(image, gamma=1.0):
    """Menerapkan penyesuaian gamma pada gambar."""
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def sharpen_image(image):
    """Melakukan penajaman pada gambar menggunakan Unsharp Masking."""
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)
    return sharpened

def preprocess_logo(logo, image_size, scale_factor=0.2):
    """Melakukan preprocessing pada logo: mengubah ukuran dan menghilangkan latar belakang."""
    # Mengubah ukuran logo agar proporsional dengan gambar
    scale_size = int(min(image_size) * scale_factor)
    logo = cv2.resize(logo, (scale_size, scale_size), interpolation=cv2.INTER_AREA)
    logo_rgba = remove_background(logo)
    return logo_rgba

def remove_background(logo):
    """Menghilangkan latar belakang dari logo menggunakan thresholding."""
    gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    logo = cv2.bitwise_and(logo, logo, mask=mask)
    b, g, r = cv2.split(logo)
    alpha_channel = mask
    logo_rgba = cv2.merge((b, g, r, alpha_channel))
    return logo_rgba

def add_text_watermark(image, text, position_str, font_color=(255, 255, 255), scale_factor=0.3, thickness=2, opacity=0.6):
    """Menambahkan watermark teks ke gambar dengan skala otomatis pada posisi yang ditentukan."""
    image_h, image_w, _ = image.shape
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Menentukan ukuran font berdasarkan scale_factor
    #font_scale = scale_factor * min(image_w, image_h)
    #font_scale=scale_factor

    # Menentukan ukuran font berdasarkan scale_factor
    font_scale = scale_factor * min(image_w, image_h) / 150  # Menyesuaikan dengan ukuran gambar

    # Tentukan ukuran teks dan baseline
    text_size, baseline = cv2.getTextSize(text, font, font_scale, thickness)
    text_w, text_h = text_size

    # Menentukan posisi watermark
    positions = {
        2 : (image_w - text_w - 10, text_h + 10),               #"kanan atas"
        5 : (image_w - text_w - 10, (image_h + text_h) // 2),   #"kanan tengah"
        8 : (image_w - text_w - 10, image_h - 10),              #"kanan bawah"
        0 : (10, text_h + 10),                                  #"kiri atas"
        3 : (10, (image_h + text_h) // 2),                      #"kiri tengah"
        6 : (10, image_h - 10),                                 #"kiri bawah"
        4 : ((image_w - text_w) // 2, (image_h + text_h) // 2), #"Tengah"
        1 : ((image_w - text_w) // 2, text_h + 10),             # Posisi baru: Tengah atas
        7 : ((image_w - text_w) // 2, image_h - 10)             # Posisi baru: Tengah bawah
    }

    # Ambil posisi dari dictionary atau gunakan default
    #position = positions.get(position_str.lower(), (image_w - text_w - 10, image_h - 10))
    position = positions.get(position_str, (image_w - text_w - 10, image_h - 10))

    # Buat overlay untuk menempatkan teks dengan transparansi
    overlay = image.copy()

    # Menambahkan teks watermark di overlay
    cv2.putText(overlay, text, position, font, font_scale, font_color, thickness, cv2.LINE_AA)

    # Menggabungkan overlay dengan gambar asli menggunakan opacity
    cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    return image

def add_logo_watermark(image, logo, position_str, opacity):
    """Menambahkan watermark logo ke gambar dengan transparansi di posisi yang ditentukan."""
    if logo is None:
        raise ValueError("Logo tidak ditemukan.")

    # Dapatkan posisi berdasarkan input string
    position = get_watermark_position(image, logo, position_str)

    # Tambahkan logo ke gambar dengan transparansi
    for c in range(0, 3):
        image[position[1]:position[1]+logo.shape[0], position[0]:position[0]+logo.shape[1], c] = \
            (logo[:, :, c] * (logo[:, :, 3] / 255.0 * opacity) +
             image[position[1]:position[1]+logo.shape[0], position[0]:position[0]+logo.shape[1], c] *
             (1.0 - logo[:, :, 3] / 255.0 * opacity))

    return image

def get_watermark_position(image, watermark, position_str):
    """Mengembalikan koordinat (x, y) berdasarkan string posisi yang diberikan."""
    image_h, image_w, _ = image.shape
    logo_h, logo_w, _ = watermark.shape

    positions = {
        2 : (image_w - logo_w, 0),#"kanan atas"
        5 : (image_w - logo_w, (image_h - logo_h) // 2),#"kanan tengah"
        8 : (image_w - logo_w, image_h - logo_h),#"kanan bawah"
        0 : (0, 0),#"kiri atas"
        3 : (0, (image_h - logo_h) // 2),#"kiri tengah"
        6 : (0, image_h - logo_h),#"kiri bawah"
        4 : ((image_w - logo_w) // 2, (image_h - logo_h) // 2),#Tengah
        1 : ((image_w - logo_w) // 2, logo_h + 10),  # Posisi baru: Tengah atas
        7 : ((image_w - logo_w) // 2, image_h - 10)  # Posisi baru: Tengah bawah
    }

    #eturn positions.get(position_str.lower(), (image_w - logo_w, image_h - logo_h))
    return positions.get(position_str, (image_w - logo_w, image_h - logo_h))

def calculate_saliency(image):
    """Menghitung peta saliency untuk gambar."""
    saliency = cv2.saliency.StaticSaliencyFineGrained_create()
    (success, saliencyMap) = saliency.computeSaliency(image)
    return saliencyMap

def find_optimal_position(image, watermark_size):
    """Menemukan posisi optimal untuk menempatkan watermark berdasarkan analisis gambar."""
    saliencyMap = calculate_saliency(image)
    saliencyMap = cv2.GaussianBlur(saliencyMap, (5, 5), 0)

    # Invert saliency map untuk mencari area yang paling "tidak penting"
    inverted_map = 1.0 - saliencyMap

    # Rescale inverted map untuk ukuran watermark
    h, w = watermark_size

    # Pastikan ukuran watermark tidak lebih besar dari gambar
    if w >= image.shape[1] or h >= image.shape[0]:
        raise ValueError("Ukuran watermark lebih besar dari gambar. Sesuaikan ukuran watermark.")

    if w >= image.shape[1] or h >= image.shape[0]:
        scale_factor = min(image.shape[1] / w, image.shape[0] / h)
        w = int(w * scale_factor)
        h = int(h * scale_factor)
        watermark_size = (w, h)  # Update ukuran watermark

    resized_map = cv2.resize(inverted_map, (image.shape[1] - w, image.shape[0] - h))

    # Temukan posisi dengan nilai terkecil (paling gelap di inverted map)
    min_val, _, min_loc, _ = cv2.minMaxLoc(resized_map)

    optimal_position = (min_loc[0], min_loc[1])

    return optimal_position

def add_watermark_with_auto_position(image, watermark, watermark_type='logo', font_color=(255, 255, 255), font_scale=1, thickness=2, opacity=1.0):
    """Menambahkan watermark pada posisi optimal di gambar."""
    if watermark_type == 'logo':
        h, w, _ = watermark.shape
        optimal_position = find_optimal_position(image, (h, w))

        # Menambahkan logo di posisi optimal dengan opacity
        overlay = image.copy()
        for c in range(0, 3):
            overlay[optimal_position[1]:optimal_position[1]+h, optimal_position[0]:optimal_position[0]+w, c] = \
                (watermark[:, :, c] * (watermark[:, :, 3] / 255.0) +
                 image[optimal_position[1]:optimal_position[1]+h, optimal_position[0]:optimal_position[0]+w, c] *
                 (1.0 - watermark[:, :, 3] / 255.0))

        # Menggabungkan logo dengan transparansi
        cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    elif watermark_type == 'text':
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(watermark, font, font_scale, thickness)
        text_w, text_h = text_size

        optimal_position = find_optimal_position(image, (text_w, text_h))

        # Pastikan posisi tidak keluar dari batas gambar
        optimal_position = (max(optimal_position[0], 0),
                            max(optimal_position[1], 0))
        optimal_position = (min(optimal_position[0], image.shape[1] - text_w),
                            min(optimal_position[1], image.shape[0] - text_h))

        # Buat overlay untuk menempatkan teks dengan transparansi
        overlay = image.copy()

        # Menambahkan teks watermark di overlay
        cv2.putText(overlay, watermark, optimal_position, font, font_scale, font_color, thickness, cv2.LINE_AA)

        # Menggabungkan overlay dengan gambar asli menggunakan opacity
        cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    return image

import os
# Fungsi utama untuk menambahkan watermark pada gambar
def main(image_path, watermark_type, output_path,text=None, logo_path=None, position_str=None, opacity=None, font_color=(255, 255, 255), scale_factor=0.3, thickness=2, output_format='png'):
    # Load image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Gambar tidak ditemukan di path: {image_path}")

    # Preprocess image
    preprocessed_image = preprocess_image(image)

    if watermark_type == 'text':
        if text is None:
            raise ValueError("Text harus disediakan untuk watermark jenis teks.")
        if position_str == -1:
            image = add_watermark_with_auto_position(preprocessed_image, text, watermark_type='text', font_color=font_color, thickness=thickness, opacity=opacity)
        else:
            image = add_text_watermark(preprocessed_image, text, position_str, font_color=font_color, opacity=opacity, thickness=thickness)
    elif watermark_type == 'logo':
        if logo_path is None:
            raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")

        # Load dan preprocess logo
        logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=preprocessed_image.shape[:2], scale_factor=scale_factor)

        if position_str == -1:
            image = add_watermark_with_auto_position(preprocessed_image, logo, watermark_type='logo', opacity=opacity)
        else:
            image = add_logo_watermark(preprocessed_image, logo, position_str, opacity=opacity)

    # Membuat folder "Watermarked Image" jika belum ada
    #output_folder = "Watermarked Image"
    output_folder = output_path
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Menambahkan "Watermark" pada nama file
    base_name = os.path.basename(image_path)  # Ambil nama file dari path
    name, ext = os.path.splitext(base_name)  # Pisahkan nama dan ekstensi
    output_filename = os.path.join(output_folder, f'Watermark_{name}.{output_format}')  # Buat nama file baru dalam folder "Watermarked Image"

    # Simpan gambar dengan watermark
    if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
        cv2.imwrite(output_filename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])  # Simpan sebagai JPG
    elif output_format.lower() == 'png':
        cv2.imwrite(output_filename, image)  # Simpan sebagai PNG
    else:
        raise ValueError("Format output tidak didukung. Silakan pilih 'jpg' atau 'png'.")

    return output_filename

# Memastikan font_color diambil dari string warna dan dikonversi ke format tuple BGR
#def process_multiple_files(file_paths, watermark_type, font_scale=1,text=None, logo_path=None, scale_factor=None, position_str="kanan bawah", opacity=None, font_color="putih", output_format='png'):
def process_multiple_files(file_paths, watermark_type,output_path, text=None, thickness=None,logo_path=None, scale_factor=0.3, position_str=9, opacity=None, font_color="putih", output_format='png'):
    # Konversi warna string ke tuple BGR menggunakan get_color_from_string
    # Konversi warna string ke tuple BGR menggunakan get_color_from_string
    font_color_bgr = get_color_from_string(font_color)

    for file_path in file_paths:
        if os.path.isfile(file_path):
            print(f"Memproses {file_path}...")
            output_image = main(
                image_path=file_path,
                output_path=output_path,
                watermark_type=watermark_type,
                text=text,
                scale_factor=scale_factor,
                logo_path=logo_path,
                position_str=position_str,
                opacity=opacity,
                font_color=font_color_bgr,  # Pastikan warna dikonversi ke BGR
                output_format=output_format
            )
            print(f"Gambar dengan watermark disimpan sebagai {output_image}")

# Fungsi untuk memilih file menggunakan dialog file picker dari tkinter
# def select_files():
#     Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
#     file_paths = askopenfilenames(title="Pilih Gambar", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
#     return file_paths

# # Memilih file secara langsung dengan tkinter
# file_paths = select_files()

# # Jika ada file yang dipilih
# if file_paths:
#     # Proses setiap file yang dipilih
#     process_multiple_files(
#         file_paths=file_paths,
#         watermark_type='text',
#         output_path="Watermark Content",
#         text='Contoh',  # Contoh teks watermark
#         position_str=8,#"kanan bawah",
#         opacity=0.6,
#         #font_scale=0.5,
#         scale_factor=0.5,
#         font_color='#49FFCE',  # Input warna sebagai string
#         output_format='png'  # Format output (bisa 'png' atau 'jpg')
#     )
# else:
#     print("Tidak ada file yang dipilih.")

# Jika ada file yang dipilih
# if file_paths:
#     # Proses setiap file yang dipilih
#     process_multiple_files(
#         file_paths=file_paths,
#         watermark_type='logo',
#         logo_path='C:\\D\Bootcamp\\ICStar Hackathon 2024\\Project Watermark\\BackEnd Watermark\\Gambar\\watermark logo.png',  # Sesuaikan dengan path logo Anda
#         position_str="kanan bawah",
#         opacity=0.5,
#         scale_factor=0.3,
#         font_color='merah',  # Input warna sebagai string
#         output_format='png'  # Format output (bisa 'png' atau 'jpg')
#     )
# else:
#     print("Tidak ada file yang dipilih.")

# Path Directory
# C:\D\Bootcamp\ICStar Hackathon 2024\Project Watermark\BackEnd Watermark\Gambar\ 