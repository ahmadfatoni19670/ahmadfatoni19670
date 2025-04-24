import os
import sys
import yt_dlp
import time  # Import modul time

class Video:
    def __init__(self, video_url):
        self.video_url = video_url

    def get_video_info(self):
        try:
            yt_dlp.utils.std_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/58.0.3029.110 Safari/537.3'
            yt_dlp.utils.std_headers['Referer'] = 'https://www.tiktok.com/'
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(self.video_url, download=False)
                return info['uploader'], info['upload_date'], info['id'], info['ext']
        except Exception as e:
            return False, False, False, False

    def download(self):
        try:
            ydl_opts = {
                'outtmpl': "%(uploader)s/%(upload_date)s - %(id)s.%(ext)s",
                'format': '(bv*+ba/b)[vcodec^=h264] / (bv*+ba/b)',
                'ratelimit': 1 * 10240 * 10240  # Batasi kecepatan unduh menjadi 1MB/s
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
            return True
        except Exception as e:
            print(f'Could not download: {self.video_url.strip()} - {e}')
            return False

    def get_user_name(self):
        pointer = self.video_url.find("@") + 1
        aux = pointer
        while self.video_url[aux] != "/":
            aux += 1
        return self.video_url[pointer:aux]

    def get_video_id(self):
        pointer = self.video_url.find("video") + 6
        return self.video_url[pointer:]

class FileDownloader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_video_links(self):
        with open(self.file_path, 'r') as file:
            return file.readlines()

    def normalize_link(self, link):
        return link.split('?')[0]

    def create_user_folder(self, download_path):
        os.makedirs(download_path, exist_ok=True)

    def create_ids_file(self, ids_path):
        open(ids_path, "a").close()

    def create_error_file(self):
        open("error.txt", "a").close()

    def check_video_existence(self, video_id, user_name):
        ids_file = f'{user_name}/_ids'
        return os.path.exists(ids_file) and video_id in open(ids_file).read()

    def write_video_id(self, video_id, user_name):
        ids_file = f'{user_name}/_ids'
        with open(ids_file, 'a') as file:
            file.write(f'{video_id}\n')

    def write_error(self, video_link):
        with open('error.txt', 'a') as file:
            file.write(f'{video_link}\n')

    def download_file(self):
        video_links = self.read_video_links()
        for link in video_links:
            if 'https://www.tiktok.com/@' in link and '/video/' in link:
                link = self.normalize_link(link)
                video = Video(link)
                user_name = video.get_user_name()
                video_id = video.get_video_id()
                download_path = f"./{user_name}"
                ids_path = f"{download_path}/_ids"
                self.create_user_folder(download_path)
                self.create_ids_file(ids_path)
                self.create_error_file()
                if not self.check_video_existence(video_id, user_name):
                    if video.download():
                        self.write_video_id(video_id, user_name)
                        time.sleep(10)  # Menambahkan delay 3 detik setelah unduhan berhasil
                    else:
                        self.write_error(link)

def download_folder():
    origin_path = 'links'
    if os.path.isdir(origin_path):
        files = os.listdir(origin_path)
        for file in files:
            path_to_file = os.path.join(origin_path, file)
            downloader = FileDownloader(path_to_file)
            downloader.download_file()

def main():
    links_folder = 'links'
    links_file = os.path.join(links_folder, 'links.txt')

    if not os.path.exists(links_folder):
        os.makedirs(links_folder)
        with open(links_file, 'w') as f:
            f.write("# Add your TikTok video links here\n")
        print(f"Folder '{links_folder}' dan file 'links.txt' dibuat. Tambahkan link video TikTok Anda ke 'links.txt' dan jalankan skrip lagi.")
        return

    if not os.path.exists(links_file):
        with open(links_file, 'w') as f:
            f.write("# Add your TikTok video links here\n")
        print(f"File 'links.txt' dibuat di '{links_folder}'. Tambahkan link video TikTok Anda ke 'links.txt' dan jalankan skrip lagi.")
        return

    if len(sys.argv) == 1:
        download_folder()
    else:
        for arg in sys.argv:
            if arg == "-file":
                downloader = FileDownloader(links_file)
                downloader.download_file()
            elif arg == "-folder":
                download_folder()
            elif arg == "-user":
                print("Opsi user dipilih, tetapi tidak ada tindakan yang didefinisikan.")

if __name__ == "__main__":
    main()
