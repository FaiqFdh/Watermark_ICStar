from image_watermark_choice import process_multiple_files as process_images
from video_watermark_choice import add_watermark_to_multiple_videos as process_videos

class WatermarkHandler:
    def __init__(self):
        self.supported_image_types = ['jpg', 'jpeg', 'png', 'pdf']
        self.supported_video_types = ['mp4', 'avi', 'mov']

    def get_file_extension(self, file_path):
        if isinstance(file_path, list):
            # Mengambil ekstensi dari file pertama dalam list
            return file_path[0].split('.')[-1].lower()  
        return file_path.split('.')[-1].lower()  # Untuk input string

    def process_files(self, file_path, watermark_type, **kwargs):
        """Memproses file gambar atau video berdasarkan input user."""
        if not file_path:
            raise ValueError("Tidak ada file yang dipilih untuk diproses.")

        # Memeriksa jika file_path adalah list, dan jika ya, ambil file pertama
        if isinstance(file_path, list):
            file_path = file_path[0]

        # Cek apakah file pertama adalah gambar atau video
        file_ext = self.get_file_extension(file_path)
        
        if file_ext in self.supported_image_types:
            return self.process_image_files(file_path, watermark_type, **kwargs)
        elif file_ext in self.supported_video_types:
            return self.process_video_files(file_path, watermark_type, **kwargs)
        else:
            raise ValueError(f"Tipe file '{file_ext}' tidak didukung.")

    def process_image_files(self, file_path, watermark_type, **kwargs):
        """Memproses file gambar dengan menambahkan watermark."""
        if watermark_type == 'text':
            return process_images(file_paths=file_path, watermark_type='text', **kwargs)
        elif watermark_type == 'logo':
            return process_images(file_paths=file_path, watermark_type='logo', **kwargs)

    def process_video_files(self, video_path, watermark_type, **kwargs):
        """Memproses file video dengan menambahkan watermark."""
        if watermark_type == 'text':
            return process_videos(video_path=video_path, watermark_type='text', **kwargs)
        elif watermark_type == 'logo':
            return process_videos(video_path=video_path, watermark_type='logo', **kwargs)

def run_watermark_handler(file_paths, watermark_type, enchance_quality=None, font_type=None, opacity=None, position_str=None, text=None, logo_path=None, font_color=None, output_format=None, thickness=None):
    handler = WatermarkHandler()
    result = handler.process_files(
        file_path=file_paths,  # Sekarang menerima string
        watermark_type=watermark_type, 
        enchance_quality=enchance_quality,
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