import tensorflow as tf
from tensorflow.keras import layers, Model


def residual_block(x, dilation_rate):
    skip = x
    tanh_out = layers.Conv1D(64, 2, dilation_rate=dilation_rate, padding='causal', activation='tanh')(x)
    sigm_out = layers.Conv1D(64, 2, dilation_rate=dilation_rate, padding='causal', activation='sigmoid')(x)
    merged = layers.Multiply()([tanh_out, sigm_out])
    out = layers.Conv1D(64, 1, padding='same')(merged)
    return layers.Add()([out, skip]), out


def wavenet_model(input_shape):
    inputs = tf.keras.Input(input_shape)
    x = layers.Conv1D(64, 2, padding='causal')(inputs)

    skips = []
    for i in range(10):
        x, skip = residual_block(x, dilation_rate=2 ** i)
        skips.append(skip)

    x = layers.Add()(skips)
    x = layers.Activation('relu')(x)

    x = layers.Conv1D(128, 1, padding='same', activation='relu')(x)
    x = layers.Conv1D(256, 1, padding='same', activation='relu')(x)
    outputs = layers.Conv1D(1, 1, activation='tanh')(x)

    return Model(inputs, outputs)


input_shape = (16000, 1)  # Example input shape
model_wavenet = wavenet_model(input_shape)
model_wavenet.summary()
