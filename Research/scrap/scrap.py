from pytube import Playlist, YouTube
import csv
import os


def download_playlist_audio(playlist_url, download_path='raw_music_pop', csv_file_path='download_log_pop.csv'):
    # Ensure the download directory exists
    os.makedirs(download_path, exist_ok=True)

    # Initialize the CSV file and write the headers
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Index', 'Performer', 'Name of the Song'])

    playlist = Playlist(playlist_url)
    print(f'Downloading playlist: {playlist.title}')

    for index, video_url in enumerate(playlist.video_urls, start=1):
        try:
            video = YouTube(video_url)
            audio_stream = video.streams.get_audio_only()
            audio_file_path = audio_stream.download(output_path=download_path)
            mp3_filename = audio_file_path.replace('.mp4', '.mp3')

            # Log the download
            with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([index, video.author, video.title])

            print(f'Downloaded: {mp3_filename}')
        except Exception as e:
            print(f'Error downloading {video_url}: {e}')


# Replace 'YOUR_PLAYLIST_URL_HERE' with the actual playlist URL
# playlist_url = 'https://www.youtube.com/watch?v=WTsmIbNku5g&list=PLOzDu-MXXLliO9fBNZOQTBDddoA3FzZUo'
playlist_url = "https://www.youtube.com/watch?v=XXYlFuWEuKI&list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj"
download_playlist_audio(playlist_url)
