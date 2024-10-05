from watermark_handler import run_watermark_handler
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# Fungsi untuk memilih file menggunakan tkinter
def select_files():
    Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
    file_paths = askopenfilenames(title="Pilih File", filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("Video files", "*.mp4 *.avi *.mov"), ("PDF files", "*.pdf")])
    return file_paths

def watermark_image(file_path, 
                    logo_path=None,
                    text=None, 
                    font_type=None, 
                    font_color=None, 
                    position_str=None, 
                    opacity=None, 
                    output_format=None,
                    enchance_quality=None, 
                    output_path=None,
                    watermark_type=None):
    """Menambahkan watermark ke gambar berdasarkan tipe yang dipilih."""
    
    if not logo_path:  # Jika logo_path kosong atau None
        # Untuk watermark teks
        result = run_watermark_handler(
            file_paths=file_path,
            output_path=output_path,
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
            output_path=output_path,
            logo_path=logo_path,
            position_str=position_str,
            opacity=opacity,
            output_format=output_format,
            enchance_quality=enchance_quality,
            watermark_type='logo'
        )
        #print('watermark logo', result)
        return result

def watermark_video(file_path, 
                    logo_path=None,
                    text=None,
                    font_type=None, 
                    font_color=None,
                    position_str=None, 
                    opacity=None, 
                    output_format=None,
                    enchance_quality=None, 
                    output_path=None, 
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
            output_path=output_path,
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
            output_path=output_path,
            watermark_type='logo'
        )
        #print('watermark logo', result)
        return result

file_paths = ['Gambar\komputer mainframe1.jpg','Gambar\shopping after.jpg']
#file_paths = ['Gambar\komputer mainframe1.jpg']

results = watermark_image(file_paths,output_path='Watermarked Content',
                    text='Sample Watermark',font_type='hershey script simplex',
                    font_color='red',position_str='bawah kanan',opacity=0.3,output_format='png',
                    enchance_quality=True,
                    #logo_path=None)
                    logo_path='Gambar\watermark logo.png')

print(results)

file_paths = ['Gambar\SampleVideo_1280x720_1mb.mp4','Gambar\file_example_MP4_1920_18MG.mp4']
#file_paths = ['Gambar\komputer mainframe1.jpg']

results = watermark_video(file_paths,output_path='Watermarked Content',
                    text='Sample Watermark',font_type='hershey script simplex',
                    font_color='red',position_str='bawah kanan',opacity=0.3,output_format='mp4',
                    enchance_quality=True,
                    logo_path='')
                    #logo_path='Gambar\watermark logo.png')

print(results)

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
