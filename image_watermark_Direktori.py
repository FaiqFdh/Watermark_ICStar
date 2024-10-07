import cv2
import numpy as np

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

def add_logo_watermark(image, logo, position_str, opacity=0.5):
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

def add_text_watermark(image, text, position_str, font_color=(255, 255, 255), scale_factor=0.002, thickness=1):
    """Menambahkan watermark teks ke gambar dengan skala otomatis pada posisi yang ditentukan."""
    image_h, image_w, _ = image.shape
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Menentukan ukuran font berdasarkan scale_factor
    font_scale = scale_factor * min(image_w, image_h)

    # Tentukan ukuran teks dan baseline
    text_size, baseline = cv2.getTextSize(text, font, font_scale, thickness)
    text_w, text_h = text_size

    positions = {
        "kanan atas": (image_w - text_w - 10, text_h + 10),
        "kanan tengah": (image_w - text_w - 10, (image_h + text_h) // 2),
        "kanan bawah": (image_w - text_w - 10, image_h - 10),
        "kiri atas": (10, text_h + 10),
        "kiri tengah": (10, (image_h + text_h) // 2),
        "kiri bawah": (10, image_h - 10),
        "tengah": ((image_w - text_w) // 2, (image_h + text_h) // 2)
    }

    position = positions.get(position_str.lower(), (image_w - text_w - 10, image_h - 10))

    # Menambahkan teks ke gambar
    cv2.putText(image, text, position, font, font_scale, font_color, thickness, lineType=cv2.LINE_AA)

    return image

def get_watermark_position(image, watermark, position_str):
    """Mengembalikan koordinat (x, y) berdasarkan string posisi yang diberikan."""
    image_h, image_w, _ = image.shape
    logo_h, logo_w, _ = watermark.shape

    positions = {
        "kanan atas": (image_w - logo_w, 0),
        "kanan tengah": (image_w - logo_w, (image_h - logo_h) // 2),
        "kanan bawah": (image_w - logo_w, image_h - logo_h),
        "kiri atas": (0, 0),
        "kiri tengah": (0, (image_h - logo_h) // 2),
        "kiri bawah": (0, image_h - logo_h),
        "tengah": ((image_w - logo_w) // 2, (image_h - logo_h) // 2)
    }

    return positions.get(position_str.lower(), (image_w - logo_w, image_h - logo_h))

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
    resized_map = cv2.resize(inverted_map, (image.shape[1] - w, image.shape[0] - h))

    # Temukan posisi dengan nilai terkecil (paling gelap di inverted map)
    min_val, _, min_loc, _ = cv2.minMaxLoc(resized_map)

    optimal_position = (min_loc[0], min_loc[1])

    return optimal_position

def add_watermark_with_auto_position(image, watermark, watermark_type='logo', font_color=(255, 255, 255), font_scale=1, thickness=2, opacity=0.5):
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

import os  # Tambahkan ini untuk mengelola nama file

def main(image_path, watermark_type, text=None, logo_path=None, position_str=None, opacity=0.5, font_color=(255, 255, 255), font_scale=1,scale_factor=0.5, thickness=2, output_format='png'):
    # Load image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Gambar tidak ditemukan di path: {image_path}")

    # Preprocess image
    preprocessed_image = preprocess_image(image)

    if watermark_type == 'text':
        if text is None:
            raise ValueError("Text harus disediakan untuk watermark jenis teks.")
        if position_str == "otomatis":
            image = add_watermark_with_auto_position(preprocessed_image, text, watermark_type='text', font_color=font_color, font_scale=font_scale, thickness=thickness)
        else:
            image = add_text_watermark(preprocessed_image, text, position_str)
    elif watermark_type == 'logo':
        if logo_path is None:
            raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
        # Load dan preprocess logo sebelum digunakan
        logo = preprocess_logo(cv2.imread(logo_path, cv2.IMREAD_UNCHANGED), image_size=preprocessed_image.shape[:2])
        if position_str == "otomatis":
            image = add_watermark_with_auto_position(preprocessed_image, logo, watermark_type='logo')
        else:
            image = add_logo_watermark(preprocessed_image, logo, position_str, opacity=opacity)

     # Buat folder "Watermarked Image" jika belum ada
    output_dir = "Watermarked Image"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

      # Menambahkan "Watermark" pada nama file
    base_name = os.path.basename(image_path)  # Ambil nama file dari path
    name, ext = os.path.splitext(base_name)  # Pisahkan nama dan ekstensi
    output_filename = os.path.join(output_dir, f'Watermark_{name}.{output_format}')  # Buat path file output dalam folder

    # Simpan gambar dengan watermark
    if output_format.lower() == 'jpg' or output_format.lower() == 'jpeg':
        cv2.imwrite(output_filename, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])  # Simpan sebagai JPG
    elif output_format.lower() == 'png':
        cv2.imwrite(output_filename, image)  # Simpan sebagai PNG
    else:
        raise ValueError("Format output tidak didukung. Silakan pilih 'jpg' atau 'png'.")

    return output_filename

# Fungsi untuk memproses multiple files dari disk lokal
def process_multiple_files(directory_path, watermark_type, text=None, logo_path=None, position_str="kanan bawah", opacity=0.5, output_format='png'):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            print(f"Memproses {file_path}...")
            output_image = main(
                image_path=file_path,
                watermark_type=watermark_type,
                text=text,
                logo_path=logo_path,
                position_str=position_str,
                opacity=opacity,
                output_format=output_format
            )
            print(f"Gambar dengan watermark disimpan sebagai {output_image}")

# Meminta user untuk memasukkan directory file gambar
directory_path = input("Masukkan path direktori tempat file gambar: ").strip()

# Pastikan path valid
if os.path.isdir(directory_path):
    # Proses setiap file yang ada di dalam direktori
    process_multiple_files(
        directory_path=directory_path,
        #watermark_type='logo',
        #logo_path='C:\\D\Bootcamp\\ICStar Hackathon 2024\\Project Watermark\\BackEnd Watermark\\Gambar\\watermark logo.png',  # Sesuaikan dengan path logo Anda
        watermark_type='text',
        text="Hak Cipta 2024",
        position_str='kanan bawah',
        opacity=0.7,
        output_format='png'  # Format output (bisa 'png' atau 'jpg')
    )
else:
    print(f"Direktori {directory_path} tidak ditemukan.")

# Path Directory
# C:\D\Bootcamp\ICStar Hackathon 2024\Project Watermark\BackEnd Watermark\Gambar\ 