# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from spleeter.separator import Separator

def separate_vocals(input_file, output_dir):
    # Initialize Spleeter separator
    separator = Separator('spleeter:2stems')

    # Specify input and output paths
    input_path = input_file
    output_path = output_dir

    # Perform source separation
    separator.separate_to_file(input_path, output_path)


from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH




def audio_to_midi(input_audio_file, output_midi_file):
    # Set parameters
    samplerate = 44100
    hop_size = 512

    # Open audio file
    source = aubio.source(input_audio_file, samplerate, hop_size)

    # Open MIDI output file
    midi_output = aubio.midioutput(1)
    midi_output.open(output_midi_file)

    # Create pitch detection object
    pitch_o = aubio.pitch("yin", samplerate, hop_size)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(0.8)

    # Process audio
    while True:
        samples, read = source()
        pitch = pitch_o(samples)[0]
        midi_output.write([pitch])

        if read < hop_size:
            break

    # Close MIDI output file
    midi_output.close()




if __name__ == '__main__':
    # input_file = 'Research/Separation/music_files/Hiatus Kaiyote - Nakamarra.mp3'
    # output_dir = 'Research/Separation/music_files/'
    # separate_vocals(input_file, output_dir)

    # Example usage
    input_audio_file = 'music_files/result.mp3/test/vocals.wav'
    output_midi_file = 'music_files/result.mp3/test/vocals.mid'


    audio_to_midi(input_audio_file, output_midi_file)
