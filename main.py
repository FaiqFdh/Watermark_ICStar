from watermark_handler import run_watermark_handler
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# Fungsi untuk memilih file menggunakan tkinter
# def select_files():
#     Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
#     file_paths = askopenfilenames(title="Pilih File", filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("Video files", "*.mp4 *.avi *.mov"), ("PDF files", "*.pdf")])
#     return file_paths

def watermark_image(file_path,          # Content File Path (String)
                    logo_path=None,     # Watermark File Path (String)
                    text=None,          # Watermark Text (String)
                    font_type=None,     # Watermak Text Font (String)
                    font_color=None,    # Watermark Text Color (String)
                    position_str=None,  # Watermark Position (String)
                    opacity=None,       # Watermark Opacity (Float)
                    output_format=None, # Output Format (String)
                    enchance_quality=None, # Enchance Quality (Boolean)
                    watermark_type=None):
    """Menambahkan watermark ke gambar berdasarkan tipe yang dipilih."""
    
    if not logo_path:  # Jika logo_path kosong atau None
        # Untuk watermark teks
        result = run_watermark_handler(
            file_paths=file_path,
            text=text,
            font_type=font_type,
            font_color=font_color,
            position_str=position_str,
            opacity=opacity,
            output_format=output_format,
            enchance_quality=enchance_quality,
            watermark_type='text'
        )
        #print('watermark text', result)
        return result
    
    else:
        # Untuk Gambar dengan Watermark Logo
        result = run_watermark_handler(
            file_paths=file_path,
            logo_path=logo_path,
            position_str=position_str,
            opacity=opacity,
            output_format=output_format,
            enchance_quality=enchance_quality,
            watermark_type='logo'
        )
        #print('watermark logo', result)
        return result
    

def watermark_video(file_path,              # Content File Path (String)
                    logo_path=None,         # Watermark File Path (String)
                    text=None,              # Watermark Text (String)
                    font_type=None,         # Watermark Text Font (String)
                    font_color=None,        # Watermark Font Color (String)
                    position_str=None,      # Watermark Position (String)
                    opacity=None,           # Watermark Opacity (Float)
                    output_format=None,     # Output Format (String)
                    enchance_quality=None,  # Enhchance Quality (Boolean)
                    watermark_type=None): 
    """Menambahkan watermark ke video berdasarkan tipe yang dipilih."""
    
    if not logo_path:  # Jika logo_path kosong atau None
        # Untuk watermark teks
        result = run_watermark_handler(
            file_paths=file_path,
            text=text,
            font_type=font_type,
            font_color=font_color,
            position_str=position_str,
            opacity=opacity,
            output_format=output_format,
            enchance_quality=enchance_quality,
            watermark_type='text'
        )
        #print('watermark text', result)
        return result
    
    else:
        # Untuk Video dengan Watermark Logo
        result = run_watermark_handler(
            file_paths=file_path,
            logo_path=logo_path,
            position_str=position_str,
            opacity=opacity,
            output_format=output_format,
            enchance_quality=enchance_quality,
            watermark_type='logo'
        )
        #print('watermark logo', result)
        return result

#file_paths = ['Gambar\komputer mainframe1.jpg','Gambar\shopping after.jpg']
#file_paths = 'Gambar\gambar pdf2.pdf'
#file_paths = "Gambar\komputer mainframe1.jpg"

# results = watermark_image(file_paths,
#                     text='Sample Watermark',font_type='hershey script simplex',
#                     font_color='red',position_str='bawah kanan',opacity=0.3,output_format='png',
#                     enchance_quality=True,
#                     #logo_path=None)
#                     logo_path='Gambar\\watermark logo.png')

# print(results)
#file_paths = 'Gambar\\Content File.png'
#file_paths = "Gambar\komputer mainframe1.jpg"
# file_paths = 'Gambar\shopping after.jpg'
# results = watermark_image(file_paths,
#                           logo_path='Gambar\Watermark File.png',
#                           #logo_path='Gambar\\watermark logo.png',
#                             text='',
#                             font_type='',
#                             font_color='',
#                             position_str='bawah kanan',
#                             opacity=0.30,
#                             output_format='jpg',
#                             enchance_quality=True)
#                             #logo_path=None)

# print(results)

# import cv2
# logo_path='Gambar\\Watermark File.png'
# logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
# if logo is None:
#     print("Gambar logo tidak dapat dibaca. Pastikan format dan path benar.")
# else:
#     print("Bentuk logo:", logo.shape)

# import numpy as np

# # Mengambil channel alpha
# alpha_channel = logo[:, :, 3]

# # Cek nilai minimum dan maksimum channel alpha
# min_alpha = np.min(alpha_channel)
# max_alpha = np.max(alpha_channel)

# print(f"Minimum alpha: {min_alpha}, Maksimum alpha: {max_alpha}")

# logo_path='Gambar\watermark logo.png'
# logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
# if logo is None:
#     print("Gambar logo tidak dapat dibaca. Pastikan format dan path benar.")
# else:
#     print("Bentuk logo:", logo.shape)

# import numpy as np

# # Mengambil channel alpha
# alpha_channel = logo[:, :, 2]

# # Cek nilai minimum dan maksimum channel alpha
# min_alpha = np.min(alpha_channel)
# max_alpha = np.max(alpha_channel)

# print(f"Minimum alpha: {min_alpha}, Maksimum alpha: {max_alpha}")


#file_paths = ['Gambar\SampleVideo_1280x720_1mb.mp4','Gambar\file_example_MP4_1920_18MG.mp4']
#file_paths = 'Gambar\SampleVideo_1280x720_1mb.mp4'
#file_paths = 'Gambar\file_example_MP4_1920_18MG.mp4'

# results = watermark_video(file_paths,
#                     text='Sample Watermark',font_type='hershey script simplex',
#                     font_color='red',position_str='bawah kanan',opacity=0.3,output_format='mp4',
#                     enchance_quality=True,
#                     logo_path='')
#                     #logo_path='Gambar\watermark logo.png')

# print(results)

#file_paths = 'Gambar\SampleVideo_1280x720_1mb.mp4'
#file_paths = 'Gambar\file_example_MP4_1920_18MG.mp4'

# results = watermark_image(file_paths,
#                           logo_path='Gambar\Watermark File.png',
#                           #logo_path='Gambar\\watermark logo.png',
#                             text='',
#                             font_type='',
#                             font_color='',
#                             position_str='bawah kanan',
#                             opacity=0.30,
#                             output_format='mp4',
#                             enchance_quality=True)
#                             #logo_path=None)

# print(results)

# def select_files():
#     Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
#     file_paths = askopenfilenames(title="Pilih File", filetypes=[("Image files", "*.jpg *.jpeg *.png *.mp4 *.avi *.mov *.pdf")])
#     return file_paths

# Memilih file secara langsung dengan tkinter
# file_paths = select_files()

# # Pastikan ada file yang dipilih
# if not file_paths:
#     print("Tidak ada file yang dipilih.")
# else:
#     # Ubah ini sesuai kebutuhan, bisa 'text' atau 'logo'
#     #watermark_type = input("Tipe Watermark: ")
#     # Memproses file berdasarkan ekstensi
#     for file_path in file_paths:
#         ext = file_path.split('.')[-1].lower()
        
#         if ext in ['jpg', 'jpeg', 'png', 'pdf']:
#             #watermark_image(file_path, watermark_type)
#             watermark_image([file_path],output_path='Watermarked Content',
#                     text='Sample Watermark',font_type='hershey script simplex',
#                     font_color='red',position_str='bawah kanan',opacity=0.3,output_format='png',
#                     enchance_quality=True,
#                     logo_path=None)
#                     #logo_path='Gambar\watermark logo.png')


#         elif ext in ['mp4', 'avi', 'mov']:
#             watermark_video([file_path],output_path='Watermarked Content',
#                     text='Sample Watermark',font_type='hershey script simplex',
#                     font_color='red',position_str='bawah kanan',opacity=0.3,output_format='mp4',
#                     enchance_quality=True,
#                     logo_path='')
#                     #logo_path='Gambar\watermark logo.png')
