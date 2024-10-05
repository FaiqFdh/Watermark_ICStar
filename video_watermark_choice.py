import cv2
import numpy as np
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

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

def add_text_watermark_video(frame, text, position, font_color,font_type, thickness=2, scale_factor=0.05, opacity=1.0):
    """Menambahkan watermark teks ke frame dengan transparansi di posisi yang ditentukan."""
    font = get_cv2_font(font_type)
    #font = cv2.FONT_HERSHEY_SIMPLEX
    scale = scale_factor * frame.shape[1] / 1000  # Menyesuaikan ukuran teks
    text_size = cv2.getTextSize(text, font, scale, thickness)[0]

    # Menentukan posisi teks
    if position == 'tengah tengah':#Tengah
        position = ((frame.shape[1] - text_size[0]) // 2, (frame.shape[0] + text_size[1]) // 2)
    elif position == 'atas kanan':#Kanan Atas
        position = (frame.shape[1] - text_size[0] - 10, text_size[1] + 10)
    elif position == 'bawah kanan':#Kanan Bawah
        position = (frame.shape[1] - text_size[0] - 10, frame.shape[0] - 10)
    elif position == 'atas kiri':#Kiri Atas
        position = (10, text_size[1] + 10)
    elif position == 'bawah kiri':#Kiri Bawah
        position = (10, frame.shape[0] - 10)
    elif position == 'atas tengah':#Tengah Atas
        position = ((frame.shape[1] - text_size[0]) // 2, text_size[1] + 10)
    elif position == 'bawah tengah':#Tengah Bawah
        position = ((frame.shape[1] - text_size[0]) // 2, frame.shape[0] - 10)
    elif position == 'tengah kiri':  # Kiri Tengah
        position = (10, (frame.shape[0] - text_size[1]) // 2)
    elif position == 'tengah kanan':  # Kanan Tengah
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
        'atas kanan' : (frame_w - logo_w, 0),#Kanan Atas
        'tengah kanan' : (frame_w - logo_w, (frame_h - logo_h) // 2),#Kanan Tengah
        'bawah kanan': (frame_w - logo_w, frame_h - logo_h),#Kanan Bawah
        'atas kiri' : (0, 0),#Kiri Atas
        'tengah kiri' : (0, (frame_h - logo_h) // 2),#Kiri Tengah
        'bawah kiri' : (0, frame_h - logo_h),#Kiri Bawah
        'tengah tengah' : ((frame_w - logo_w) // 2, (frame_h - logo_h) // 2),#Tengah
        'atas tengah' : ((frame_w - logo_w) // 2, 0),#Tengah Atas
        'bawah tengah' : ((frame_w - logo_w) // 2, frame_h - logo_h)#Tengah Bawah
    }

    return positions.get(position_str.lower(), (frame_w - logo_w, frame_h - logo_h))
    #return positions.get(position_str, (frame_w - logo_w, frame_h - logo_h))

def add_watermark_to_multiple_videos(video_paths, watermark_type, output_path, output_format='mp4', **kwargs):
    """Menambahkan watermark ke beberapa video berdasarkan jenis watermark yang dipilih."""
    output_video_paths = []  # Menyimpan daftar video yang berhasil diproses
    error_messages = []  # Menyimpan pesan error jika ada
    
    # Buat folder output jika belum ada
    os.makedirs(output_path, exist_ok=True)

    # Tentukan codec video berdasarkan format output
    if output_format == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif output_format == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    elif output_format == 'mov':
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
    else:
        raise ValueError(f"Tipe format output '{output_format}' tidak didukung. Pilih antara 'mp4', 'avi', atau 'mov'.")

    # Loop melalui semua video yang akan diberi watermark
    for input_video_path in video_paths:
        try:
            # Coba buka video input
            cap = cv2.VideoCapture(input_video_path)
            if not cap.isOpened():
                raise ValueError(f"Video tidak dapat dibuka: {input_video_path}")

            # Ambil informasi video (fps, ukuran frame, dll.)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Generate output filename secara otomatis
            filename = os.path.basename(input_video_path)
            output_video_path = os.path.join(output_path, f"Watermark_{filename.split('.')[0]}.{output_format}")
            output_video_paths.append(output_video_path)

            # Buat video writer
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

            enhance_quality = kwargs.get('enhance_quality', True)  # Ambil opsi enhance_quality

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Proses denoise dan sharpening frame jika diperlukan
                if enhance_quality:
                    #print('Dilakukan Preprocessing')
                    frame = denoise_frame(frame)
                    frame = sharpen_frame(frame)

                #print('Tidak Dilakukan Preprocessing')
                # Tambahkan watermark berdasarkan jenis yang dipilih
                if watermark_type == 'logo':
                    logo_path = kwargs.get('logo_path')
                    position_str = kwargs.get('position_str', 'kanan bawah')
                    opacity = kwargs.get('opacity', 0.6)

                    # Load logo dan preprocess
                    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
                    if logo is None:
                        raise ValueError(f"Logo tidak dapat dibuka: {logo_path}")
                    logo = preprocess_logo_video(logo, kwargs.get('scale_factor', 0.3))

                    # Dapatkan posisi watermark
                    position = get_watermark_position_video(frame, logo, position_str)

                    # Tambahkan logo watermark
                    frame = add_logo_watermark_video(frame, logo, position, opacity)

                elif watermark_type == 'text':
                    text = kwargs.get('text', '')
                    position_str = kwargs.get('position_str', 'bawah kanan')

                    # Dapatkan warna font dari input user (gunakan putih sebagai default)
                    color_str = kwargs.get('font_color', '#FFFFFF')
                    font_color = get_color_from_string(color_str)  # Ambil warna dari hex atau nama warna
                    
                    thickness = kwargs.get('thickness', 2)
                    scale_factor = kwargs.get('scale_factor', 0.5)
                    opacity = kwargs.get('opacity', 0.6)
                    font_type = kwargs.get('font_type', 'hershey simplex')

                    # Tambahkan teks watermark
                    frame = add_text_watermark_video(frame, text, position_str, font_color, font_type, thickness, scale_factor, opacity)

                # Tulis frame ke video output
                out.write(frame)

            # Bersihkan resources
            cap.release()
            out.release()

        except Exception as e:
            # Jika terjadi error, tambahkan pesan error dan lanjutkan ke video berikutnya
            error_messages.append(f"Error pada video {input_video_path}: {str(e)}")
    
    cv2.destroyAllWindows()

    # Return daftar video output yang berhasil dihasilkan, atau error jika ada
    if error_messages:
        combined_list = output_video_paths + error_messages  # Gabungkan output video dengan pesan error
        return combined_list
    else:
        return ["Watermark"] + output_video_paths # Return "Watermark" sebagai penanda sukses dan output video paths

# def add_watermark_to_multiple_videos(video_paths, watermark_type, output_path, output_format='mp4', **kwargs):
    """Menambahkan watermark ke beberapa video berdasarkan jenis watermark yang dipilih."""
    output_video_paths = []  # Menyimpan daftar video yang berhasil diproses
    error_messages = []  # Menyimpan pesan error jika ada
    
    # Buat folder output jika belum ada
    os.makedirs(output_path, exist_ok=True)

    # Tentukan codec video berdasarkan format output
    if output_format == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif output_format == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    elif output_format == 'mov':
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
    else:
        raise ValueError(f"Tipe format output '{output_format}' tidak didukung. Pilih antara 'mp4', 'avi', atau 'mov'.")

    # Loop melalui semua video yang akan diberi watermark
    for input_video_path in video_paths:
        try:
            # Coba buka video input
            cap = cv2.VideoCapture(input_video_path)
            if not cap.isOpened():
                raise ValueError(f"Video tidak dapat dibuka: {input_video_path}")

            # Ambil informasi video (fps, ukuran frame, dll.)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Generate output filename secara otomatis
            filename = os.path.basename(input_video_path)
            output_video_path = os.path.join(output_path, f"Watermark_{filename.split('.')[0]}.{output_format}")
            output_video_paths.append(output_video_path)

            # Buat video writer
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Proses denoise dan sharpening frame jika diperlukan
                frame = denoise_frame(frame)
                frame = sharpen_frame(frame)

                # Tambahkan watermark berdasarkan jenis yang dipilih
                if watermark_type == 'logo':
                    logo_path = kwargs.get('logo_path')
                    position_str = kwargs.get('position_str', 'kanan bawah')
                    opacity = kwargs.get('opacity', 0.6)

                    # Load logo dan preprocess
                    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
                    if logo is None:
                        raise ValueError(f"Logo tidak dapat dibuka: {logo_path}")
                    logo = preprocess_logo_video(logo, kwargs.get('scale_factor', 0.3))

                    # Dapatkan posisi watermark
                    position = get_watermark_position_video(frame, logo, position_str)

                    # Tambahkan logo watermark
                    frame = add_logo_watermark_video(frame, logo, position, opacity)

                elif watermark_type == 'text':
                    text = kwargs.get('text', '')
                    position_str = kwargs.get('position_str', 'bawah kanan')

                    # Dapatkan warna font dari input user (gunakan putih sebagai default)
                    color_str = kwargs.get('font_color', '#FFFFFF')
                    font_color = get_color_from_string(color_str)  # Ambil warna dari hex atau nama warna
                    
                    thickness = kwargs.get('thickness', 2)
                    scale_factor = kwargs.get('scale_factor', 0.5)
                    opacity = kwargs.get('opacity', 0.6)
                    font_type = kwargs.get('font_type', 'hershey simplex')

                    # Tambahkan teks watermark
                    frame = add_text_watermark_video(frame, text, position_str, font_color, font_type, thickness, scale_factor, opacity)

                # Tulis frame ke video output
                out.write(frame)

            # Bersihkan resources
            cap.release()
            out.release()

        except Exception as e:
            # Jika terjadi error, tambahkan pesan error dan lanjutkan ke video berikutnya
            error_messages.append(f"Error pada video {input_video_path}: {str(e)}")
    
    cv2.destroyAllWindows()

    # Return daftar video output yang berhasil dihasilkan, atau error jika ada
    if error_messages:
        combined_list = output_video_paths + error_messages  # Gabungkan output video dengan pesan error
        return combined_list
    else:
        return ["Watermark"] + output_video_paths  # Return "Watermark" sebagai penanda sukses dan output video paths


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