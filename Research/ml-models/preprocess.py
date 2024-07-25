import os
import numpy as np
import librosa
import soundfile as sf
import tensorflow as tf
from tensorflow.keras.utils import Sequence
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, TimeDistributed, RepeatVector, Attention


class AudioDataGenerator(Sequence):
    def __init__(self, vocal_folder, lofi_folder, batch_size=32, seq_length=128, sr=44100, n_mels=128,
                 segment_length=5):
        self.vocal_folder = vocal_folder
        self.lofi_folder = lofi_folder
        self.batch_size = batch_size
        self.seq_length = seq_length
        self.sr = sr
        self.n_mels = n_mels
        self.segment_length = segment_length
        self.vocal_files = [f for f in os.listdir(vocal_folder) if f.endswith('.mp3') or f.endswith('.wav')]
        self.lofi_files = [f for f in os.listdir(lofi_folder) if f.endswith('.mp3') or f.endswith('.wav')]

    def __len__(self):
        return len(self.vocal_files) // self.batch_size

    def __getitem__(self, idx):
        batch_vocal_files = self.vocal_files[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_lofi_files = self.lofi_files[idx * self.batch_size:(idx + 1) * self.batch_size]

        X, y = [], []
        for vocal_file, lofi_file in zip(batch_vocal_files, batch_lofi_files):
            vocal_path = os.path.join(self.vocal_folder, vocal_file)
            lofi_path = os.path.join(self.lofi_folder, lofi_file)
            vocal_segments = self.preprocess_audio(vocal_path)
            lofi_segments = self.preprocess_audio(lofi_path)
            for vocal_segment, lofi_segment in zip(vocal_segments, lofi_segments):
                if vocal_segment.shape[1] > self.seq_length and lofi_segment.shape[1] > self.seq_length:
                    for i in range(min(vocal_segment.shape[1], lofi_segment.shape[1]) - self.seq_length):
                        X.append(vocal_segment[:, i:i + self.seq_length])
                        y.append(lofi_segment[:, i:i + self.seq_length])

        X = np.array(X)
        y = np.array(y)

        if len(X) == 0 or len(y) == 0:
            raise ValueError("Generated batch is empty. Check data preprocessing steps.")

        return X, y

    def preprocess_audio(self, file_path):
        y, sr = librosa.load(file_path, sr=self.sr)
        segments = self.segment_audio(y)
        mel_specs = [self.extract_mel_spectrogram(segment) for segment in segments if not self.is_silent(segment)]
        return mel_specs

    def segment_audio(self, y):
        segment_samples = self.segment_length * self.sr
        segments = []
        for start in range(0, len(y), segment_samples):
            end = min(start + segment_samples, len(y))
            segments.append(y[start:end])
        return segments

    def extract_mel_spectrogram(self, y):
        mel_spec = librosa.feature.melspectrogram(y=y, sr=self.sr, n_mels=self.n_mels)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        return mel_spec_db

    def is_silent(self, y, threshold=0.01):
        return np.max(np.abs(y)) < threshold

# # Build the sequence-to-sequence model
# def build_seq2seq_model(input_shape, output_length):
#     encoder_inputs = Input(shape=input_shape)
#     encoder = LSTM(256, return_state=True)
#     encoder_outputs, state_h, state_c = encoder(encoder_inputs)
#     encoder_states = [state_h, state_c]
#
#     decoder_inputs = RepeatVector(output_length)(encoder_outputs)
#     decoder_lstm = LSTM(256, return_sequences=True, return_state=False)
#     decoder_outputs = decoder_lstm(decoder_inputs, initial_state=encoder_states)
#
#     attention = Attention()([decoder_outputs, encoder_outputs])
#     attention = TimeDistributed(Dense(128, activation="relu"))(attention)
#
#     outputs = TimeDistributed(Dense(input_shape[1]))(attention)
#
#     model = Model([encoder_inputs, decoder_inputs], outputs)
#     model.compile(optimizer='adam', loss='mse')
#     return model
#
#
# # Generate lofi music from vocals
# def generate_lofi_music(model, seed, seq_length=128, generate_length=500):
#     generated = seed
#     for _ in range(generate_length // seq_length):
#         input_seq = generated[:, -seq_length:]  # Get the last seq_length frames
#         pred = model.predict([np.expand_dims(input_seq, axis=0), np.expand_dims(input_seq, axis=0)])
#         generated = np.hstack((generated, pred[0]))  # Append the prediction to the sequence
#     return generated
#
#
# # Convert Mel spectrogram to audio
# def mel_to_audio(mel_spec, sr=44100):
#     mel_spec_db = librosa.db_to_power(mel_spec)  # Convert back to power
#     y = librosa.feature.inverse.mel_to_audio(mel_spec_db, sr=sr)
#     return y
#
#
# # Save the generated audio
# def save_audio(waveform, sr=44100, file_path='generated_audio.wav'):
#     sf.write(file_path, waveform, sr)

#
# # Example usage
# vocal_folder_path = 'files/raw_pop_small_10_spleet_mp3'  # Change this to your vocal tracks folder path
# lofi_folder_path = 'files/raw_lofi_small_10'  # Change this to your lofi songs folder path
#
# batch_size = 32
# seq_length = 128
#
# data_gen = AudioDataGenerator(vocal_folder_path, lofi_folder_path, batch_size=batch_size, seq_length=seq_length)
#
# # Check the shape of the data
# X, y = data_gen[0]
# print(X[0].shape, y.shape)  # Ensure X and y shapes are consistent
#
# input_shape = (seq_length, X[0].shape[2])
# output_length = seq_length
# model = build_seq2seq_model(input_shape, output_length)
# model.fit(data_gen, epochs=50, steps_per_epoch=len(data_gen))
#
# # Generate Mel spectrogram
# seed = X[0][0]  # Use the first sequence in X as the seed
# generated_mel_spec = generate_lofi_music(model, seed, seq_length=seq_length, generate_length=500)
#
# # Convert Mel spectrogram to audio
# generated_waveform = mel_to_audio(generated_mel_spec, sr=44100)
#
# # Save the audio
# save_audio(generated_waveform, sr=44100, file_path='generated_lofi_song.wav')
