import cv2
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
import os

def get_color_from_string(color_str):
    """Mengambil warna RGB dari input string hex (#RRGGBB) atau nama warna ('red', 'green', 'blue')."""
    
    # Peta nama warna dasar ke nilai RGB
    named_colors = {
        'red': (0, 0, 255),  # BGR format untuk OpenCV
        'green': (0, 255, 0),
        'blue': (255, 0, 0),
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'yellow': (0, 255, 255),
        'cyan': (255, 255, 0),
        'magenta': (255, 0, 255)
    }
    
    # Ubah input menjadi huruf kecil untuk mencocokkan nama warna
    color_str = color_str.lower().strip()

    # Cek apakah input adalah nama warna
    if color_str in named_colors:
        return named_colors[color_str]

    # Jika tidak, asumsikan input adalah kode hex dan konversi ke RGB (BGR untuk OpenCV)
    color_str = color_str.lstrip('#')  # Menghilangkan tanda '#'
    if len(color_str) == 6:  # Harus sesuai format hex
        try:
            # Mengonversi nilai hex menjadi RGB
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            return (b, g, r)  # OpenCV menggunakan format BGR, jadi kita urutkan b, g, r
        except ValueError:
            raise ValueError(f"Kode warna hex '{color_str}' tidak valid. Harus dalam format #RRGGBB.")
    else:
        raise ValueError("Input harus berupa kode hex 6 digit (#RRGGBB) atau nama warna dasar ('red', 'green', 'blue', dll).")

def get_cv2_font(font_name):
    # Ubah input menjadi huruf kecil dan hilangkan karakter tambahan seperti apostrof
    font_name = font_name.lower()
    
    # Pemetaan dari string yang diberikan user ke konstanta OpenCV
    font_dict = {
        "hershey simplex": cv2.FONT_HERSHEY_SIMPLEX,
        "hershey plain": cv2.FONT_HERSHEY_PLAIN,
        "hershey duplex": cv2.FONT_HERSHEY_DUPLEX,
        "hershey complex": cv2.FONT_HERSHEY_COMPLEX,
        "hershey triplex": cv2.FONT_HERSHEY_TRIPLEX,
        "hershey complex small": cv2.FONT_HERSHEY_COMPLEX_SMALL,
        "hershey script simplex": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
        "hershey script complex": cv2.FONT_HERSHEY_SCRIPT_COMPLEX
    }

    # Cek apakah font_name ada di dalam dictionary
    if font_name in font_dict:
        return font_dict[font_name]
    else:
        raise ValueError(f"Font '{font_name}' tidak ditemukan. Harap gunakan salah satu dari font berikut: {list(font_dict.keys())}")

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

# def remove_background(logo):
#     """Menghilangkan latar belakang dari logo menggunakan thresholding."""
#     gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    
#     # Membuat mask berdasarkan thresholding
#     _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

#     # Menggunakan mask untuk menghilangkan latar belakang
#     logo_with_mask = cv2.bitwise_and(logo, logo, mask=mask)

#     # Cek jumlah saluran logo
#     if logo.shape[2] == 3:  # RGB
#         # Jika logo adalah RGB, buat alpha channel dengan nilai penuh
#         b, g, r = cv2.split(logo)
#         alpha_channel = np.zeros(b.shape, dtype=b.dtype)  # Alpha channel kosong
#         alpha_channel[mask > 0] = 255  # Set alpha channel menjadi 255 di area yang tidak putih
#         logo_rgba = cv2.merge((b, g, r, alpha_channel))
#     elif logo.shape[2] == 4:  # RGBA
#         # Jika logo sudah memiliki alpha channel
#         b, g, r, a = cv2.split(logo)
#         # Buat mask baru yang berdasarkan warna putih
#         new_mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)[1]  # Mask untuk area putih
#         a[new_mask == 255] = 0  # Set alpha channel menjadi 0 di area putih
#         logo_rgba = cv2.merge((b, g, r, a))

#     return logo_rgba

def remove_background(logo):
    """Menghilangkan latar belakang dari logo menggunakan thresholding."""
    gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)

    # Cek untuk background hitam
    is_black_background = np.mean(gray) < 50  # Threshold untuk mendeteksi latar belakang hitam

    # Membuat mask berdasarkan thresholding
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Menggunakan mask untuk menghilangkan latar belakang
    logo_with_mask = cv2.bitwise_and(logo, logo, mask=mask)

    # Cek jumlah saluran logo
    if logo.shape[2] == 3:  # RGB
        # Jika logo adalah RGB, buat alpha channel dengan nilai penuh
        b, g, r = cv2.split(logo)
        alpha_channel = np.zeros(b.shape, dtype=b.dtype)  # Alpha channel kosong
        alpha_channel[mask > 0] = 255  # Set alpha channel menjadi 255 di area yang tidak putih
        logo_rgba = cv2.merge((b, g, r, alpha_channel))
    elif logo.shape[2] == 4:  # RGBA
        # Jika logo sudah memiliki alpha channel
        b, g, r, a = cv2.split(logo)
        # Buat mask baru yang berdasarkan warna putih
        new_mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)[1]  # Mask untuk area putih
        a[new_mask == 255] = 0  # Set alpha channel menjadi 0 di area putih
        logo_rgba = cv2.merge((b, g, r, a))

    # Jika latar belakang hitam, set alpha channel menjadi 0 di area hitam
    if is_black_background:
        alpha_channel[gray < 50] = 0  # Set alpha channel menjadi 0 di area hitam

    return logo_rgba

def add_text_watermark(image, text, position_str,font_type='hershey simplex', font_color=(255, 255, 255), scale_factor=0.3, thickness=2, opacity=0.6):
    """Menambahkan watermark teks ke gambar dengan skala otomatis pada posisi yang ditentukan."""
    image_h, image_w, _ = image.shape

    font = get_cv2_font(font_type)
    
    #font = cv2.FONT_HERSHEY_SIMPLEX

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
        "atas kanan" : (image_w - text_w - 10, text_h + 10),               #"kanan atas"
        "tengah kanan" : (image_w - text_w - 10, (image_h + text_h) // 2),   #"kanan tengah"
        'bawah kanan' : (image_w - text_w - 10, image_h - 10),              #"kanan bawah"
        "atas kiri" : (10, text_h + 10),                                  #"kiri atas"
        'tengah kiri' : (10, (image_h + text_h) // 2),                      #"kiri tengah"
        'bawah kiri' : (10, image_h - 10),                                 #"kiri bawah"
        'tengah tengah' : ((image_w - text_w) // 2, (image_h + text_h) // 2), #"Tengah"
        'atas tengah' : ((image_w - text_w) // 2, text_h + 10),             # Posisi baru: Tengah atas
        'bawah tengah' : ((image_w - text_w) // 2, image_h - 10)             # Posisi baru: Tengah bawah
    }

    # Ambil posisi dari dictionary atau gunakan default
    position = positions.get(position_str.lower(), (image_w - text_w - 10, image_h - 10))
    #position = positions.get(position_str, (image_w - text_w - 10, image_h - 10))

    # Buat overlay untuk menempatkan teks dengan transparansi
    overlay = image.copy()

    # Menambahkan teks watermark di overlay
    cv2.putText(overlay, text, position, font, font_scale, font_color, thickness, cv2.LINE_AA)

    # Menggabungkan overlay dengan gambar asli menggunakan opacity
    cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    return image

def add_logo_watermark(image, logo, position_str, opacity):
    """Menambahkan watermark logo ke gambar dengan transparansi di posisi yang ditentukan."""

    # logo = cv2.imread(logo, cv2.IMREAD_UNCHANGED)

    # if logo is None:
    #     raise ValueError("Logo tidak ditemukan.")

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
        'atas kanan' : (image_w - logo_w, 0),#"kanan atas"
        'tengah kanan' : (image_w - logo_w, (image_h - logo_h) // 2),#"kanan tengah"
        'bawah kanan' : (image_w - logo_w, image_h - logo_h),#"kanan bawah"
        'atas kiri' : (0, 0),#"kiri atas"
        'tengah kiri' : (0, (image_h - logo_h) // 2),#"kiri tengah"
        'bawah kiri' : (0, image_h - logo_h),#"kiri bawah"
        'tengah tengah' : ((image_w - logo_w) // 2, (image_h - logo_h) // 2),#Tengah
        'atas tengah' : ((image_w - logo_w) // 2, logo_h + 10),  # Posisi baru: Tengah atas
        'bawah tengah' : ((image_w - logo_w) // 2, image_h - 10)  # Posisi baru: Tengah bawah
    }
    
    return positions.get(position_str.lower(), (image_w - logo_w, image_h - logo_h))
    #return positions.get(position_str, (image_w - logo_w, image_h - logo_h))

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

def add_watermark_with_auto_position(image, watermark, font_type='hershey simplex',watermark_type='logo', font_color=(255, 255, 255), font_scale=1, thickness=2, opacity=1.0):
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
        font = get_cv2_font(font_type)
        #font = cv2.FONT_HERSHEY_SIMPLEX
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

# Fungsi untuk menambahkan watermark di bawah gambar dengan bar putih dan scale factor
def add_watermark_below_image(image, font_type='hershey simplex',text=None, bar_height=50, opacity=0.3, font_color=(0, 0, 0), font_scale=1, thickness=2, scale_factor=0.7):
    # Load image
    # image = cv2.imread(image_path)
    # if image is None:
    #     raise ValueError(f"Gambar tidak ditemukan di path: {image_path}")
    
    # Ukuran gambar asli
    h, w, _ = image.shape

    # Buat bar putih di bawah gambar
    bar = np.ones((bar_height, w, 3), dtype=np.uint8) * 255  # Membuat bar putih dengan tinggi tertentu

    # Gabungkan gambar asli dengan bar putih di bawahnya
    combined_image = np.vstack((image, bar)).astype(np.uint8)

    # Sesuaikan skala teks berdasarkan scale factor
    scaled_font_scale = font_scale * scale_factor

    font = get_cv2_font(font_type)

    # Posisi teks di kanan bar dengan scale factor
    #text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scaled_font_scale, thickness)[0]
    text_size = cv2.getTextSize(text, font, scaled_font_scale, thickness)[0]
    text_x = w - text_size[0] - 10  # Teks di sebelah kanan dengan padding 10 px
    text_y = h + (bar_height + text_size[1]) // 2

    # Buat overlay untuk teks saja
    text_overlay = combined_image.copy()

    # Tambahkan teks ke bar putih pada overlay
    #cv2.putText(text_overlay, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, scaled_font_scale, font_color, thickness, cv2.LINE_AA)
    cv2.putText(text_overlay, text, (text_x, text_y), font, scaled_font_scale, font_color, thickness, cv2.LINE_AA)

    # Gabungkan teks overlay dengan gambar utama menggunakan opacity
    cv2.addWeighted(text_overlay[h:, :], opacity, combined_image[h:, :], 1 - opacity, 0, combined_image[h:, :])

    return combined_image

"""
#Fungsi utama untuk menambahkan watermark dan menyimpan dalam berbagai format
def main(image_path, watermark_type, output_path, text=None, logo_path=None, position_str=None, opacity=None, bar_height=50,font_color=(255, 255, 255), scale_factor=0.3, thickness=2, output_format='png'):
    # Load image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Gambar tidak ditemukan di path: {image_path}")

    # Preprocess image jika diperlukan
    preprocessed_image = image  # Placeholder untuk preprocessing jika diperlukan

    # Jika watermark berupa teks
    if watermark_type == 'text':
        if text is None:
            raise ValueError("Text harus disediakan untuk watermark jenis teks.")
        
        # Jika posisi adalah -2, gunakan fungsi `add_watermark_below_image`
        if position_str == -2:
            image_with_watermark = add_watermark_below_image(
                image_path=image_path,
                text=text,
                bar_height=bar_height,  # Tinggi bar bisa disesuaikan
                opacity=opacity,
                font_color=font_color,
                scale_factor=scale_factor,
                font_scale=1,  # Anda bisa mengganti skala font sesuai kebutuhan
                thickness=thickness
            )
        elif position_str == -1:
            # Implementasi watermark otomatis (jika ada)
            image_with_watermark = add_watermark_with_auto_position(
                preprocessed_image, text, watermark_type='text', font_color=font_color, thickness=thickness, opacity=opacity
            )
        else:
            # Implementasi watermark di posisi yang ditentukan
            image_with_watermark = add_text_watermark(
                preprocessed_image, text, position_str, font_color=font_color, opacity=opacity, thickness=thickness
            )
    
    # Jika watermark berupa logo
    elif watermark_type == 'logo':
        if logo_path is None:
            raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")

        # Load dan preprocess logo
        logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=preprocessed_image.shape[:2], scale_factor=scale_factor)

        if position_str == -1:
            # Implementasi watermark otomatis (jika ada)
            image_with_watermark = add_watermark_with_auto_position(
                preprocessed_image, logo, watermark_type='logo', opacity=opacity
            )
        else:
            # Implementasi watermark logo di posisi yang ditentukan
            image_with_watermark = add_logo_watermark(
                preprocessed_image, logo, position_str, opacity=opacity
            )

    # Membuat folder output jika belum ada
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Menambahkan "Watermark" pada nama file
    base_name = os.path.basename(image_path)  # Ambil nama file dari path
    name, ext = os.path.splitext(base_name)  # Pisahkan nama dan ekstensi
    output_filename = os.path.join(output_path, f'Watermark_{name}.{output_format}')  # Buat nama file dengan format yang dipilih

    # Simpan gambar dengan format yang dipilih oleh pengguna (JPG/PNG/JPEG)
    if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
        cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])  # Simpan sebagai JPG atau JPEG
    elif output_format.lower() == 'png':
        cv2.imwrite(output_filename, image_with_watermark)  # Simpan sebagai PNG
    else:
        raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

    return output_filename
"""


import cv2
import os
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

def remove_white_background(image, margin=0):
    # Convert image ke format grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Menggunakan adaptive threshold untuk mendeteksi area non-putih
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Temukan kontur
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Jika kontur ditemukan
    if contours:
        # Dapatkan bounding box terbesar dari semua kontur
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))

        # Crop gambar berdasarkan bounding box, tambahkan margin opsional
        cropped_image = image[max(0, y - margin):y + h + margin, max(0, x - margin):x + w + margin]

        return cropped_image
    else:
        # Jika tidak ada kontur, kembalikan gambar asli
        return image

def process_multiple_files(file_paths, watermark_type=None, enchance_quality=None, font_type=None, text=None, logo_path=None, position_str=None, opacity=None, bar_height=50, font_color=(255, 255, 255), scale_factor=0.3, thickness=2, output_format='png'):
    output_files = [os.path.abspath(file_paths), '']  # Inisialisasi list strict dengan 2 item: [file_path, error_message]
     
    try:
        # Cek apakah file path ada
        if not os.path.exists(file_paths):
            output_files[1] = "Error While Embedding Watermark: file tidak ditemukan"
            return output_files

        # Proses jika file adalah PDF
        if file_paths.lower().endswith('.pdf'):
            images = convert_from_path(file_paths, dpi=300, poppler_path=r"C:\\Users\\user\\poppler\\poppler-24.07.0\\Library\\bin")
            watermarked_images = []  # Menyimpan gambar dengan watermark untuk dikonversi kembali ke PDF
            
            for idx, image in enumerate(images):
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                open_cv_image = remove_white_background(open_cv_image, margin=0)
                
                if enchance_quality:
                    open_cv_image = preprocess_image(open_cv_image)

                image_with_watermark = open_cv_image

                # Watermark teks
                if watermark_type == 'text':
                    font_color = get_color_from_string(font_color)
                    if text is None:
                        raise ValueError("Text harus disediakan untuk watermark jenis teks.")
                    
                    if position_str == 'luar gambar':
                        image_with_watermark = add_watermark_below_image(
                            open_cv_image, text=text, bar_height=bar_height, opacity=opacity,
                            font_color=font_color, font_type=font_type, scale_factor=scale_factor, font_scale=1, thickness=thickness
                        )
                    elif position_str == 'auto':
                        image_with_watermark = add_watermark_with_auto_position(
                            open_cv_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
                        )
                    else:
                        image_with_watermark = add_text_watermark(
                            open_cv_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
                        )

                # Watermark logo
                elif watermark_type == 'logo':
                    if logo_path is None:
                        raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                    
                    # Cek apakah logo bukan PNG, jika iya, konversi ke PNG
                    logo_ext = os.path.splitext(logo_path)[1].lower()
                    if logo_ext in ['.jpg', '.jpeg']:
                        logo_image = cv2.imread(logo_path)
                        if logo_image is not None:
                            converted_logo_path = logo_path.replace(logo_ext, '.png')
                            cv2.imwrite(converted_logo_path, logo_image)
                            logo_path = converted_logo_path  # Set logo_path ke file PNG baru
                        else:
                            raise ValueError(f"Logo tidak dapat dibuka: {logo_path}")
                    
                    logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=open_cv_image.shape[:2], scale_factor=scale_factor)
                    
                    if position_str == 'auto':
                        image_with_watermark = add_watermark_with_auto_position(
                            open_cv_image, logo, watermark_type='logo', opacity=opacity
                        )                    
                    else:
                        image_with_watermark = add_logo_watermark(
                            open_cv_image, logo, position_str, opacity=opacity
                        )

                watermarked_images.append(Image.fromarray(cv2.cvtColor(image_with_watermark, cv2.COLOR_BGR2RGB)))

                base_name = os.path.basename(file_paths)
                name, ext = os.path.splitext(base_name)
                output_filename = os.path.join(f'Watermarked{idx + 1}_{name}.{output_format}')
                
                #output_files[0] = output_filename  # Set file path output ke list
                output_files[0] = os.path.abspath(output_filename)  # Set file path output ke list

                if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                    cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                elif output_format.lower() == 'png':
                    cv2.imwrite(output_filename, image_with_watermark)
                else:
                    raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

            if output_format.lower() == 'pdf':
                pdf_output_filename = os.path.join(f'Watermarked{os.path.basename(file_paths)}')
                watermarked_images[0].save(pdf_output_filename, save_all=True, append_images=watermarked_images[1:], resolution=300)
                #output_files[0] = pdf_output_filename  # Set PDF path ke list
                # Mengubah pdf_output_filename menjadi path absolut
                output_files[0] = os.path.abspath(pdf_output_filename)  # Set PDF path ke list
                return output_files

            return output_files

        else:
            # Jika file yang diupload bukan PDF, proses sebagai gambar
            image = cv2.imread(file_paths)
            if image is None:
                output_files[1] = f"Gambar tidak ditemukan di path: {file_paths}"
                return output_files

            if enchance_quality:
                preprocessed_image = preprocess_image(image)
            else:
                preprocessed_image = image

            image_with_watermark = preprocessed_image

            if watermark_type == 'text':
                font_color = get_color_from_string(font_color)
                if text is None:
                    raise ValueError("Text harus disediakan untuk watermark jenis teks.")
              
                if position_str == 'luar gambar':
                    image_with_watermark = add_watermark_below_image(
                        preprocessed_image, text=text, bar_height=bar_height, opacity=opacity,
                        font_color=font_color, font_type=font_type, scale_factor=scale_factor, font_scale=1, thickness=thickness
                    )
                elif position_str == 'auto':
                    image_with_watermark = add_watermark_with_auto_position(
                        preprocessed_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
                    )
                else:
                    image_with_watermark = add_text_watermark(
                        preprocessed_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
                    )

            elif watermark_type == 'logo':
                if logo_path is None:
                    raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                
                 # Cek apakah logo bukan PNG, jika iya, konversi ke PNG
                logo_ext = os.path.splitext(logo_path)[1].lower()
                if logo_ext in ['.jpg', '.jpeg']:
                    logo_image = cv2.imread(logo_path)
                    if logo_image is not None:
                        converted_logo_path = logo_path.replace(logo_ext, '.png')
                        cv2.imwrite(converted_logo_path, logo_image)
                        logo_path = converted_logo_path  # Set logo_path ke file PNG baru
                    else:
                        raise ValueError(f"Logo tidak dapat dibuka: {logo_path}")
                    
                logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=preprocessed_image.shape[:2], scale_factor=scale_factor)
                
                #logo=logo_path
                if position_str == 'auto':
                    image_with_watermark = add_watermark_with_auto_position(
                        preprocessed_image, logo, watermark_type='logo', opacity=opacity
                    )
                else:
                    image_with_watermark = add_logo_watermark(
                        preprocessed_image, logo, position_str, opacity=opacity
                    )

            base_name = os.path.basename(file_paths)
            name, ext = os.path.splitext(base_name)
            output_filename = os.path.join(f'Watermarked{name}.{output_format}')
            
            #output_files[0] = output_filename  # Set path output
            # Mengubah output_filename menjadi path absolut
            output_files[0] = os.path.abspath(output_filename)  # Set path output

            if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            elif output_format.lower() == 'png':
                cv2.imwrite(output_filename, image_with_watermark)
            else:
                raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

            return output_files

    except Exception as e:
        output_files[1] = f"Error While Embedding Watermark: {str(e)}"
        return output_files


#Set
"""
def process_multiple_files(file_paths, watermark_type=None, enchance_quality=None, font_type=None, text=None, logo_path=None, position_str=None, opacity=None, bar_height=50, font_color=(255, 255, 255), scale_factor=0.3, thickness=2, output_format='png'):
    output_files = set()  # Inisialisasi set untuk menyimpan hasil output unik
    
    try:
        # Cek apakah file path ada
        if not os.path.exists(file_paths):
            output_files.add(file_paths)
            output_files.add("")  # Menambahkan string kosong ke dalam set
            return output_files.union({f"Error While Embedding Watermark: file tidak ditemukan"}) 

        # Cek apakah file yang diupload adalah PDF
        if file_paths.lower().endswith('.pdf'):
            # Konversi PDF ke gambar
            images = convert_from_path(file_paths, dpi=300, poppler_path=r"C:\\Users\\user\\poppler\\poppler-24.07.0\\Library\\bin")
            watermarked_images = []  # Menyimpan gambar dengan watermark untuk dikonversi kembali ke PDF
            
            for idx, image in enumerate(images):
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                open_cv_image = remove_white_background(open_cv_image, margin=0)
                
                if enchance_quality:
                    print('Dilakukan Preprocessing')
                    open_cv_image = preprocess_image(open_cv_image)
                else:
                    print('Tidak dilakukan preprocessing')

                image_with_watermark = open_cv_image  # Inisialisasi dengan gambar asli

                if watermark_type == 'text':
                    font_color = get_color_from_string(font_color)
                    if text is None:
                        raise ValueError("Text harus disediakan untuk watermark jenis teks.")
                    
                    if position_str == 'luar gambar':
                        image_with_watermark = add_watermark_below_image(
                            open_cv_image,
                            text=text,
                            bar_height=bar_height,  # Tinggi bar bisa disesuaikan
                            opacity=opacity,
                            font_color=font_color,
                            font_type=font_type,
                            scale_factor=scale_factor,
                            font_scale=1,
                            thickness=thickness
                        )
                    elif position_str == 'auto':
                        image_with_watermark = add_watermark_with_auto_position(
                            open_cv_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
                        )
                    else:
                        image_with_watermark = add_text_watermark(
                            open_cv_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
                        )

                elif watermark_type == 'logo':
                    if logo_path is None:
                        raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                    logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=open_cv_image.shape[:2], scale_factor=scale_factor)
                    
                    if position_str == 'auto':
                        image_with_watermark = add_watermark_with_auto_position(
                            open_cv_image, logo, watermark_type='logo', opacity=opacity
                        )                    
                    else:
                        image_with_watermark = add_logo_watermark(
                            open_cv_image, logo, position_str, opacity=opacity
                        )

                watermarked_images.append(Image.fromarray(cv2.cvtColor(image_with_watermark, cv2.COLOR_BGR2RGB)))

                base_name = os.path.basename(file_paths)
                name, ext = os.path.splitext(base_name)
                output_filename = os.path.join(f'Watermarked{idx + 1}_{name}.{output_format}')
                output_files.add(output_filename)

                if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                    cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                elif output_format.lower() == 'png':
                    cv2.imwrite(output_filename, image_with_watermark)
                else:
                    raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

            if output_format.lower() == 'pdf':
                pdf_output_filename = os.path.join(f'Watermarked{os.path.basename(file_paths)}')
                watermarked_images[0].save(pdf_output_filename, save_all=True, append_images=watermarked_images[1:], resolution=300)
                output_files.add("")  # Menambahkan string kosong
                return {pdf_output_filename}  # Kembalikan nama file PDF hasil watermarking dalam set

            output_files.add("")  # Menambahkan string kosong ke set
            return output_files  # Kembalikan daftar file hasil watermarking dalam format gambar (set)

        else:
            # Jika file yang diupload bukan PDF, proses seperti biasa
            image = cv2.imread(file_paths)
            if image is None:
                raise ValueError(f"Gambar tidak ditemukan di path: {file_paths}")

            if enchance_quality:
                print('Dilakukan Preprocessing')
                preprocessed_image = preprocess_image(image)
            else:
                preprocessed_image = image  # Tidak dilakukan preprocessing jika enhance_quality = False
                print('Tidak Dilakukan Preprocessing')
            
            image_with_watermark = preprocessed_image  # Inisialisasi dengan gambar asli

            if watermark_type == 'text':
                font_color = get_color_from_string(font_color)
                if text is None:
                    raise ValueError("Text harus disediakan untuk watermark jenis teks.")
              
                if position_str == 'luar gambar':
                    image_with_watermark = add_watermark_below_image(
                        preprocessed_image,
                        text=text,
                        bar_height=bar_height,
                        opacity=opacity,
                        font_color=font_color,
                        font_type=font_type,
                        scale_factor=scale_factor,
                        font_scale=1,
                        thickness=thickness
                    )
                elif position_str == 'auto':
                    image_with_watermark = add_watermark_with_auto_position(
                        preprocessed_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
                    )
                else:
                    image_with_watermark = add_text_watermark(
                        preprocessed_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
                    )
        
            elif watermark_type == 'logo':
                if logo_path is None:
                    raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=preprocessed_image.shape[:2], scale_factor=scale_factor)
                
                if position_str == 'auto':
                    image_with_watermark = add_watermark_with_auto_position(
                        preprocessed_image, logo, watermark_type='logo', opacity=opacity
                    )                    
                else:
                    image_with_watermark = add_logo_watermark(
                        preprocessed_image, logo, position_str, opacity=opacity
                    )

            base_name = os.path.basename(file_paths)
            name, ext = os.path.splitext(base_name)
            output_filename = os.path.join(f'Watermarked{name}.{output_format}')
            output_files.add(output_filename)

            if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            elif output_format.lower() == 'png':
                cv2.imwrite(output_filename, image_with_watermark)
            else:
                raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

            output_files.add("")  # Menambahkan string kosong ke set
            return output_files  # Kembalikan daftar file dalam set (meskipun hanya satu file)

    except Exception as e:
        output_files.add("")  # Menambahkan string kosong ke set saat ada error
        return output_files.union({f"Error While Embedding Watermark: {str(e)}"})  # Mengembalikan output_files ditambah pesan kesalahan dalam set
"""

#Tuple
"""
def process_multiple_files(file_paths, watermark_type=None, enchance_quality=None, font_type=None, text=None, logo_path=None, position_str=None, opacity=None, bar_height=50, font_color=(255, 255, 255), scale_factor=0.3, thickness=2, output_format='png'):
    output_files = ()  # Inisialisasi tuple untuk menyimpan hasil output
    
    try:
        # Cek apakah file path ada
        if not os.path.exists(file_paths):
            output_files = (file_paths,)  # Membuat tuple berisi file_paths
            output_files = output_files + ("",)  # Menyisipkan elemen "" ke dalam tuple
            return output_files + (f"Error While Embedding Watermark: file tidak ditemukan",)

        # Cek apakah file yang diupload adalah PDF
        if file_paths.lower().endswith('.pdf'):
            # Konversi PDF ke gambar
            images = convert_from_path(file_paths, dpi=300, poppler_path=r"C:\\Users\\user\\poppler\\poppler-24.07.0\\Library\\bin")
            watermarked_images = []  # Menyimpan gambar dengan watermark untuk dikonversi kembali ke PDF
            
            for idx, image in enumerate(images):
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                open_cv_image = remove_white_background(open_cv_image, margin=0)
                
                if enchance_quality:
                    print('Dilakukan Preprocessing')
                    open_cv_image = preprocess_image(open_cv_image)
                else:
                    print('Tidak dilakukan preprocessing')

                image_with_watermark = open_cv_image  # Inisialisasi dengan gambar asli

                if watermark_type == 'text':
                    font_color = get_color_from_string(font_color)
                    if text is None:
                        raise ValueError("Text harus disediakan untuk watermark jenis teks.")
                    
                    if position_str == 'luar gambar':
                        image_with_watermark = add_watermark_below_image(
                            open_cv_image,
                            text=text,
                            bar_height=bar_height,  # Tinggi bar bisa disesuaikan
                            opacity=opacity,
                            font_color=font_color,
                            font_type=font_type,
                            scale_factor=scale_factor,
                            font_scale=1,
                            thickness=thickness
                        )
                    elif position_str == 'auto':
                        image_with_watermark = add_watermark_with_auto_position(
                            open_cv_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
                        )
                    else:
                        image_with_watermark = add_text_watermark(
                            open_cv_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
                        )

                elif watermark_type == 'logo':
                    if logo_path is None:
                        raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                    logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=open_cv_image.shape[:2], scale_factor=scale_factor)
                    
                    if position_str == 'auto':
                        image_with_watermark = add_watermark_with_auto_position(
                            open_cv_image, logo, watermark_type='logo', opacity=opacity
                        )                    
                    else:
                        image_with_watermark = add_logo_watermark(
                            open_cv_image, logo, position_str, opacity=opacity
                        )

                watermarked_images.append(Image.fromarray(cv2.cvtColor(image_with_watermark, cv2.COLOR_BGR2RGB)))

                base_name = os.path.basename(file_paths)
                name, ext = os.path.splitext(base_name)
                output_filename = os.path.join(f'Watermarked{idx + 1}_{name}.{output_format}')
                output_files = output_files + (output_filename,)  # Menambah output filename ke tuple

                if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                    cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                elif output_format.lower() == 'png':
                    cv2.imwrite(output_filename, image_with_watermark)
                else:
                    raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

            if output_format.lower() == 'pdf':
                pdf_output_filename = os.path.join(f'Watermarked{os.path.basename(file_paths)}')
                watermarked_images[0].save(pdf_output_filename, save_all=True, append_images=watermarked_images[1:], resolution=300)
                return (pdf_output_filename,)  # Kembalikan nama file PDF hasil watermarking sebagai tuple
            
            output_files = output_files + ("",)  # Menambahkan string kosong ke tuple
            return output_files  # Kembalikan daftar file hasil watermarking dalam format gambar (tuple)

        else:
            # Jika file yang diupload bukan PDF, proses seperti biasa
            image = cv2.imread(file_paths)
            if image is None:
                raise ValueError(f"Gambar tidak ditemukan di path: {file_paths}")

            if enchance_quality:
                print('Dilakukan Preprocessing')
                preprocessed_image = preprocess_image(image)
            else:
                preprocessed_image = image  # Tidak dilakukan preprocessing jika enhance_quality = False
                print('Tidak Dilakukan Preprocessing')
            
            image_with_watermark = preprocessed_image  # Inisialisasi dengan gambar asli

            if watermark_type == 'text':
                font_color = get_color_from_string(font_color)
                if text is None:
                    raise ValueError("Text harus disediakan untuk watermark jenis teks.")
              
                if position_str == 'luar gambar':
                    image_with_watermark = add_watermark_below_image(
                        preprocessed_image,
                        text=text,
                        bar_height=bar_height,
                        opacity=opacity,
                        font_color=font_color,
                        font_type=font_type,
                        scale_factor=scale_factor,
                        font_scale=1,
                        thickness=thickness
                    )
                elif position_str == 'auto':
                    image_with_watermark = add_watermark_with_auto_position(
                        preprocessed_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
                    )
                else:
                    image_with_watermark = add_text_watermark(
                        preprocessed_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
                    )
        
            elif watermark_type == 'logo':
                if logo_path is None:
                    raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=preprocessed_image.shape[:2], scale_factor=scale_factor)
                
                if position_str == 'auto':
                    image_with_watermark = add_watermark_with_auto_position(
                        preprocessed_image, logo, watermark_type='logo', opacity=opacity
                    )                    
                else:
                    image_with_watermark = add_logo_watermark(
                        preprocessed_image, logo, position_str, opacity=opacity
                    )

            base_name = os.path.basename(file_paths)
            name, ext = os.path.splitext(base_name)
            output_filename = os.path.join(f'Watermarked{name}.{output_format}')
            output_files = output_files + (output_filename,)  # Menambahkan output filename ke tuple

            if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            elif output_format.lower() == 'png':
                cv2.imwrite(output_filename, image_with_watermark)
            else:
                raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")
            
            output_files = output_files + ("",)  # Menambahkan string kosong ke tuple
            return output_files  # Kembalikan daftar file dalam tuple (meskipun hanya satu file)

    except Exception as e:
        return output_files + (f"Error While Embedding Watermark: {str(e)}",)  # Mengembalikan output_files ditambah pesan kesalahan dalam tuple
"""

#LIST
"""def process_multiple_files(file_paths, watermark_type=None, enchance_quality=None, font_type=None, text=None, logo_path=None, position_str=None, opacity=None, bar_height=50, font_color=(255, 255, 255), scale_factor=0.3, thickness=2, output_format='png'):
    output_files = []  # Inisialisasi list untuk menyimpan hasil output
    
    try:
        # Cek apakah file path ada
        if not os.path.exists(file_paths):
            output_files.append(file_paths)
            return output_files + [f"Error While Embedding Watermark: file tidak ditemukan"] 
            #return [f"Error: File tidak ditemukan di path: {file_paths}"]  # Jika file path tidak ditemukan

        # Cek apakah file yang diupload adalah PDF
        if file_paths.lower().endswith('.pdf'):
            # Konversi PDF ke gambar
            images = convert_from_path(file_paths, dpi=300, poppler_path=r"C:\\Users\\user\\poppler\\poppler-24.07.0\\Library\\bin")
            watermarked_images = []  # Menyimpan gambar dengan watermark untuk dikonversi kembali ke PDF
            
            for idx, image in enumerate(images):
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                open_cv_image = remove_white_background(open_cv_image, margin=0)
                
                if enchance_quality:
                    print('Dilakukan Preprocessing')
                    open_cv_image = preprocess_image(open_cv_image)
                else:
                    print('Tidak dilakukan preprocessing')

                image_with_watermark = open_cv_image  # Inisialisasi dengan gambar asli

                if watermark_type == 'text':
                    font_color = get_color_from_string(font_color)
                    if text is None:
                        raise ValueError("Text harus disediakan untuk watermark jenis teks.")
                    
                    if position_str == 'luar gambar':
                        image_with_watermark = add_watermark_below_image(
                            open_cv_image,
                            text=text,
                            bar_height=bar_height,  # Tinggi bar bisa disesuaikan
                            opacity=opacity,
                            font_color=font_color,
                            font_type=font_type,
                            scale_factor=scale_factor,
                            font_scale=1,
                            thickness=thickness
                        )
                    elif position_str == 'auto':
                        image_with_watermark = add_watermark_with_auto_position(
                            open_cv_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
                        )
                    else:
                        image_with_watermark = add_text_watermark(
                            open_cv_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
                        )

                elif watermark_type == 'logo':
                    if logo_path is None:
                        raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                    logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=open_cv_image.shape[:2], scale_factor=scale_factor)
                    
                    if position_str == 'auto':
                        image_with_watermark = add_watermark_with_auto_position(
                            open_cv_image, logo, watermark_type='logo', opacity=opacity
                        )                    
                    else:
                        image_with_watermark = add_logo_watermark(
                            open_cv_image, logo, position_str, opacity=opacity
                        )

                watermarked_images.append(Image.fromarray(cv2.cvtColor(image_with_watermark, cv2.COLOR_BGR2RGB)))

                base_name = os.path.basename(file_paths)
                name, ext = os.path.splitext(base_name)
                output_filename = os.path.join(f'Watermarked{idx + 1}_{name}.{output_format}')
                output_files.append(output_filename)

                if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                    cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                elif output_format.lower() == 'png':
                    cv2.imwrite(output_filename, image_with_watermark)
                else:
                    raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

            if output_format.lower() == 'pdf':
                pdf_output_filename = os.path.join(f'Watermarked{os.path.basename(file_paths)}')
                watermarked_images[0].save(pdf_output_filename, save_all=True, append_images=watermarked_images[1:], resolution=300)
                return [pdf_output_filename]  # Kembalikan nama file PDF hasil watermarking dalam list

            return output_files + ['']  # Kembalikan daftar file hasil watermarking dalam format gambar (list)

        else:
            # Jika file yang diupload bukan PDF, proses seperti biasa
            image = cv2.imread(file_paths)
            if image is None:
                raise ValueError(f"Gambar tidak ditemukan di path: {file_paths}")

            if enchance_quality:
                print('Dilakukan Preprocessing')
                preprocessed_image = preprocess_image(image)
            else:
                preprocessed_image = image  # Tidak dilakukan preprocessing jika enhance_quality = False
                print('Tidak Dilakukan Preprocessing')
            
            image_with_watermark = preprocessed_image  # Inisialisasi dengan gambar asli

            if watermark_type == 'text':
                font_color = get_color_from_string(font_color)
                if text is None:
                    raise ValueError("Text harus disediakan untuk watermark jenis teks.")
              
                if position_str == 'luar gambar':
                    image_with_watermark = add_watermark_below_image(
                        preprocessed_image,
                        text=text,
                        bar_height=bar_height,
                        opacity=opacity,
                        font_color=font_color,
                        font_type=font_type,
                        scale_factor=scale_factor,
                        font_scale=1,
                        thickness=thickness
                    )
                elif position_str == 'auto':
                    image_with_watermark = add_watermark_with_auto_position(
                        preprocessed_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
                    )
                else:
                    image_with_watermark = add_text_watermark(
                        preprocessed_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
                    )
        
            elif watermark_type == 'logo':
                if logo_path is None:
                    raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=preprocessed_image.shape[:2], scale_factor=scale_factor)
                
                if position_str == 'auto':
                    image_with_watermark = add_watermark_with_auto_position(
                        preprocessed_image, logo, watermark_type='logo', opacity=opacity
                    )                    
                else:
                    image_with_watermark = add_logo_watermark(
                        preprocessed_image, logo, position_str, opacity=opacity
                    )

            base_name = os.path.basename(file_paths)
            name, ext = os.path.splitext(base_name)
            output_filename = os.path.join(f'Watermarked{name}.{output_format}')
            output_files.append(output_filename)

            if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
                cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            elif output_format.lower() == 'png':
                cv2.imwrite(output_filename, image_with_watermark)
            else:
                raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

            return output_files + ['']  # Kembalikan daftar file dalam list (meskipun hanya satu file)

    except Exception as e:
        #return f"Error While Embedding Watermark: {str(e)}", output_files  # Kembalikan pesan error dan daftar file output jika ada
        return output_files + [f"Error While Embedding Watermark: {str(e)}"]  # Mengembalikan output_files ditambah pesan kesalahan
        #return output_files + ['Error While Embedding Watermark'] # Kembalikan pesan error dan daftar file output jika ada
"""

# file_paths = 'Gambar\komputer mainframe1.jpg'

# results = process_multiple_files(file_paths,watermark_type='logo',
#                     text='Sample Watermark',font_type='hershey script simplex',
#                     font_color='red',position_str='bawah kanan',opacity=0.3,output_format='png',
#                     enchance_quality=True,
#                     #logo_path=None)
#                     logo_path='Gambar\watermark logo.png')

# print(results)

#def main(file_paths, watermark_type, output_path, enchance_quality=None,font_type=None, text=None, logo_path=None, position_str=None, opacity=None, bar_height=50, font_color=(255, 255, 255), scale_factor=0.3, thickness=2, output_format='png'):
    # output_files = []  # Inisialisasi list untuk menyimpan hasil output
    
    # try:
    #     # Cek apakah file yang diupload adalah PDF
    #     if image_path.lower().endswith('.pdf'):
    #         # Konversi PDF ke gambar
    #         images = convert_from_path(image_path, dpi=300, poppler_path=r"C:\\Users\\user\\poppler\\poppler-24.07.0\\Library\\bin")
    #         watermarked_images = []  # Menyimpan gambar dengan watermark untuk dikonversi kembali ke PDF
            
    #         for idx, image in enumerate(images):
    #             open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    #             open_cv_image = remove_white_background(open_cv_image, margin=0)
                
    #             if enchance_quality:
    #                 print('Dilakukan Preprocessing')
    #                 open_cv_image = preprocess_image(open_cv_image)
    #             else:
    #                 print('Tidak dilakukan preprocessing')

    #             if watermark_type == 'text':
    #                 font_color = get_color_from_string(font_color)
    #                 if text is None:
    #                     raise ValueError("Text harus disediakan untuk watermark jenis teks.")
                    
    #                 if position_str == 'luar gambar':
    #                     image_with_watermark = add_watermark_below_image(
    #                         open_cv_image,
    #                         text=text,
    #                         bar_height=bar_height,  # Tinggi bar bisa disesuaikan
    #                         opacity=opacity,
    #                         font_color=font_color,
    #                         font_type=font_type,
    #                         scale_factor=scale_factor,
    #                         font_scale=1,
    #                         thickness=thickness
    #                     )
    #                 elif position_str == 'auto':
    #                     image_with_watermark = add_watermark_with_auto_position(
    #                         open_cv_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
    #                     )
    #                 else:
    #                     image_with_watermark = add_text_watermark(
    #                         open_cv_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
    #                     )

    #             elif watermark_type == 'logo':
    #                 if logo_path is None:
    #                     raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
    #                 logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=open_cv_image.shape[:2], scale_factor=scale_factor)
                    
    #                 if position_str == 'auto':
    #                     image_with_watermark = add_watermark_with_auto_position(
    #                         open_cv_image, logo, watermark_type='logo', opacity=opacity
    #                     )                    
    #                 else:
    #                     image_with_watermark = add_logo_watermark(
    #                         open_cv_image, logo, position_str, opacity=opacity
    #                     )

    #             watermarked_images.append(Image.fromarray(cv2.cvtColor(image_with_watermark, cv2.COLOR_BGR2RGB)))

    #             if not os.path.exists(output_path):
    #                 os.makedirs(output_path)

    #             base_name = os.path.basename(image_path)
    #             name, ext = os.path.splitext(base_name)
    #             output_filename = os.path.join(output_path, f'Watermarked_Page_{idx + 1}_{name}.{output_format}')
    #             output_files.append(output_filename)

    #             if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
    #                 cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    #             elif output_format.lower() == 'png':
    #                 cv2.imwrite(output_filename, image_with_watermark)
    #             else:
    #                 raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

    #         if output_format.lower() == 'pdf':
    #             pdf_output_filename = os.path.join(output_path, f'Watermarked_{os.path.basename(image_path)}')
    #             watermarked_images[0].save(pdf_output_filename, save_all=True, append_images=watermarked_images[1:], resolution=300)
    #             return [pdf_output_filename]  # Kembalikan nama file PDF hasil watermarking dalam list

    #         return output_files  # Kembalikan daftar file hasil watermarking dalam format gambar (list)

    #     else:
    #         # Jika file yang diupload bukan PDF, proses seperti biasa
    #         image = cv2.imread(image_path)
    #         if image is None:
    #             raise ValueError(f"Gambar tidak ditemukan di path: {image_path}")

    #         if enchance_quality:
    #                 print('Dilakukan Preprocessing')
    #                 preprocessed_image = preprocess_image(open_cv_image)
    #         else:
    #             print('Tidak dilakukan preprocessing')
            
    #         if watermark_type == 'text':
    #             font_color = get_color_from_string(font_color)
    #             if text is None:
    #                 raise ValueError("Text harus disediakan untuk watermark jenis teks.")
              
    #             if position_str == 'luar gambar':
    #                 image_with_watermark = add_watermark_below_image(
    #                     preprocessed_image,
    #                     text=text,
    #                     bar_height=bar_height,
    #                     opacity=opacity,
    #                     font_color=font_color,
    #                     font_type=font_type,
    #                     scale_factor=scale_factor,
    #                     font_scale=1,
    #                     thickness=thickness
    #                 )
    #             elif position_str == 'auto':
    #                 image_with_watermark = add_watermark_with_auto_position(
    #                     preprocessed_image, text, watermark_type='text', font_color=font_color, font_type=font_type, thickness=thickness, opacity=opacity
    #                 )
    #             else:
    #                 image_with_watermark = add_text_watermark(
    #                     preprocessed_image, text, position_str, font_color=font_color, font_type=font_type, opacity=opacity, thickness=thickness
    #                 )
        
    #         elif watermark_type == 'logo':
    #             if logo_path is None:
    #                 raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
    #             logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=preprocessed_image.shape[:2], scale_factor=scale_factor)
                
    #             if position_str == 'auto':
    #                 image_with_watermark = add_watermark_with_auto_position(
    #                     preprocessed_image, logo, watermark_type='logo', opacity=opacity
    #                 )                    
    #             else:
    #                 image_with_watermark = add_logo_watermark(
    #                     preprocessed_image, logo, position_str, opacity=opacity
    #                 )

    #         if not os.path.exists(output_path):
    #             os.makedirs(output_path)

    #         base_name = os.path.basename(image_path)
    #         name, ext = os.path.splitext(base_name)
    #         output_filename = os.path.join(output_path, f'Watermark_{name}.{output_format}')
    #         output_files.append(output_filename)

    #         if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
    #             cv2.imwrite(output_filename, image_with_watermark, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    #         elif output_format.lower() == 'png':
    #             cv2.imwrite(output_filename, image_with_watermark)
    #         else:
    #             raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")

    #         return output_files  # Kembalikan daftar file dalam list (meskipun hanya satu file)

    # except Exception as e:
    #     return f"Error: {str(e)}", output_files


# def process_multiple_files(file_paths, watermark_type, enchance_quality,font_type=None, text=None, thickness=None, logo_path=None, scale_factor=0.3, position_str=None, opacity=None, font_color="putih", output_format='png'):
    # Inisialisasi list untuk menyimpan output dari setiap file yang diproses
    # all_output_files = []
    # all_output_files
    # error_messages = []

    # for file_paths in file_paths:
    #     if os.path.isfile(file_path):
    #         try:
    #             print(f"Memproses {file_path}...")
    #             # Memanggil fungsi main untuk setiap file
    #             output_files = main(
    #                 image_path=file_path,
    #                 watermark_type=watermark_type,
    #                 text=text,
    #                 enchance_quality=enchance_quality,
    #                 font_type=font_type,
    #                 scale_factor=scale_factor,
    #                 logo_path=logo_path,
    #                 thickness=thickness,
    #                 position_str=position_str,
    #                 opacity=opacity,
    #                 font_color=font_color,
    #                 output_format=output_format
    #             )
    #             # Menambahkan hasil output ke dalam list
    #             if isinstance(output_files, list):
    #                 all_output_files.extend(output_files)  # Jika `output_files` adalah list, tambahkan semuanya
    #             else:
    #                 all_output_files.append(output_files)  # Jika hanya satu file, tambahkan langsung
    #         except Exception as e:
    #             #error_messages.append(f"Error processing {file_path}: {str(e)}")
    #             error_messages.append(f"Error while embedding watermark")
    #             error_messages.append(file_path)
                

    # # Return daftar file output yang berhasil diproses, atau error jika ada
    # if error_messages:
    #     combined_list = all_output_files + error_messages  # Gabungkan output file dengan pesan error
    #     return combined_list
    # else:
    #     return all_output_files + ['']  # Return "Watermarked" sebagai penanda sukses dan output file paths


# Fungsi untuk memilih file menggunakan dialog file picker dari tkinter
# def select_files():
#     Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
#     file_paths = askopenfilenames(title="Pilih Gambar", filetypes=[("Image files", "*.jpg *.jpeg *.png *.pdf")])
#     return file_paths

# # Memilih file secara langsung dengan tkinter
# file_paths = select_files()

# # # #Jika ada file yang dipilih
# if file_paths:
#     # Proses setiap file yang dipilih
#     process_multiple_files(
#         file_paths=file_paths,
#         watermark_type='text',
#         output_path="Watermarked Content",
#         text='Contoh',  # Contoh teks watermark
#         position_str=2,#"kanan bawah",
#         opacity=0.3,
#         #font_scale=0.5,
#         scale_factor=0.5,
#         thickness=2,
#         font_color='#49FFCE',  # Input warna sebagai string
#         output_format='png'  # Format output (bisa 'png' atau 'jpg')
#     )
# else:
#     print("Tidak ada file yang dipilih.")

# Path Directory
# C:\D\Bootcamp\ICStar Hackathon 2024\Project Watermark\BackEnd Watermark\Gambar\ 


# print(f"Watermark telah ditambahkan: {output_image}")