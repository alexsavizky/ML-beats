import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
import librosa
import soundfile as sf
import itertools
from tqdm import tqdm

# Enable XLA
tf.config.optimizer.set_jit(True)

# Constants
SAMPLE_RATE = 22050  # Common sample rate for audio
DURATION = 60  # Duration in seconds for the output
N_MELS = 128  # Number of Mel bands to generate
HOP_LENGTH = 512  # Number of samples between successive frames


# Function to load saved spectrograms from files
def load_spectrograms(directory):
    print(f"Loading spectrograms from '{directory}'...")
    files = [f for f in os.listdir(directory) if f.endswith('.npy')]
    spectrograms = [np.load(os.path.join(directory, f)) for f in files]
    print(f"Loaded {len(spectrograms)} spectrograms from '{directory}'")
    return spectrograms


# Step 2: Define the Generator and Discriminator models
def build_generator(input_shape=(N_MELS, None, 1)):  # None for time dimension to allow varying lengths
    print("Building Generator model...")
    inputs = layers.Input(shape=input_shape)

    # Downsampling
    x = layers.Conv2D(64, (4, 4), strides=2, padding='same')(inputs)
    x = layers.LeakyReLU(alpha=0.2)(x)
    x = layers.Conv2D(128, (4, 4), strides=2, padding='same')(x)
    x = layers.LeakyReLU(alpha=0.2)(x)

    # Bottleneck
    x = layers.Conv2D(256, (4, 4), strides=2, padding='same')(x)
    x = layers.LeakyReLU(alpha=0.2)(x)

    # Upsampling
    x = layers.Conv2DTranspose(128, (4, 4), strides=2, padding='same')(x)
    x = layers.ReLU()(x)
    x = layers.Conv2DTranspose(64, (4, 4), strides=2, padding='same')(x)
    x = layers.ReLU()(x)

    outputs = layers.Conv2DTranspose(1, (4, 4), strides=2, padding='same', activation='tanh')(x)

    model = tf.keras.models.Model(inputs, outputs)
    print("Generator model built successfully.")
    return model


def build_discriminator(input_shape=(N_MELS, None, 1)):
    print("Building Discriminator model...")
    inputs = layers.Input(shape=input_shape)

    x = layers.Conv2D(64, (4, 4), strides=2, padding='same')(inputs)
    x = layers.LeakyReLU(alpha=0.2)(x)
    x = layers.Conv2D(128, (4, 4), strides=2, padding='same')(x)
    x = layers.LeakyReLU(alpha=0.2)(x)
    x = layers.Conv2D(256, (4, 4), strides=2, padding='same')(x)
    x = layers.LeakyReLU(alpha=0.2)(x)
    x = layers.Conv2D(512, (4, 4), strides=2, padding='same')(x)
    x = layers.LeakyReLU(alpha=0.2)(x)

    # Add a Global Average Pooling layer to flatten the feature maps
    x = layers.GlobalAveragePooling2D()(x)

    # Add a Dense layer for classification
    outputs = layers.Dense(1, activation='sigmoid')(x)

    model = tf.keras.models.Model(inputs, outputs)
    print("Discriminator model built successfully.")
    return model


# Step 3: Compile the Models
def compile_models(generator_g, generator_f, discriminator_x, discriminator_y):
    print("Compiling models...")
    # Optimizers
    generator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
    discriminator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)

    # Compile the models
    generator_g.compile(loss='mse', optimizer=generator_optimizer)
    generator_f.compile(loss='mse', optimizer=generator_optimizer)
    discriminator_x.compile(loss='binary_crossentropy', optimizer=discriminator_optimizer)
    discriminator_y.compile(loss='binary_crossentropy', optimizer=discriminator_optimizer)

    print("Models compiled successfully.")


# Step 4: Training the CycleGAN Model
def train_cycle_gan(generator_g, generator_f, discriminator_x, discriminator_y,
                    regular_spectrograms, lofi_spectrograms, epochs=6, batch_size=1):
    print(f"Starting training for {epochs} epochs...")

    # Re-instantiate the optimizers
    generator_optimizer_g = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
    generator_optimizer_f = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
    discriminator_optimizer_x = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
    discriminator_optimizer_y = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)

    dataset_size = len(regular_spectrograms)
    lofi_cycle = itertools.cycle(lofi_spectrograms)  # Create an iterator that cycles through lofi_spectrograms

    for epoch in range(epochs):
        print(f"\nEpoch {epoch + 1}/{epochs}")

        # Shuffle the dataset at the beginning of each epoch
        indices = np.arange(dataset_size)
        np.random.shuffle(indices)

        for i in tqdm(range(0, dataset_size, batch_size)):
            batch_indices = indices[i:i + batch_size]

            # Create batches of regular and lofi spectrograms
            regular_batch = np.array([regular_spectrograms[j] for j in batch_indices])
            lofi_batch = np.array([next(lofi_cycle) for _ in batch_indices])  # Cycle through lofi spectrograms

            # Reshape input data to (batch_size, N_MELS, time, 1)
            regular_batch = np.expand_dims(regular_batch, axis=-1)  # Shape becomes (batch_size, N_MELS, time, 1)
            lofi_batch = np.expand_dims(lofi_batch, axis=-1)  # Shape becomes (batch_size, N_MELS, time, 1)

            # Train the discriminator_x (lofi vs. fake lofi)
            with tf.GradientTape() as tape:
                fake_lofi = generator_g(regular_batch, training=True)
                d_x_real = discriminator_x(lofi_batch, training=True)
                d_x_fake = discriminator_x(fake_lofi, training=True)
                d_x_loss_real = tf.keras.losses.binary_crossentropy(tf.ones_like(d_x_real), d_x_real)
                d_x_loss_fake = tf.keras.losses.binary_crossentropy(tf.zeros_like(d_x_fake), d_x_fake)
                d_x_loss = d_x_loss_real + d_x_loss_fake
            grads = tape.gradient(d_x_loss, discriminator_x.trainable_variables)
            discriminator_optimizer_x.apply_gradients(zip(grads, discriminator_x.trainable_variables))

            # Train the discriminator_y (regular vs. fake regular)
            with tf.GradientTape() as tape:
                fake_regular = generator_f(lofi_batch, training=True)
                d_y_real = discriminator_y(regular_batch, training=True)
                d_y_fake = discriminator_y(fake_regular, training=True)
                d_y_loss_real = tf.keras.losses.binary_crossentropy(tf.ones_like(d_y_real), d_y_real)
                d_y_loss_fake = tf.keras.losses.binary_crossentropy(tf.zeros_like(d_y_fake), d_y_fake)
                d_y_loss = d_y_loss_real + d_y_loss_fake
            grads = tape.gradient(d_y_loss, discriminator_y.trainable_variables)
            discriminator_optimizer_y.apply_gradients(zip(grads, discriminator_y.trainable_variables))

            # Train the generator_g (regular -> fake lofi -> reconstructed regular)
            with tf.GradientTape() as tape:
                fake_lofi = generator_g(regular_batch, training=True)
                reconstructed_regular = generator_f(fake_lofi, training=True)

                # Resize reconstructed_regular if necessary to match regular_batch
                if regular_batch.shape != reconstructed_regular.shape:
                    reconstructed_regular = tf.image.resize(reconstructed_regular, size=regular_batch.shape[1:3])

                g_g_loss = tf.keras.losses.binary_crossentropy(tf.ones_like(discriminator_x(fake_lofi)),
                                                               discriminator_x(fake_lofi))
                cycle_loss = tf.reduce_mean(tf.abs(regular_batch - reconstructed_regular))
                total_g_g_loss = g_g_loss + 10 * cycle_loss
            grads = tape.gradient(total_g_g_loss, generator_g.trainable_variables)
            generator_optimizer_g.apply_gradients(zip(grads, generator_g.trainable_variables))

            # Train the generator_f (lofi -> fake regular -> reconstructed lofi)
            with tf.GradientTape() as tape:
                fake_regular = generator_f(lofi_batch, training=True)
                reconstructed_lofi = generator_g(fake_regular, training=True)

                # Resize reconstructed_lofi if necessary to match lofi_batch
                if lofi_batch.shape != reconstructed_lofi.shape:
                    reconstructed_lofi = tf.image.resize(reconstructed_lofi, size=lofi_batch.shape[1:3])

                g_f_loss = tf.keras.losses.binary_crossentropy(tf.ones_like(discriminator_y(fake_regular)),
                                                               discriminator_y(fake_regular))
                cycle_loss = tf.reduce_mean(tf.abs(lofi_batch - reconstructed_lofi))
                total_g_f_loss = g_f_loss + 10 * cycle_loss
            grads = tape.gradient(total_g_f_loss, generator_f.trainable_variables)
            generator_optimizer_f.apply_gradients(zip(grads, generator_f.trainable_variables))

            # Convert the loss values to scalars before printing
            d_x_loss_value = d_x_loss.numpy().mean()
            d_y_loss_value = d_y_loss.numpy().mean()
            total_g_g_loss_value = total_g_g_loss.numpy().mean()
            total_g_f_loss_value = total_g_f_loss.numpy().mean()

            # Print loss for this batch
            print(
                f"Batch {i + 1}/{dataset_size} | Discriminator X Loss: {d_x_loss_value:.4f} | Discriminator Y Loss: {d_y_loss_value:.4f} | Generator G Loss: {total_g_g_loss_value:.4f} | Generator F Loss: {total_g_f_loss_value:.4f}")


# Step 5: Convert the generated spectrogram back to MP3
def convert_spectrogram_to_mp3(spectrogram, output_file):
    print(f"Converting generated spectrogram to MP3: {output_file}")

    # Convert the spectrogram back to audio
    S_db = librosa.db_to_amplitude(spectrogram)
    y = librosa.feature.inverse.mel_to_audio(S_db, sr=SAMPLE_RATE, hop_length=HOP_LENGTH)

    # Write the audio data to a file
    sf.write(output_file, y, SAMPLE_RATE)

    print(f"MP3 saved as '{output_file}'")


# Main function to run the entire process
if __name__ == "__main__":
    # Paths to directories
    # regular_spectrogram_dir = 'C:/final_project/ML-beats/Research/regular_spectrograms'
    # lofi_spectrogram_dir = 'C:/final_project/ML-beats/Research/lofi_spectrograms'
    #
    # # Load spectrogram data
    # regular_spectrograms = load_spectrograms(regular_spectrogram_dir)
    # lofi_spectrograms = load_spectrograms(lofi_spectrogram_dir)
    #
    # # Calculate the required length of the spectrogram
    # num_time_steps = int((DURATION * SAMPLE_RATE) / HOP_LENGTH)
    #
    # # Pad or truncate spectrograms to have the desired time length
    # regular_spectrograms = [librosa.util.fix_length(s, size=num_time_steps, axis=1) for s in regular_spectrograms]
    # lofi_spectrograms = [librosa.util.fix_length(s, size=num_time_steps, axis=1) for s in lofi_spectrograms]

    # Step 2: Build the models
    generator_g = build_generator()
    generator_f = build_generator()
    discriminator_x = build_discriminator()
    discriminator_y = build_discriminator()

    # Step 3: Compile the models
    compile_models(generator_g, generator_f, discriminator_x, discriminator_y)

    from tensorflow.keras.utils import plot_model

    plot_model(generator_g, to_file='../temp-data/G_pop_to_lofi_model.png', show_shapes=True, show_layer_names=True)
    plot_model(generator_f, to_file='../temp-data/G_lofi_to_pop_model.png', show_shapes=True, show_layer_names=True)
    plot_model(discriminator_x, to_file='../temp-data/D_pop_model.png', show_shapes=True, show_layer_names=True)
    plot_model(discriminator_y, to_file='../temp-data/D_lofi_model.png', show_shapes=True, show_layer_names=True)

    # # Step 4: Train the model
    # train_cycle_gan(generator_g, generator_f, discriminator_x, discriminator_y,
    #                 regular_spectrograms, lofi_spectrograms, epochs=6, batch_size=1)
    #
    # # Step 5: Convert the generated spectrogram back to MP3
    # generator_g.save('generator_g_model.h5')
    # # Example with one spectrogram
    # example_spectrogram = regular_spectrograms[0]  # Replace with actual spectrogram
    # generated_spectrogram = generator_g(example_spectrogram[np.newaxis, :, :, np.newaxis])
    # convert_spectrogram_to_mp3(generated_spectrogram[0, :, :, 0], 'output_lofi.mp3')
