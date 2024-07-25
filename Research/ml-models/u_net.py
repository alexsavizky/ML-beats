import tensorflow as tf
from tensorflow.keras import layers, Model


def unet_model(input_shape):
    inputs = tf.keras.Input(input_shape)

    # encoder
    c1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    c1 = layers.MaxPooling2D((2, 2))(c1)
    c2 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c1)
    c2 = layers.MaxPooling2D((2, 2))(c2)
    c3 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(c2)
    c3 = layers.MaxPooling2D((2, 2))(c3)

    # bottleneck
    bottleneck = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(c3)
    # decoder
    d1 = layers.Conv2DTranspose(256, (3, 3), strides=(2, 2), padding='same')(bottleneck)
    d1 = layers.concatenate([d1, c3])
    d2 = layers.Conv2DTranspose(128, (3, 3), strides=(2, 2), padding='same')(d1)
    d2 = layers.concatenate([d2, c2])
    d3 = layers.Conv2DTranspose(64, (3, 3), strides=(2, 2), padding='same')(d2)
    d3 = layers.concatenate([d3, c1])
    outputs = layers.Conv2D(1, (1, 1), activation='sigmoid')(d3)
    return Model(inputs, outputs)


input_shape = (128, 128, 1)  # Example input shape
model_unet = unet_model(input_shape)
model_unet.summary()
