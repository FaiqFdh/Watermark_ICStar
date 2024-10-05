from watermark_handler import run_watermark_handler
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# Fungsi untuk memilih file menggunakan tkinter
# def select_files():
#     Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
#     file_paths = askopenfilenames(title="Pilih File", filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("Video files", "*.mp4 *.avi *.mov"), ("PDF files", "*.pdf")])
#     return file_paths

# # Memilih file secara langsung dengan tkinter
# file_paths = select_files()

# # Pastikan ada file yang dipilih
# if not file_paths:
#     print("Tidak ada file yang dipilih.")
# else:
#     watermark_type ='logo'
#     # Memproses file berdasarkan ekstensi
#     for file_path in file_paths:
#         ext = file_path.split('.')[-1].lower()
        
#         if ext in ['jpg', 'jpeg', 'png' ,'pdf']:
#             # Untuk Gambar dengan Watermark Text
#             if watermark_type == 'text':
#                 result = run_watermark_handler(
#                     file_paths=[file_path],
#                     text='Sample Watermark',
#                     font_type='hershey script simplex',
#                     font_color="#49FFCE",
#                     position_str='bawah kanan',
#                     opacity=0.3,
#                     output_format='png',
#                     enchance_quality=False,
#                     watermark_type='text',
#                     output_path='Watermarked Content'
#                 )
#                 print(watermark_type , result)

#             elif watermark_type=='logo':
#                 # Untuk Gambar dengan Watermark Logo
#                 result = run_watermark_handler(
#                     file_paths=[file_path],
#                     watermark_type='logo',
#                     output_path='Watermarked Content',
#                     logo_path='Gambar\\watermark logo.png',
#                     position_str='auto',
#                     opacity=0.5,
#                     output_format='png',
#                     enchance_quality=True
#                 )
#                 print(watermark_type , result)

#         elif ext in ['mp4', 'avi', 'mov']:
#             # Untuk Video dengan Watermark Logo
#             if watermark_type == 'logo':
#                 result = run_watermark_handler(
#                     file_paths=[file_path],
#                     logo_path='Gambar\\watermark logo.png',
#                     position_str='atas kanan',
#                     opacity=0.5,
#                     output_format='mp4',
#                     enchance_quality=True,
#                     output_path="Watermarked Content",
#                     watermark_type='logo'
#                 )
#                 print(watermark_type , result)

#             elif watermark_type == 'text':
#             # Untuk Video dengan Watermark Text
#                 result = run_watermark_handler(
#                     file_paths=[file_path],
#                     text='Hak Cipta 2024',
#                     font_type='hershey script simplex',
#                     font_color="red",  # Nama warna
#                     position_str='bawah kanan',
#                     opacity=0.5,
#                     output_path="Watermarked Content",
#                     watermark_type='text',
#                     output_format='mp4',
#                     enchance_quality=False
#                 )
#                 print(watermark_type,result)

##___________________________________________________________________________________________________________________________##

from watermark_handler import run_watermark_handler
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# Fungsi untuk memilih file menggunakan tkinter
def select_files():
    Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
    file_paths = askopenfilenames(title="Pilih File", filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("Video files", "*.mp4 *.avi *.mov"), ("PDF files", "*.pdf")])
    return file_paths

def watermark_image(file_path, watermark_type):
    """Menambahkan watermark ke gambar berdasarkan tipe yang dipilih."""
    if watermark_type == 'text':
        result = run_watermark_handler(
            file_paths=[file_path],
            text='Sample Watermark',
            font_type='hershey script simplex',
            font_color="#49FFCE",
            position_str='bawah kanan',
            opacity=0.3,
            output_format='png',
            enchance_quality=False,
            watermark_type='text',
            output_path='Watermarked Content'
        )
        print(watermark_type, result)

    elif watermark_type == 'logo':
        # Untuk Gambar dengan Watermark Logo
        result = run_watermark_handler(
            file_paths=[file_path],
            output_path='Watermarked Content',
            logo_path='Gambar\\watermark logo.png',
            position_str='auto',
            opacity=0.5,
            output_format='png',
            watermark_type='logo',
            enchance_quality=True
        )
        print(watermark_type, result)

def watermark_video(file_path, watermark_type):
    """Menambahkan watermark ke video berdasarkan tipe yang dipilih."""
    if watermark_type == 'logo':
        result = run_watermark_handler(
            file_paths=[file_path],
            logo_path='Gambar\\watermark logo.png',
            position_str='atas kanan',
            opacity=0.5,
            output_format='mp4',
            enchance_quality=True,
            output_path="Watermarked Content",
            watermark_type='logo'
        )
        print(watermark_type, result)

    elif watermark_type == 'text':
        # Untuk Video dengan Watermark Text
        result = run_watermark_handler(
            file_paths=[file_path],
            text='Hak Cipta 2024',
            font_type='hershey script simplex',
            font_color="red",  # Nama warna
            position_str='bawah kanan',
            opacity=0.5,
            output_format='mp4',
            enchance_quality=False,
            output_path="Watermarked Content",
            watermark_type='text'
        )
        print(watermark_type, result)

# Memilih file secara langsung dengan tkinter
file_paths = select_files()

# Pastikan ada file yang dipilih
if not file_paths:
    print("Tidak ada file yang dipilih.")
else:
    watermark_type = 'text'  # Ubah ini sesuai kebutuhan, bisa 'text' atau 'logo'
    #watermark_type = input("Tipe Watermark: ")
    # Memproses file berdasarkan ekstensi
    for file_path in file_paths:
        ext = file_path.split('.')[-1].lower()
        
        if ext in ['jpg', 'jpeg', 'png', 'pdf']:
            watermark_image(file_path, watermark_type)

        elif ext in ['mp4', 'avi', 'mov']:
            watermark_video(file_path, watermark_type)
