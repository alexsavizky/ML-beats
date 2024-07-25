import tensorflow as tf
from tensorflow.keras import layers, Model


def build_generator():
    inputs = tf.keras.Input(shape=(128, 128, 1))

    x = layers.Conv2D(64, (7, 7), padding='same')(inputs)
    x = layers.LeakyReLU()(x)

    for _ in range(3):
        x = layers.Conv2D(128, (3, 3), padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.LeakyReLU()(x)

    x = layers.Conv2DTranspose(64, (3, 3), strides=(2, 2), padding='same')(x)
    x = layers.LeakyReLU()(x)

    outputs = layers.Conv2D(1, (7, 7), padding='same', activation='tanh')(x)

    return Model(inputs, outputs)


def build_discriminator():
    inputs = tf.keras.Input(shape=(128, 128, 1))

    x = layers.Conv2D(64, (4, 4), strides=(2, 2), padding='same')(inputs)
    x = layers.LeakyReLU()(x)

    for _ in range(3):
        x = layers.Conv2D(128, (4, 4), strides=(2, 2), padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.LeakyReLU()(x)

    outputs = layers.Conv2D(1, (4, 4), padding='same')(x)

    return Model(inputs, outputs)


# Generators
G_pop_to_lofi = build_generator()
G_lofi_to_pop = build_generator()

# Discriminators
D_pop = build_discriminator()
D_lofi = build_discriminator()

G_pop_to_lofi.summary()
G_lofi_to_pop.summary()
D_pop.summary()
D_lofi.summary()
