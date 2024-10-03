from tkinter import Tk
from tkinter.filedialog import askopenfilenames
from image_watermark_choice import process_multiple_files as process_images
from video_watermark_choice import add_watermark_to_multiple_videos as process_videos

class WatermarkHandler:
    def __init__(self):
        self.supported_image_types = ['jpg', 'jpeg', 'png']
        self.supported_video_types = ['mp4', 'avi', 'mov']

    def get_file_extension(self, file_path):
        return file_path.split('.')[-1].lower()

    def process_files(self, file_paths, watermark_type,output_path, **kwargs):
        """Memproses file gambar atau video berdasarkan input user."""
        if not file_paths:
            raise ValueError("Tidak ada file yang dipilih untuk diproses.")

        # Cek apakah file pertama adalah gambar atau video
        file_ext = self.get_file_extension(file_paths[0])
        
        if file_ext in self.supported_image_types:
            # Jika gambar, panggil fungsi image watermarking
            return self.process_image_files(file_paths, watermark_type,output_path, **kwargs)
        elif file_ext in self.supported_video_types:
            # Jika video, panggil fungsi video watermarking
            return self.process_video_files(file_paths, watermark_type, output_path,**kwargs)
        else:
            raise ValueError(f"Tipe file '{file_ext}' tidak didukung. Hanya {self.supported_image_types} untuk gambar dan {self.supported_video_types} untuk video.")

    def process_image_files(self, file_paths, watermark_type, output_path,**kwargs):
        """Memproses file gambar dengan menambahkan watermark."""
        if watermark_type == 'text':
            print("Memproses gambar dengan watermark teks...")
            return process_images(
                file_paths=file_paths,
                output_path=output_path,
                watermark_type='text',
                **kwargs
            )
        elif watermark_type == 'logo':
            print("Memproses gambar dengan watermark logo...")
            return process_images(
                file_paths=file_paths,
                output_path=output_path,
                watermark_type='logo',
                **kwargs
            )
        else:
            raise ValueError(f"Tipe watermark '{watermark_type}' tidak didukung untuk gambar.")

    def process_video_files(self, video_paths, watermark_type,output_path, **kwargs):
        """Memproses file video dengan menambahkan watermark."""
        if watermark_type == 'text':
            print("Memproses video dengan watermark teks...")
            return process_videos(
                video_paths=video_paths,
                watermark_type='text',
                output_path=output_path,
                **kwargs
            )
        elif watermark_type == 'logo':
            print("Memproses video dengan watermark logo...")
            return process_videos(
                video_paths=video_paths,
                watermark_type='logo',
                output_path=output_path,
                **kwargs
            )
        else:
            raise ValueError(f"Tipe watermark '{watermark_type}' tidak didukung untuk video.")

# Fungsi untuk memilih file menggunakan tkinter
def select_files():
    Tk().withdraw()  # Untuk menyembunyikan jendela Tkinter yang kosong
    file_paths = askopenfilenames(title="Pilih File", filetypes=[("Image files", "*.jpg *.jpeg *.png *.mp4 *.avi *.mov")])
    return file_paths

# Memilih file secara langsung dengan tkinter
file_paths = select_files()
watermark_handler = WatermarkHandler()

# Memeriksa jenis file dan memilih watermark yang sesuai

# Cek apakah file pertama adalah gambar atau video
file_ext = watermark_handler.get_file_extension(file_paths[0])

#File Path dalam bentuk list = ['File 1', 'File 2']
#Or APPEND with list ??

if file_ext in watermark_handler.supported_image_types:
    # Jika file adalah gambar dan user memilih watermark text
    output_images = None
    watermark_type = 'text'  # Misalnya user memilih watermark text
    if watermark_type == 'text':
        output_images = watermark_handler.process_files(
            file_paths=file_paths,
            watermark_type='text',
            output_path="Watermarked Content",
            text='Hak Cipta 2024',
            position_str=-2,  # Posisi watermark (misalnya kanan atas)
            opacity=0.3,
            font_color='#49FFCE',
            #thickness=1,
            output_format='png'
        )
    # Jika user memilih watermark logo
    elif watermark_type == 'logo':
        output_images = watermark_handler.process_files(
            file_paths=file_paths,
            watermark_type='logo',
            output_path="Watermarked Content",
            logo_path='Gambar\\watermark logo.png',  # Contoh path logo
            position_str=2,  # Posisi watermark (misalnya kanan atas)
            opacity=0.7,
            scale_factor=0.3,
            output_format='png'
        )
    print(output_images)

elif file_ext in watermark_handler.supported_video_types:
    # Jika file adalah video dan user memilih watermark text
    output_videos = None
    watermark_type = 'logo'  # Misalnya user memilih watermark text
    if watermark_type == 'text':
        output_videos = watermark_handler.process_files(
            file_paths=file_paths,
            watermark_type='text',
            output_path="Watermarked Content",
            text='Hak Cipta 2024',
            position_str=2,
            font_color="#49FFCE",
            opacity=0.7,
            output_format='mp4'
        )
    # Jika user memilih watermark logo
    elif watermark_type == 'logo':
        output_videos = watermark_handler.process_files(
            file_paths=file_paths,
            watermark_type='logo',
            output_path="Watermarked Content",
            logo_path='Gambar\\watermark logo.png',  # Contoh path logo
            position_str=8,  # Posisi watermark (misalnya kanan bawah)
            opacity=0.7,
            output_format='mp4'
        )
    print(output_videos)
