```markdown
# Grayjay Playlist Extractor and Converter Tool for Termux (requires root)

A command-line tool for managing and converting Grayjay playlist files. This tool Extracts the playlist data, processes the data, and converts media files to MP3 format. It also supports renaming files based on metadata from the playlist.

## Features

- **Extract and Process Playlist Data**: Fetches the latest playlist data and performs various cleanup operations.
- **File Conversion**: Converts `.webma` and `.mp4a` files to `.mp3` format with high quality.
- **File Renaming**: Renames files based on metadata from the playlist.
- **Multi-core Conversion**: Utilizes multiple CPU cores to speed up file conversion.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/buzzcola3/grayjay-pl-dl.git
   cd grayjay-pl-dl
   ```

2. **Install Dependencies**

   Ensure you have Python 3 installed. You may also need `ffmpeg` installed on your system.

   pkg install ffmpeg
   pkg install python
   pkg install tsu (for root access)

   Install required Python packages using `pip`

## Usage

### Basic Usage

Run the tool with default settings in Termux Android shell:

```bash
tsu python grayjay_pl_dl.py
```

### Command-Line Options

- `-i, --input`: The path to the directory containing the original playlist files. Default is `/data/data/com.futo.platformplayer/files/downloads/`.
- `-o, --output`: The path to the directory where the renamed and converted files will be saved. Default is `/sdcard/Music/grayjay/`.
- `-j, --json`: The path to the JSON file containing playlist data. Default is `/sdcard/Music/grayjay/playlist.json`.
- `-c, --convert`: Whether to convert files to MP3 format. Default is `True`.
- `-h, --help`: Show this help message and exit.

**Example:**

```bash
tsu python grayjay_pl_dl.py -i /path/to/input -o /path/to/output -j /path/to/playlist.json -c False
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests. Ensure you follow the project's coding standards and include tests where applicable.

## Contact

For questions or comments, please open an issue on the [GitHub repository](https://github.com/buzzcola3/grayjay-pl-dl/issues).

```