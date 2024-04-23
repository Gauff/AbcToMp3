import subprocess
import os
from pydub import AudioSegment
import concurrent.futures
import re


abc2midi_path = r'C:\temp\EasyABC\bin\abc2midi.exe'
abc_file_path = r'songs.abc'
sound_font_path = r"C:\temp\SoundFonts\HQ_Orchestral_Soundfont_Collection_v3.0.sf2"
tempo_bpm = 140

# Define the MIDI directives
midi_directives = [
    "%%MIDI control 7 96",   # Set channel volume to 96
    "%%MIDI control 10 64",  # Set panning position to 64 (center)
    "%%MIDI gchordon",       # Begin guitar chord event
    "%%MIDI program 46",     # Set instrument program to 46
    "%%MIDI chordprog 24",   # Set chord instrument program to 24
    "%%MIDI bassprog 24",    # Set bass instrument program to 24
    "%%MIDI chordvol 73",    # Set chord volume to 73
    "%%MIDI bassvol 73",     # Set bass volume to 73
    "%%MIDI control 7 91",   # Adjust channel volume to 91
    f"Q:1/4 ={tempo_bpm}"    # Adjust tempo
]

def sanitize_filename(filename):
    # Define a regular expression pattern to match valid filename characters
    # This pattern includes letters (upper and lower case), digits, underscores, and hyphens
    pattern = r'[^a-zA-Z0-9_\-\.]'

    # Replace any characters not matching the pattern with an underscore
    sanitized_filename = re.sub(pattern, '_', filename)

    return sanitized_filename

# Function to generate MIDI file from ABC content
def generate_midi_file(output_directory, tune_abc):
    tune_number = get_tune_number(tune_abc)
    tune_name = get_tune_name(tune_abc)
    tune_filename = sanitize_filename(f"{int(tune_number):04d} - {tune_name}")
    midi_file_path = os.path.join(output_directory, f"{tune_filename}.mid")

    # https://www.mankier.com/1/abc2midi for settings
    command = [
        abc2midi_path,
        "-",
        "-o",
        midi_file_path,
        "-BF",
        "-TT",
        "440",
        "-EA"
    ]
    try:
        # Open a subprocess with the command
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Pass the input ABC content to the subprocess
        stdout, stderr = process.communicate(input=tune_abc)

        # Check for errors
        if stderr:
            print(f"Error: {stderr}")
        else:
            print("Conversion successful.")

    except Exception as e:
        print(f"An error occurred: {e}")

    return midi_file_path


def normalize_audio(audio):
    return audio.apply_gain(-audio.max_dBFS)


# Function to convert MIDI to WAV
def convert_midi_to_wav(midi_filename, output_directory, tune_filename):
    wav_filename = os.path.join(output_directory, f"{tune_filename}.wav")
    subprocess.run(
        [
            "fluidsynth",
             "-i",
             sound_font_path,
             "-o",
             "audio.driver=dsound",
             midi_filename,
             "-F",
             wav_filename],
        check=True)
    return wav_filename

# Function to convert WAV to MP3
def convert_wav_to_mp3(output_directory, tune_filename, wav_filename):
    mp3_filename = os.path.join(output_directory, f"{tune_filename}.mp3")

    audio = AudioSegment.from_wav(wav_filename)

    # Normalize audio to -3dB
    normalized_audio = normalize_audio(audio)

    normalized_audio.export(mp3_filename, format="mp3")

    return mp3_filename

# Function to add MIDI controls to a tune
def add_midi_controls_to_a_tune(tune_abc):
    tune_lines = f"X:{tune_abc}".split("\n")

    index_split = 1
    part1 = tune_lines[:index_split]
    part2 = tune_lines[index_split:]

    tune_lines = part1 + midi_directives + part2

    return '\n'.join(tune_lines)

# Function to add MIDI controls to tunes in an ABC file
def add_midi_controls_to_abc_file(file_path):
    # Load the content of the ABC file
    with open(file_path, 'r') as file:
        abc_content = file.read()

        tunes = abc_content.split('X:')[1:]

        modified_tunes = []

        for tune_abc in tunes:
            modified_tune = add_midi_controls_to_a_tune(tune_abc)
            modified_tunes.append(modified_tune)

        return modified_tunes

# Function to process a tune and generate MP3
def process_tune(tune_abc):
    generate_mp3_from_abc_tune(tune_abc)

# Function to generate MP3 from ABC tune
def generate_mp3_from_abc_tune(tune_abc, output_directory="output"):
    try:
        tune_number = get_tune_number(tune_abc)
        tune_name = get_tune_name(tune_abc)
        tune_filename = sanitize_filename(f"{int(tune_number):04d} - {tune_name}")
        print(f"Processing song {tune_filename}")

        # Create output directory if it doesn't exist
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        midi_filename = generate_midi_file(output_directory, tune_abc)
        wav_filename = convert_midi_to_wav(midi_filename, output_directory, tune_filename)
        mp3_filename = convert_wav_to_mp3(output_directory, tune_filename, wav_filename)

        # Delete the temporary WAV and MIDI files
        os.remove(wav_filename)
        os.remove(midi_filename)

        print(f"MP3 file {mp3_filename} generated.")

    except Exception as e:
        print(f"An exception occurred while processing tune: {e}")

# Function to get the name of a tune from ABC content
def get_tune_name(abc_content):
    lines = abc_content.split('\n')
    for line in lines:
        if line.startswith('T:'):
            return line[2:].strip()

# Function to get the number of a tune from ABC content
def get_tune_number(abc_content):
    lines = abc_content.split('\n')
    for line in lines:
        if line.startswith('X:'):
            return line[2:].strip()



# Add MIDI controls to tunes in the ABC file
modified_tunes = add_midi_controls_to_abc_file(abc_file_path)

# Number of threads to use for parallel processing
num_threads = 15

# Process tunes in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(process_tune, modified_tunes)
