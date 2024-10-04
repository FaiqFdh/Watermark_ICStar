import cv2
import numpy as np
import os
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

def denoise_frame(frame):
    """Mengurangi noise pada frame menggunakan Gaussian Blur."""
    return cv2.GaussianBlur(frame, (5, 5), 0)

def sharpen_frame(frame):
    """Menajamkan frame dengan filter kernel."""
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    return cv2.filter2D(frame, -1, kernel)

def preprocess_logo_video(logo, scale_factor):
    """Melakukan preprocessing pada logo: mengubah ukuran, menghilangkan latar belakang."""
    logo_resized = cv2.resize(logo, (int(logo.shape[1] * scale_factor), int(logo.shape[0] * scale_factor)))
    return remove_background_video(logo_resized)

def remove_background_video(logo):
    """Menghilangkan latar belakang dari logo menggunakan thresholding."""
    gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    logo = cv2.bitwise_and(logo, logo, mask=mask)

    if len(logo.shape) == 3:  # Memastikan logo memiliki 3 saluran
        b, g, r = cv2.split(logo)
        alpha_channel = mask
        logo_rgba = cv2.merge((b, g, r, alpha_channel))
        return logo_rgba
    else:
        return logo  # Jika logo tidak memiliki 3 saluran, kembalikan tanpa perubahan

def add_logo_watermark_video(frame, logo, position, opacity=1.0):
    """Menambahkan watermark logo ke frame dengan transparansi di posisi yang ditentukan."""
    h, w, _ = logo.shape
    for c in range(0, 3):
        frame[position[1]:position[1]+h, position[0]:position[0]+w, c] = \
            (logo[:, :, c] * (logo[:, :, 3] / 255.0 * opacity) +
             frame[position[1]:position[1]+h, position[0]:position[0]+w, c] *
             (1.0 - logo[:, :, 3] / 255.0 * opacity))
    return frame

def add_text_watermark_video(frame, text, position, font_color, thickness=2, scale_factor=0.05, opacity=1.0):
    """Menambahkan watermark teks ke frame dengan transparansi di posisi yang ditentukan."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = scale_factor * frame.shape[1] / 1000  # Menyesuaikan ukuran teks
    text_size = cv2.getTextSize(text, font, scale, thickness)[0]

    # Menentukan posisi teks
    if position == 4:#Tengah
        position = ((frame.shape[1] - text_size[0]) // 2, (frame.shape[0] + text_size[1]) // 2)
    elif position == 2:#Kanan Atas
        position = (frame.shape[1] - text_size[0] - 10, text_size[1] + 10)
    elif position == 8:#Kanan Bawah
        position = (frame.shape[1] - text_size[0] - 10, frame.shape[0] - 10)
    elif position == 0:#Kiri Atas
        position = (10, text_size[1] + 10)
    elif position == 6:#Kiri Bawah
        position = (10, frame.shape[0] - 10)
    elif position == 1:#Tengah Atas
        position = ((frame.shape[1] - text_size[0]) // 2, text_size[1] + 10)
    elif position == 7:#Tengah Bawah
        position = ((frame.shape[1] - text_size[0]) // 2, frame.shape[0] - 10)
    elif position == 3:  # Kiri Tengah
        position = (10, (frame.shape[0] - text_size[1]) // 2)
    elif position == 5:  # Kanan Tengah
        position = (frame.shape[1] - text_size[0] - 10, (frame.shape[0] - text_size[1]) // 2)
    else:
        raise ValueError(f"Posisi '{position}' tidak dikenal.")

    overlay = frame.copy()
    # Memastikan position adalah tuple dengan dua nilai
    if isinstance(position, tuple) and len(position) == 2:
        cv2.putText(overlay, text, position, font, scale, font_color, thickness, cv2.LINE_AA)
    else:
        raise ValueError("Posisi harus berupa tuple yang berisi dua nilai (x, y).")

    # Menggabungkan teks dengan transparansi
    cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
    return frame


def get_watermark_position_video(frame, watermark, position_str):
    """Mengembalikan koordinat (x, y) berdasarkan string posisi yang diberikan."""
    frame_h, frame_w, _ = frame.shape
    logo_h, logo_w, _ = watermark.shape

    positions = {
        2 : (frame_w - logo_w, 0),#Kanan Atas
        5 : (frame_w - logo_w, (frame_h - logo_h) // 2),#Kanan Tengah
        8: (frame_w - logo_w, frame_h - logo_h),#Kanan Bawah
        0 : (0, 0),#Kiri Atas
        3 : (0, (frame_h - logo_h) // 2),#Kiri Tengah
        6 : (0, frame_h - logo_h),#Kiri Bawah
        4 : ((frame_w - logo_w) // 2, (frame_h - logo_h) // 2),#Tengah
        1 : ((frame_w - logo_w) // 2, 0),#Tengah Atas
        7 : ((frame_w - logo_w) // 2, frame_h - logo_h)#Tengah Bawah
    }

    #return positions.get(position_str.lower(), (frame_w - logo_w, frame_h - logo_h))
    return positions.get(position_str, (frame_w - logo_w, frame_h - logo_h))

import cv2
import os


def add_watermark_to_multiple_videos(video_paths, watermark_type, output_path,output_format='mp4', **kwargs):
    """Menambahkan watermark ke beberapa video berdasarkan jenis watermark yang dipilih."""
    output_video_paths = []
    
    # Buat folder "Watermarked Video" jika belum ada
    output_folder = output_path
    os.makedirs(output_folder, exist_ok=True)

    # Tentukan codec video berdasarkan format output
    if output_format == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif output_format == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    elif output_format == 'mov':
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
    else:
        raise ValueError(f"Tipe format output '{output_format}' tidak didukung. Pilih antara 'mp4', 'avi', atau 'mov'.")

    for input_video_path in video_paths:
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            raise ValueError(f"Video tidak dapat dibuka: {input_video_path}")

        # Ambil informasi video (fps, ukuran frame, dll.)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Generate output filename secara otomatis
        filename = os.path.basename(input_video_path)
        output_video_path = os.path.join(output_folder, f"Watermark_{filename.split('.')[0]}.{output_format}")
        output_video_paths.append(output_video_path)

        # Buat video writer
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = denoise_frame(frame)
            frame = sharpen_frame(frame)

            # Jika watermark berupa logo
            if watermark_type == 'logo':
                logo_path = kwargs.get('logo_path')
                position_str = kwargs.get('position_str', 'kanan bawah')
                opacity = kwargs.get('opacity', 1.0)

                # Load logo dan preprocess
                logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
                if logo is None:
                    raise ValueError(f"Logo tidak dapat dibuka: {logo_path}")
                logo = preprocess_logo_video(logo, kwargs.get('scale_factor', 0.3))

                # Dapatkan posisi watermark
                position = get_watermark_position_video(frame, logo, position_str)

                # Tambahkan logo watermark
                frame = add_logo_watermark_video(frame, logo, position, opacity)

            # Jika watermark berupa teks
            elif watermark_type == 'text':
                text = kwargs.get('text', '')
                position_str = kwargs.get('position_str', 'tengah')

                # Dapatkan warna font dari input user (gunakan putih sebagai default)
                color_str = kwargs.get('font_color', 'putih')  # default 'putih'
                font_color = get_color_from_string(color_str)  # Ambil warna dari kamus
                
                thickness = kwargs.get('thickness', 1)
                scale_factor = kwargs.get('scale_factor', 0.5)
                opacity = kwargs.get('opacity', 1.0)

                # Tambahkan teks watermark
                frame = add_text_watermark_video(frame, text, position_str, font_color, thickness, scale_factor, opacity)

            # Tulis frame ke video output
            out.write(frame)

        # Bersihkan
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    return output_video_paths  # Mengembalikan list dari path video output

# Contoh penggunaan untuk beberapa video
# Contoh penggunaan untuk multiple file upload
# Fungsi untuk memilih file menggunakan dialog file picker dari tkinter
# def select_files():
#     Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
#     file_paths = askopenfilenames(title="Pilih Video", filetypes=[("Video files", "*.mp4 *.avi *.mov")])
#     return file_paths

# # Memilih file secara langsung dengan tkinter
# file_paths = select_files()

# output_videos = add_watermark_to_multiple_videos(
#     video_paths=file_paths,
#     watermark_type='logo',
#     output_path="Watermarked Content",
#     logo_path='Gambar\\watermark logo.png',
#     position_str=8,
#     opacity=0.5
# )

# print(f"Video dengan watermark disimpan sebagai: {output_videos}")

# output_videos = add_watermark_to_multiple_videos(
#     video_paths=file_paths,
#     watermark_type='text',
#     output_path='Watermarked Content',
#     text='Hak Cipta 2024',
#     position_str=8,#'kanan bawah',
#     font_color="#49FFCE",  # Nama warna
#     opacity=0.3,
#     #thickness=2
# )

# print(f"Video dengan watermark disimpan sebagai: {output_videos}")