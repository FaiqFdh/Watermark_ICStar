import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from pdf2image import convert_from_path

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
    #font_name = font_name.lower()
    
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

def add_text_watermark(image, text, position_str, font_type='hershey simplex', font_color='red', scale_factor=0.3, thickness=2, opacity=0.6):
    """Menambahkan watermark teks ke gambar dengan skala otomatis pada posisi yang ditentukan."""
    image_h, image_w, _ = image.shape

    font_folder = "Font"  # Nama folder untuk font eksternal
    external_font_used = False  # Flag untuk menentukan apakah font eksternal digunakan

    # # Ubah warna font dari string ke format BGR
    # font_color = get_color_from_string(font_color)

    # Periksa apakah font termasuk font OpenCV atau eksternal
    if font_type.lower() in get_cv2_fonts():
        font = get_cv2_font(font_type) # Menentukan Font yang dipakai
        font_scale = scale_factor * min(image_w, image_h) / 150 # Menghitung nilai font_scale. Min(image_w, image_h) memilih ukuran terkecil antara lebar (image_w) dan tinggi (image_h) dari gambar untuk mengatur skala font agar proporsional dengan ukuran gambar.
        text_size, baseline = cv2.getTextSize(text, font, font_scale, thickness) # Fungsi cv2.getTextSize digunakan untuk menghitung ukuran teks (text_size) dan baseline teks (baseline) berdasarkan font, skala font (font_scale), dan ketebalan (thickness). text_size akan berisi lebar dan tinggi teks dalam piksel.
        text_w, text_h = text_size
    else:
        # Gunakan font eksternal dari folder Font jika tidak ada di OpenCV
        external_font_used = True
        font_path = os.path.join(font_folder, f"{font_type}.ttf")
        
        # Cek apakah file font eksternal ada
        if not os.path.exists(font_path):
            raise ValueError(f"Font '{font_type}' tidak ditemukan di folder '{font_folder}'. Pastikan file .ttf ada di folder tersebut.")
        
        # Menggunakan font eksternal
        font_scale = int(scale_factor * min(image_w, image_h) / 10)  # Sesuaikan ukuran font
        font = ImageFont.truetype(font_path, font_scale) # BMembuat objek font menggunakan font eksternal yang berada di jalur font_path dengan ukuran yang ditentukan oleh font_scale. Fungsi ImageFont.truetype dari modul PIL digunakan untuk mendukung font TTF (TrueType Font) eksternal.
        
        # Konversi gambar ke format Pillow untuk mendukung font eksternal
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)) # Mengonversi gambar OpenCV (image) menjadi format PIL. OpenCV menggunakan format warna BGR secara default, sehingga cv2.cvtColor digunakan untuk mengubah gambar ke format RGB sebelum konversi ke format PIL menggunakan Image.fromarray.
        draw = ImageDraw.Draw(pil_image) # Baris ini membuat objek draw dari ImageDraw, yang memungkinkan Anda menggambar di atas pil_image. Dengan draw, Anda dapat menambahkan teks, bentuk, dan elemen lain ke dalam gambar.
        
        # Menggunakan textbbox untuk mendapatkan ukuran teks
        text_bbox = draw.textbbox((0, 0), text, font=font) # draw.textbbox untuk menghitung kotak pembatas (bounding box) dari teks yang akan ditampilkan. text_bbox mengembalikan tuple yang berisi koordinat bounding box (kiri, atas, kanan, bawah) berdasarkan font yang diberikan. Koordinat ini memungkinkan kita mengetahui ukuran teks yang akan digambar.
        text_w = text_bbox[2] - text_bbox[0] # Baris ini menghitung lebar teks (text_w) dengan mengurangkan nilai kiri (text_bbox[0]) dari kanan (text_bbox[2]). Ini memberikan lebar aktual teks dalam piksel.
        text_h = text_bbox[3] - text_bbox[1] # Baris ini menghitung tinggi teks (text_h) dengan mengurangkan nilai atas (text_bbox[1]) dari bawah (text_bbox[3]). Ini memberikan tinggi aktual teks dalam piksel.
        
    # Menentukan posisi watermark
    positions = {
        "atas kanan": (image_w - text_w - 10, text_h + 10),
        "tengah kanan": (image_w - text_w - 10, (image_h + text_h) // 2),
        'bawah kanan': (image_w - text_w - 10, image_h - 10),
        "atas kiri": (10, text_h + 10),
        'tengah kiri': (10, (image_h + text_h) // 2),
        'bawah kiri': (10, image_h - 10),
        'tengah tengah': ((image_w - text_w) // 2, (image_h + text_h) // 2),
        'atas tengah': ((image_w - text_w) // 2, text_h + 10),
        'bawah tengah': ((image_w - text_w) // 2, image_h - 10)
    }

    # Dapatkan posisi awal
    position = positions.get(position_str.lower(), (image_w - text_w - 10, image_h - 10))

    # Periksa dan sesuaikan posisi agar teks tidak keluar dari batas gambar
    x, y = position
    if x + text_w > image_w:  # Jika teks keluar batas kanan gambar
        x = image_w - text_w - 10 # Jika teks keluar dari batas kanan gambar, baris ini akan menyesuaikan nilai x agar teks berada dalam batas kanan gambar dengan memberikan jarak 10 piksel dari tepi.
    if y + text_h > image_h:  # Jika teks keluar batas bawah gambar
        y = image_h - text_h - 10
    if x < 0:  # Jika teks keluar batas kiri gambar
        x = 10
    if y < 0:  # Jika teks keluar batas atas gambar
        y = text_h + 10

    position = (x, y)

    if external_font_used:
        # Ubah warna font ke format RGB untuk Pillow
        font_color_rgb = font_color[::-1]  # Membalik urutan dari BGR ke RGB
        
        # Tambahkan teks ke gambar menggunakan Pillow untuk font eksternal
        draw.text(position, text, fill=font_color_rgb, font=font)
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR) # Convert kembali dalam bentuk format openCV
    else:
        # Buat overlay untuk OpenCV text
        overlay = image.copy() # Salinan ini digunakan untuk menempatkan teks secara terpisah dari gambar asli, yang memungkinkan pengaturan transparansi (opacity) melalui efek overlay. 
        cv2.putText(overlay, text, position, font, font_scale, font_color, thickness, cv2.LINE_AA) # cv2.LINE_AA: jenis garis anti-aliasing untuk membuat tepi teks lebih halus.
        cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image) # Menggabungkan gambar overlay dengan teks dan gambar asli (image) menggunakan efek transparansi. 

    return image

def get_cv2_font(font_name):
    """Mengembalikan font OpenCV berdasarkan nama."""
    #font_name = font_name.lower()
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

    if font_name in font_dict:
        return font_dict[font_name]
    else:
        raise ValueError(f"Font '{font_name}' tidak ditemukan dalam daftar font OpenCV. Harap gunakan font yang tersedia.")

def get_cv2_fonts():
    """Mengembalikan daftar font OpenCV yang tersedia."""
    return {
        "hershey simplex",
        "hershey plain",
        "hershey duplex",
        "hershey complex",
        "hershey triplex",
        "hershey complex small",
        "hershey script simplex",
        "hershey script complex"
    }

def preprocess_image(image):
    """Melakukan preprocessing pada gambar."""
    # Adjust gamma
    gamma_corrected = adjust_gamma(image, gamma=1.0)
    # Remove noise
    denoised_image = remove_noise(gamma_corrected)
    # Sharpen the image
    sharpened_image = sharpen_image(denoised_image)
    # Unblur the image
    #final_image = unblur_image(sharpened_image)
    
    return sharpened_image

def adjust_gamma(image, gamma=1.0):
    """Menerapkan penyesuaian gamma pada gambar. Tingkat kecerahan gambar"""
    invGamma = 1.0 / gamma # Menghitung nilai kebalikan dari gamma, invGamma. Nilai ini digunakan untuk menentukan seberapa besar perubahan kecerahan gambar. Nilai gamma di atas 1 akan membuat gambar lebih gelap, sementara nilai di bawah 1 akan membuat gambar lebih terang.
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8") #  melakukan operasi penyesuaian gamma untuk setiap nilai pixel
    return cv2.LUT(image, table) # mengonversi setiap nilai pixel dalam gambar sesuai tabel

def sharpen_image(image):
    """Melakukan penajaman pada gambar menggunakan Unsharp Masking."""
    blurred = cv2.GaussianBlur(image, (5, 5), 0) # ukuran kernel yang digunakan untuk blurring (semakin besar kernel, semakin kabur hasilnya). 0: nilai standar deviasi yang otomatis disesuaikan berdasarkan ukuran kernel.
    sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0) # mengombinasikan gambar asli dan versi buramnya dengan bobot yang berbeda untuk mendapatkan efek tajam. memberikan bobot negatif (-0.5) pada gambar buram untuk mengurangi detail yang kabur dari gambar asli.
    return sharpened

def remove_noise(image):
    """Menghilangkan noise dari gambar menggunakan metode denoising."""
    #metode OpenCV yang dirancang untuk menghilangkan noise dari gambar berwarna.
    #h=10: Parameter filter yang menentukan kekuatan penghilangan noise. Semakin tinggi nilainya, semakin banyak noise yang dihilangkan, namun ini juga bisa menghilangkan detail gambar.
    #templateWindowSize=7: Ukuran jendela untuk perhitungan rata-rata sekitar setiap piksel, digunakan untuk mencari kesamaan. Ukuran yang umum adalah 7x7.
    #searchWindowSize=21: Ukuran jendela pencarian untuk menemukan area serupa di sekitar piksel. Ukuran yang lebih besar akan meningkatkan kualitas penghilangan noise tetapi menambah waktu pemrosesan.
    return cv2.fastNlMeansDenoisingColored(image, None, h=10, templateWindowSize=7, searchWindowSize=21)

# def unblur_image(image):
#     """Mengurangi blur pada gambar menggunakan filter Laplacian."""
#     laplacian_filter = cv2.Laplacian(image, cv2.CV_64F) # metode yang menggunakan filter Laplacian untuk mendeteksi tepi pada gambar
#     unblurred = cv2.subtract(image, laplacian_filter.astype(np.uint8)) # melakukan pengurangan nilai piksel antara gambar asli dan gambar dengan filter Laplacian untuk mengurangi blur dan meningkatkan ketajaman.
#     return unblurred

def preprocess_logo(logo, image_size, scale_factor=0.2):
    """Melakukan preprocessing pada logo: mengubah ukuran dan menghilangkan latar belakang."""
    # Mengubah ukuran logo agar proporsional dengan gambar
    #Mengambil ukuran terkecil dari image_size (antara lebar dan tinggi) agar logo tetap dalam proporsi yang sesuai dengan gambar utama.
    #Mengalikan hasilnya dengan scale_factor untuk menghitung scale_size, yaitu dimensi baru untuk logo dalam bentuk persegi.
    scale_size = int(min(image_size) * scale_factor)
    logo = cv2.resize(logo, (scale_size, scale_size), interpolation=cv2.INTER_AREA) # untuk memperkecil ukuran gambar secara efektif.
    logo_rgba = remove_background(logo)

    return logo_rgba

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

def add_logo_watermark(image, logo, position_str, opacity):
    """Menambahkan watermark logo ke gambar dengan transparansi di posisi yang ditentukan."""

    # logo = cv2.imread(logo, cv2.IMREAD_UNCHANGED)

    # if logo is None:
    #     raise ValueError("Logo tidak ditemukan.")

    # Dapatkan posisi berdasarkan input string
    position = get_watermark_position(image, logo, position_str)

    # Tambahkan logo ke gambar dengan transparansi
    # Mengambil nilai pixel dari logo.
    # Mengalikan nilai pixel logo dengan nilai transparansi yang telah disesuaikan.
    # Mengambil nilai pixel dari gambar asli di area yang sama.
    # Mengalikan nilai pixel gambar asli dengan nilai kebalikannya dari transparansi logo.
    # Menjumlahkan kedua hasil tersebut untuk mendapatkan nilai akhir pixel yang akan ditetapkan di gambar utama.
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
        font = None
        overlay=image.copy()
        # Try to get OpenCV font
        try:
            font = get_cv2_font(font_type)  # Try to get OpenCV font
            text_size, _ = cv2.getTextSize(watermark, font, font_scale, thickness)
            
        except ValueError:
            font = None  # Font not found, proceed to TTF handling

        if font is not None:
            # If font is found in OpenCV
            text_size, _ = cv2.getTextSize(watermark, font, font_scale, thickness)
            text_w, text_h = text_size

            optimal_position = find_optimal_position(image, (text_w, text_h))
            optimal_position = (max(optimal_position[0], 0),
                                max(optimal_position[1], 0))
            optimal_position = (min(optimal_position[0], image.shape[1] - text_w),
                                min(optimal_position[1], image.shape[0] - text_h))
            # max() untuk memastikan bahwa koordinat x dan y dari optimal_position tidak negatif, sehingga posisi berada dalam area gambar dan tidak keluar dari batas kiri atau atas gambar.
            # min() memastikan bahwa posisi x dan y dari optimal_position tidak melampaui batas kanan atau bawah gambar. 
            overlay = image.copy()
            cv2.putText(overlay, watermark, optimal_position, font, font_scale, font_color, thickness, cv2.LINE_AA)
        else:
            # If font not found in OpenCV, check for TTF file
            ttf_font_path = os.path.join('Font', f"{font_type}.ttf")
            print(f"Looking for font at: {ttf_font_path}")  # Debug output
            if os.path.exists(ttf_font_path):
                #print("Font file found.")  # Debug output
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(pil_image)
                font = ImageFont.truetype(ttf_font_path, int(font_scale * 20))  # Adjust size as necessary
                
                # Get text bounding box with PIL
                text_bbox = draw.textbbox((0, 0), watermark, font=font)
                text_w = text_bbox[2] - text_bbox[0]
                text_h = text_bbox[3] - text_bbox[1]

                optimal_position = find_optimal_position(image, (text_w, text_h))

                # Convert font_color to RGB for PIL
                font_color = font_color[::-1]  # Membalik urutan dari BGR ke RGB
                draw.text(optimal_position, watermark, font=font, fill=font_color)

                # Convert back to OpenCV image
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            else:
                raise ValueError(f"Font TTF '{ttf_font_path}' tidak ditemukan.")

        # Combine overlay with the original image using opacity
        cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

    return image

def add_watermark_below_image(image, font_type='hershey simplex', text=None, bar_height=50, opacity=0.3, font_color=(0, 0, 0), font_scale=1, thickness=2, scale_factor=0.7):
    """Menambahkan watermark teks di bawah gambar dengan opsi untuk font OpenCV dan TTF."""
    
    # Ukuran gambar asli
    h, w, _ = image.shape

    # Buat bar putih di bawah gambar
    bar = np.ones((bar_height, w, 3), dtype=np.uint8) * 255  # Membuat bar putih dengan tinggi tertentu

    # Gabungkan gambar asli dengan bar putih di bawahnya
    combined_image = np.vstack((image, bar)).astype(np.uint8)

    # Sesuaikan skala teks berdasarkan scale factor
    scaled_font_scale = font_scale * scale_factor

    font = None
    # Coba ambil font OpenCV
    try:
        font = get_cv2_font(font_type)  # Coba mendapatkan font OpenCV
        #color_to_use = get_color_from_string(font_color)  # Ambil warna BGR untuk OpenCV font
    except ValueError:
        font = None  # Font tidak ditemukan, lanjut ke TTF

    if font is not None:
        # Jika font ditemukan di OpenCV
        text_size = cv2.getTextSize(text, font, scaled_font_scale, thickness)[0]
        text_x = w - text_size[0] - 10  # Teks di sebelah kanan dengan padding 10 px
        text_y = h + (bar_height + text_size[1]) // 2

        # Buat overlay untuk teks saja
        text_overlay = combined_image.copy()

        # Tambahkan teks ke bar putih pada overlay
        cv2.putText(text_overlay, text, (text_x, text_y), font, scaled_font_scale, font_color, thickness, cv2.LINE_AA)

        # Gabungkan teks overlay dengan gambar utama menggunakan opacity
        cv2.addWeighted(text_overlay[h:, :], opacity, combined_image[h:, :], 1 - opacity, 0, combined_image[h:, :])

    else:
        # Jika font tidak ditemukan di OpenCV, cari file TTF
        ttf_font_path = os.path.join('Font', f"{font_type}.ttf")
        print(f"Looking for font at: {ttf_font_path}")  # Debug output
        if os.path.exists(ttf_font_path):
            #print("Font file found.")  # Debug output
            # Convert OpenCV image to PIL image
            pil_image = Image.fromarray(cv2.cvtColor(combined_image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)
            font = ImageFont.truetype(ttf_font_path, int(scaled_font_scale * 20))  # Adjust size as necessary
            
            # Get text bounding box with PIL
            text_size = draw.textbbox((0, 0), text, font=font)
            text_w = text_size[2] - text_size[0]
            text_h = text_size[3] - text_size[1]

            text_x = w - text_w - 10  # Teks di sebelah kanan dengan padding 10 px
            text_y = h + (bar_height + text_h) // 2

            # Convert font_color to RGB for PIL
            font_color = font_color[::-1] 
            draw.text((text_x, text_y), text, font=font, fill=font_color)

            # Convert back to OpenCV image
            combined_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        else:
            raise ValueError(f"Font TTF '{ttf_font_path}' tidak ditemukan.")

    return combined_image

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

def process_multiple_files(file_paths, watermark_type=None, enchance_quality=None, font_type=None, text=None, logo_path=None, position_str=None, opacity=None, bar_height=50, font_color=(255, 255, 255), scale_factor=0.3, thickness=2, output_format=None):
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

                #image_with_watermark = open_cv_image

                # Watermark teks
                if watermark_type == 'text':
                    font_color = get_color_from_string(font_color)
                    if text is None:
                        #raise ValueError("Text harus disediakan untuk watermark jenis teks.")
                        output_files[1] = "Error While Embedding Watermark: Text harus disediakan untuk watermark jenis teks."
                        return output_files
                    
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
                        #raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                        output_files[1] = "Error While Embedding Watermark: Path logo harus disediakan untuk watermark jenis logo."
                        return output_files
                    
                    # Cek apakah logo bukan PNG, jika iya, konversi ke PNG
                    logo_ext = os.path.splitext(logo_path)[1].lower()
                    if logo_ext in ['.jpg', '.jpeg']:
                        logo_image = cv2.imread(logo_path)
                        if logo_image is not None:
                            converted_logo_path = logo_path.replace(logo_ext, '.png')
                            cv2.imwrite(converted_logo_path, logo_image)
                            logo_path = converted_logo_path  # Set logo_path ke file PNG baru
                        else:
                            #raise ValueError(f"Logo tidak dapat dibuka: {logo_path}")
                            output_files[1] = "Error While Embedding Watermark: Logo tidak dapat dibuka"
                            return output_files
                    
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
                elif output_format.lower() == 'pdf':
                    pdf_output_filename = os.path.join(f'Watermarked{os.path.basename(file_paths)}')
                    watermarked_images[0].save(pdf_output_filename, save_all=True, append_images=watermarked_images[1:], resolution=300)
                else:
                    #raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")
                    output_files[1] = "Error While Embedding Watermark: Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'."
                    return output_files

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
                #print("preproces")
                preprocessed_image = preprocess_image(image)
            else:
                preprocessed_image = image

            #image_with_watermark = preprocessed_image

            if watermark_type == 'text':
                font_color = get_color_from_string(font_color)
                if text is None:
                    #raise ValueError("Text harus disediakan untuk watermark jenis teks.")
                    output_files[1] = "Error While Embedding Watermark: Text harus disediakan untuk watermark jenis teks."
                    return output_files
              
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
                    #raise ValueError("Path logo harus disediakan untuk watermark jenis logo.")
                    output_files[1] = "Error While Embedding Watermark: Path Logo harus disediakan untuk watermark jenis logo."
                    return output_files
                
                 # Cek apakah logo bukan PNG, jika iya, konversi ke PNG
                logo_ext = os.path.splitext(logo_path)[1].lower()
                if logo_ext in ['.jpg', '.jpeg']:
                    logo_image = cv2.imread(logo_path)
                    if logo_image is not None:
                        converted_logo_path = logo_path.replace(logo_ext, '.png')
                        cv2.imwrite(converted_logo_path, logo_image)
                        logo_path = converted_logo_path  # Set logo_path ke file PNG baru
                    else:
                        #raise ValueError(f"Logo tidak dapat dibuka: {logo_path}")
                        output_files[1] = "Error While Embedding Watermark: Logo tidak dapat dibuka"
                        return output_files
                    
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

            # Cek apakah image_with_watermark kosong
            if image_with_watermark is None or image_with_watermark.size == 0:
                output_files[1] = "Error: Gambar hasil watermarking kosong."
                return output_files

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
                #raise ValueError("Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'.")
                output_files[1] = "Error While Embedding Watermark: Format output tidak didukung. Silakan pilih 'jpg', 'jpeg', atau 'png'."
                return output_files

            return output_files

    except Exception as e:
        output_files[1] = f"Error While Embedding Watermark: {str(e)}"
        return output_files
