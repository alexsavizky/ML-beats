import os
import time
import yt_dlp
from tqdm import tqdm

def download_video(url, download_path, index):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ignoreerrors': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f'Downloaded video {index}')
    except Exception as e:
        print(f"Error downloading video {index}: {e}")

def download_playlist_in_chunks(playlist_url, download_path='downloads2', chunk_size=500):
    ydl_opts = {
        'extract_flat': True,
        'ignoreerrors': True,
    }
    os.makedirs(download_path, exist_ok=True)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        video_urls = [entry['url'] for entry in playlist_info['entries']]

    total_videos = len(video_urls)
    print(f'Total videos in playlist: {total_videos}')

    for i in range(0, total_videos, chunk_size):
        for j in tqdm(range(i, min(i + chunk_size, total_videos))):
            download_video(video_urls[j], download_path, j + 1)
        print(f"Finished downloading videos {i + 1} to {min(i + chunk_size, total_videos)}")
        if i + chunk_size < total_videos:
            print("Taking a 15-minute break...")
            time.sleep(900)  # Pause for 15 minutes between chunks

# Replace with your actual playlist URL
playlist_url = "https://youtube.com/playlist?list=PLHUfq0EyQKo50y57fa_wkxCse2OSOuno_&si=vUbuRJpoi-Am4aEK"
download_playlist_in_chunks(playlist_url)
