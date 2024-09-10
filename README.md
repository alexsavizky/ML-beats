
## ML-Beats: Genre Transformation from Popular Music to Lofi

### Project Overview

This project, titled **ML-Beats**, focuses on genre transformation in music using machine learning techniques. Specifically, we aim to convert popular music tracks into lofi music. The repository is organized into research, data processing, and model training components, facilitating the transformation of popular music into the desired lofi genre.

### Directory Structure

```bash
ML-Beats/
│
├── .venv/                     # Python virtual environment
│
├── Research/
│   ├── ml-models/              # Model architecture and training scripts
│   │   ├── cycle_gan.py        # Main CycleGAN architecture for genre transformation
│   │   ├── generator_g_model.h5# Pretrained model weights
│   │   ├── preprocess.py       # Data preprocessing scripts
│   │   ├── train_models.py     # Scripts for training CycleGAN
│   │   ├── u_net.py            # U-Net architecture for enhancement
│   │   └── wave_net.py         # WaveNet architecture for music generation
│   └── scrap/
│       ├── downloads/          # Raw music data downloads
│       ├── raw_music_pop/      # Popular music samples
│       └── yt_cookies.txt      # YouTube cookies for scraping audio
│
├── separation/
│   └── main.py                 # Main script for music separation and conversion
│
├── temp-data/
│   ├── lofi_spectrograms/      # Spectrogram data for lofi music
│   ├── regular_spectrograms/   # Spectrogram data for pop music
│   ├── D_lofi_model.png        # Discriminator model for lofi
│   ├── G_lofi_to_pop_model.png # Generator for converting lofi to pop
│   └── output_lofi.mp3         # Sample output lofi track
│
├── webapp/
│   ├── static/                 # Web app static files
│   ├── templates/              # HTML templates
│   └── db.py                   # Database interaction scripts
│
├── .gitignore                  # Git ignore file
└── README.md                   # Project documentation
```

### Features

- **CycleGAN Architecture**: The primary model architecture is based on CycleGAN, enabling unsupervised genre transformation between popular and lofi music.
- **Spectrogram Data**: The music files are converted to spectrograms, which serve as the input data for the model.
- **Preprocessing**: Efficient preprocessing of audio data, including the separation of vocals and beats, is included.
- **WaveNet Enhancement**: WaveNet is used to refine the audio quality and style in the output music.
- **Web Interface**: A simple web app interface is provided to allow users to upload popular music files and generate lofi versions.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ML-Beats.git
   ```
2. Set up a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # For Unix
   .venv\Scripts\activate     # For Windows
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Preprocess the data:
   ```bash
   python Research/ml-models/preprocess.py
   ```
2. Train the CycleGAN model:
   ```bash
   python Research/ml-models/train_models.py
   ```
3. Generate lofi music from a popular music input:
   ```bash
   python separation/main.py
   ```

### Data

- **Popular Music Dataset**: A collection of popular music tracks used for training.
- **Lofi Music Dataset**: A collection of lofi music tracks.
- **Spectrograms**: Generated from both the popular and lofi datasets to serve as input to the CycleGAN model.

### Results

The model successfully transforms popular music tracks into the lofi genre while preserving key characteristics such as rhythm and melody. Sample outputs are provided in the `temp-data/` directory, including spectrograms and generated audio files.

### Web Interface

A basic web interface allows users to upload their own popular music and transform it into lofi. The app is located in the `webapp/` folder.

### Future Work

- **Model Refinement**: Enhancing the model with more advanced architectures like WaveNet and U-Net for better music quality.
- **Additional Genres**: Extending the project to support additional genre transformations.
- **Real-Time Conversion**: Implementing real-time conversion and streaming of transformed audio.

