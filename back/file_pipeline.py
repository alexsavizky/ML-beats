# import os
# from spleeter.separator import Separator
#
# class File_pipeline:
#     def __init__(self,file):
#         self.file = file
#
#     def vocal_split(spleet_dir, song_path):
#         # 2stems separates into vocals and accompaniment
#         separator = Separator('spleeter:2stems')
#
#         if os.path.isfile(song_path):
#             # Separate vocals and save to the 'spleet' directory
#             try:
#                 separator.separate_to_file(song_path, os.path.join(spleet_dir), filename_format='{instrument}.{codec}')
#                 vocal_file_path = os.path.join(spleet_dir, 'vocals.wav')
#                 if os.path.exists(vocal_file_path):
#                     os.rename(vocal_file_path, os.path.join(spleet_dir, os.path.basename(song_path)))
#             except KeyboardInterrupt:
#                 print("Execution interrupted by the user.")
#             except Exception as e:
#                 print(f"An error occurred: {e}")