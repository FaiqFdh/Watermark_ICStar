from image_watermark_choice import process_multiple_files as process_images
from video_watermark_choice import add_watermark_to_multiple_videos as process_videos
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

class WatermarkHandler:
    def __init__(self):
        self.supported_image_types = ['jpg', 'jpeg', 'png', 'pdf']
        self.supported_video_types = ['mp4', 'avi', 'mov']

    def get_file_extension(self, file_path):
        return file_path.split('.')[-1].lower()

    def process_files(self, file_paths, watermark_type, output_path, **kwargs):
        """Memproses file gambar atau video berdasarkan input user."""
        if not file_paths:
            raise ValueError("Tidak ada file yang dipilih untuk diproses.")

        # Cek apakah file pertama adalah gambar atau video
        file_ext = self.get_file_extension(file_paths[0])
        
        if file_ext in self.supported_image_types:
            # Jika gambar, panggil fungsi image watermarking
            return self.process_image_files(file_paths, watermark_type, output_path, **kwargs)
        elif file_ext in self.supported_video_types:
            # Jika video, panggil fungsi video watermarking
            return self.process_video_files(file_paths, watermark_type, output_path, **kwargs)
        else:
            raise ValueError(f"Tipe file '{file_ext}' tidak didukung.")

    def process_image_files(self, file_paths, watermark_type, output_path, **kwargs):
        """Memproses file gambar dengan menambahkan watermark."""
        if watermark_type == 'text':
            return process_images(file_paths=file_paths, output_path=output_path, watermark_type='text', **kwargs)
        elif watermark_type == 'logo':
            return process_images(file_paths=file_paths, output_path=output_path, watermark_type='logo', **kwargs)

    def process_video_files(self, video_paths, watermark_type, output_path, **kwargs):
        """Memproses file video dengan menambahkan watermark."""
        if watermark_type == 'text':
            return process_videos(video_paths=video_paths, watermark_type='text', output_path=output_path, **kwargs)
        elif watermark_type == 'logo':
            return process_videos(video_paths=video_paths, watermark_type='logo', output_path=output_path, **kwargs)


# Fungsi utama yang akan dipanggil dari UiPath
def run_watermark_handler(file_paths, watermark_type, output_path,enchance_quality=None,font_type=None, opacity=None, position_str=None,text=None, logo_path=None,font_color=None,output_format=None,thickness=None):
    handler = WatermarkHandler()
    result = handler.process_files(
        file_paths=file_paths, 
        watermark_type=watermark_type, 
        output_path=output_path, 
        enchance_quality = enchance_quality,
        opacity=opacity,
        font_type=font_type,
        text=text, 
        logo_path=logo_path,
        font_color=font_color,
        position_str=position_str,
        output_format=output_format,
        thickness=thickness
    )
    return result

# Fungsi untuk memilih file menggunakan tkinter
def select_files():
    Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
    file_paths = askopenfilenames(title="Pilih File", filetypes=[("Image files", "*.jpg *.jpeg *.png *.mp4 *.avi *.mov *.pdf")])
    return file_paths

# Memilih file secara langsung dengan tkinter
file_paths = select_files()

#file_paths = ['Gambar\fsdsd.png']

# Fungsi Untuk Gambar
#file_paths = ['Gambar\\shopping after.jpg','Gambar\\komputer mainframe1.jpg']
#Untuk Gambar dengan Watermark Text
# result = run_watermark_handler(file_paths=file_paths,
#                                watermark_type='text',
#                                output_path='Watermarked Content',
#                                enchance_quality=False,
#                                text='Sample Watermark',
#                                position_str='bawah kanan',
#                                font_type='hershey script simplex',
#                                font_color="#49FFCE",
#                                opacity=0.3,
#                                output_format='png'
#                                )
# print(result)
#print(type(result))

# Untuk Gambar dengan Watermark Logo
# result = run_watermark_handler(file_paths=file_paths,
#                                watermark_type='logo',
#                                output_path='Watermarked Content',
#                                logo_path='Gambar\\watermark logo.png',
#                                position_str='auto',
#                                opacity=0.5,
#                                output_format='png'
#                                )

# print(result)

# Untuk Video dengan Watermark Logo
# result = run_watermark_handler(file_paths=file_paths,
#                                 watermark_type='logo',
#                                 output_path="Watermarked Content",
#                                 logo_path='Gambar\\watermark logo.png',
#                                 position_str='atas kanan',
#                                 opacity=0.5,
#                                 output_format='mp4'
#                                )

# print(result)

# Untuk Video dengan Watermark Text
result = run_watermark_handler(file_paths=file_paths,
                                watermark_type='text',
                                output_path="Watermarked Content",
                                text='Hak Cipta 2024',
                                enchance_quality=False,
                                position_str='bawah kanan',
                                #font_color="#49FFCE",  # Nama warna
                                font_color="red",  # Nama warna
                                font_type='hershey script simplex',
                                opacity=0.5,
                                output_format='mp4',
                                #thickness=2
                               )

print(result)