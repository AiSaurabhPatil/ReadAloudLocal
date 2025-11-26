# ReadAloudLocal

**ReadAloudLocal** is a lightning-fast, offline text-to-speech (TTS) application for Windows. It uses the **Supertonic** ONNX model to generate high-quality speech instantly and features a premium dark-themed UI with clipboard integration.

## Features

- **🚀 Lightning Fast**: Runs locally on your CPU/GPU using ONNX Runtime. No cloud APIs, no latency.
- **🔒 Privacy First**: All processing happens on your device.
- **📋 Clipboard Reader**: Automatically detects and reads text you copy from any application (Browser, PDF, etc.).
- **🎛️ Playback Controls**: Play, Pause, Stop, and adjustable reading speed (0.5x - 2.0x).
- **🌙 Dark Mode**: Sleek, modern charcoal interface.

## Prerequisites

- **Python 3.10+**
- **Git** (for cloning dependencies)
- **Microsoft Visual C++ Redistributable** (Required for PyTorch on Windows)

## Installation

1.  **Clone this repository**:
    ```powershell
    git clone https://github.com/AiSaurabhPatil/ReadAloudLocal.git
    cd ReadAloudLocal
    ```

2.  **Install Python Dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```

3.  **Setup Supertonic**:
    This app relies on the Supertonic engine. You need to clone it into the project directory:
    ```powershell
    # Clone the Supertonic repo
    git clone https://github.com/supertone-inc/supertonic.git
    
    # Download the model weights (requires Git LFS)
    git lfs install
    cd supertonic
    git clone https://huggingface.co/Supertone/supertonic assets
    cd ..
    ```

## Usage

1.  **Run the Application**:
    ```powershell
    python app.py
    ```

2.  **Manual Mode**:
    - Type or paste text into the main window.
    - Click **Generate & Play**.

3.  **Clipboard Mode**:
    - Click the **"Auto-Read Clipboard: OFF"** button to toggle it **ON**.
    - Copy text from any other application (`Ctrl+C`).
    - The app will automatically paste and read the text.

## Troubleshooting

-   **Error: `[WinError 126] ... fbgemm.dll`**:
    -   Install the [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe).
    -   Restart your computer.

-   **No Audio**:
    -   Check your system volume.
    -   Ensure `sounddevice` is installed correctly.

## License

This project uses code from [Supertonic](https://github.com/supertone-inc/supertonic).
