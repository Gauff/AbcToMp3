# ABC2MP3 Converter
=====================

Transforms ABC notation files into high-quality MP3 audio files by leveraging the power of sound fonts.

### Overview

This project is a command-line tool that takes an ABC file as input, generates a MIDI file from it, converts the MIDI file to WAV, and then converts the WAV file to MP3. 
The script uses the `abc2midi` executable to generate the MIDI file, `fluidsynth` to convert the MIDI file to WAV, and `pydub` to convert the WAV file to MP3.
This will generate a new directory called "output" containing the converted MP3 files.

### Configuration

The script can be configured by modifying the `abc2midi_path`, `abc_file_path`, `sound_font_path`, and `tempo_bpm` variables at the top of the file.

### Dependencies

* `abc2midi` executable
* `fluidsynth` executable
* `pydub` library
* Python 3.x

### Credits

This project was inspired by [EasyABC](https://easyabc.net/) and [FluidSynth](https://www.fluidsynth.org/).

### License

This project is licensed under the MIT License.