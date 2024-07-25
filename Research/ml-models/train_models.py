import u_net as un
import wave_net as wn
import cycle_gan as cg
import pickle_handler as ph
import numpy as np
from preprocess import AudioDataGenerator
from sklearn.model_selection import train_test_split

# config
vocal_folder = 'files/raw_pop_small_10_spleet_mp3'
lofi_folder = 'files/raw_lofi_small_10'
batch_size = 32
seq_length = 128
sr = 44100
n_mels = 128
segment_length = 5
test_size = 0.2
random_state = 42
run = 2

# preprocess
adg = AudioDataGenerator(vocal_folder, lofi_folder, batch_size, seq_length, sr, n_mels, segment_length)
X, y = adg[0], adg[1]

# split the data into training and testing sets
X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size, random_state)

# train U-Net model
input_shape = X_train.shape[1:]
unet = un.unet_model(input_shape)
unet.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
history_unet = unet.fit(X_train, Y_train, epochs=50, batch_size=32, validation_data=(X_test, Y_test))

# save u-net model and training history
ph.save_model(unet, f'results/unet_model{run}.pkl')
ph.save_model_info(history_unet.history, f'results/unet_info{run}.pkl')
ph.save_model_info_csv(history_unet.history, f'results/unet_info{run}.csv')

# train waveNet model
input_shape = X_train.shape[1:]
wavenet = wn.wavenet_model(input_shape)
wavenet.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
history_wavenet = wavenet.fit(X_train, Y_train, epochs=50, batch_size=32, validation_data=(X_test, Y_test))

# save waveNet model and training history
ph.save_model(wavenet, f'results/wavenet_model{run}.pkl')
ph.save_model_info(history_wavenet.history, f'results/wavenet_info{run}.pkl')
ph.save_model_info_csv(history_wavenet.history, f'results/wavenet_info{run}.csv')

# train cycleGAN model (simplified training loop, should be expanded for actual use)
G_pop_to_lofi = cg.build_generator()
G_lofi_to_pop = cg.build_generator()
D_pop = cg.build_discriminator()
D_lofi = cg.build_discriminator()

# Compile the CycleGAN components (losses and optimizers need to be set up here)
# For simplicity, using placeholder code to indicate training
# Add actual CycleGAN training loop here

# Save cycleGAN models
ph.save_model(G_pop_to_lofi, f'results/cyclegan_G_pop_to_lofi{run}.pkl')
ph.save_model(G_lofi_to_pop, f'results/cyclegan_G_lofi_to_pop{run}.pkl')
ph.save_model(D_pop, f'results/cyclegan_D_pop{run}.pkl')
ph.save_model(D_lofi, f'results/cyclegan_D_lofi{run}.pkl')

# Save CycleGAN training history/info if available
# save_model_info(cyclegan_history, 'cyclegan_info.pkl')
# save_model_info_csv(cyclegan_history, 'cyclegan_info.csv')
