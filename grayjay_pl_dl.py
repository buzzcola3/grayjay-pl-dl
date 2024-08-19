import json
import re
import os
import shutil
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse


def get_last_object_from_array(file_path):
    """
    Reads a JSON file and returns the last object in the array.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or None: The last object in the array, or None if the array is empty.
    """
    with open(file_path, 'r', encoding="UTF-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("The JSON data is not an array.")

    return data[-1] if data else None


def save_object_to_json(file_path, obj):
    """
    Saves a Python object as a pretty-printed JSON string in a text file.

    Args:
        file_path (str): The path to the output text file.
        obj (dict or list): The object to save.
    """
    json_string = json.dumps(obj, indent=4)

    with open(file_path, 'w', encoding="UTF-8") as file:
        file.write(json_string)


def crop_cache_string(file_path, save_changes=False):
    """
    Crops '__CACHE:' from the start and a '"' from the end of the content in the given file.

    Args:
        file_path (str): The path to the text file.
        save_changes (bool): If True, saves the changes to the file. If False, returns the modified content.

    Returns:
        str: The modified content if save_changes is False.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    if content.startswith('"__CACHE:'):
        content = content[len('"__CACHE:'):]

    if content.endswith('"'):
        content = content[:-1]

    if save_changes:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    else:
        return content


def replace_and_remove_quotes(file_path, save_changes=False):
    """
    Removes unescaped '"' from the content and replaces all occurrences of '\"' with '"'.

    Args:
        file_path (str): The path to the text file.
        save_changes (bool): If True, saves the changes to the file. If False, returns the modified content.

    Returns:
        str: The modified content if save_changes is False.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    content_no_unescaped_quotes = re.sub(r'(?<!\\)"', '', content)
    final_content = content_no_unescaped_quotes.replace(r'\"', '"')

    if save_changes:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(final_content)
    else:
        return final_content


def load_json(json_str):
    """
    Loads a JSON string and returns its content as a Python variable.

    Args:
        json_str (str): The JSON string.

    Returns:
        dict or list: The content of the JSON string as a Python dictionary or list.
    """
    return json.loads(json_str)


def remove_escaped_quotes(file_path, save_changes=False):
    """
    Removes all occurrences of '\\"' from the content of the given file.

    Args:
        file_path (str): The path to the text file.
        save_changes (bool): If True, saves the changes to the file. If False, returns the modified content.

    Returns:
        str: The modified content if save_changes is False.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    modified_content = content.replace(r'\\"', '')

    if save_changes:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
    else:
        return modified_content


def filter_json_data(data):
    """
    Filters the JSON data to keep only the 'value' and 'name' fields.

    Args:
        data (dict): The JSON data as a dictionary.

    Returns:
        dict: The filtered JSON data.
    """
    filtered_data = []
    for video in data.get("videos", []):
        filtered_video = {
            "name": video.get("name"),
            "value": video.get("id", {}).get("value")
        }
        filtered_data.append(filtered_video)
    return {"videos": filtered_data}


def sanitize_filename(name):
    """
    Sanitizes the filename by removing or replacing characters that are not allowed in filenames.

    Args:
        name (str): The original filename.

    Returns:
        str: The sanitized filename.
    """
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)

def convert_file_to_mp3(file_path, directory):
    """
    Converts a single .webma or .mp4a file to .mp3 format and removes the original file.

    Args:
        file_path (str): The path to the file to convert.
        directory (str): The directory where the files are located.
    
    Returns:
        tuple: A tuple containing the filename and a boolean indicating success or failure.
    """
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    mp3_filename = f"{base_name}.mp3"
    mp3_file_path = os.path.join(directory, mp3_filename)

    command = [
        'ffmpeg', '-i', file_path,
        '-q:a', '0',  # Best audio quality
        '-map', 'a',
        '-loglevel', 'error',  # Suppress output unless there's an error
        mp3_file_path
    ]

    try:
        subprocess.run(command, check=True)
        os.remove(file_path)
        return (file_path, True)
    except subprocess.CalledProcessError:
        return (file_path, False)
        
def convert_folder_to_mp3(directory, max_workers=None):
    """
    Converts .webma and .mp4a files in the specified directory to .mp3 format with high quality,
    using multiple processes to speed up the conversion. Tracks the progress and counts the number
    of successful and failed conversions.

    Args:
        directory (str): The path to the directory containing the files to convert.
        max_workers (int, optional): The maximum number of worker processes to use. If None, uses the number of available CPU cores.
    """
    files_to_convert = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.webma') or f.endswith('.mp4a')]
    total_files = len(files_to_convert)
    success_count = 0
    failure_count = 0

    print("Converting to MP3")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_file_to_mp3, file_path, directory): file_path for file_path in files_to_convert}
        
        for future in as_completed(futures):
            filename, success = future.result()
            if success:
                success_count += 1
            else:
                failure_count += 1

            # Print progress
            print(f"Convert to MP3: {success_count + failure_count}/{total_files} - Success: {success_count}, Failures: {failure_count}")

    print(f"Conversion completed. Total: {total_files}, Successful: {success_count}, Failed: {failure_count}")


def rename_files_based_on_json(json_data, input_directory, output_directory):
    """
    Copies files from the input directory to the output directory, renames them based on 
    'value' and 'name' fields from the JSON data, and saves the renamed files to the output directory.

    Args:
        json_data (dict): The JSON data containing video details.
        input_directory (str): The path to the directory where the original files are located.
        output_directory (str): The path to the directory where the renamed files will be saved.
    """
    videos = json_data.get("videos", [])

    for video in videos:
        value = video.get("value")
        name = sanitize_filename(video.get("name"))

        if not value or not name:
            print(f"Skipping due to missing 'value' or 'name' for video: {video}")
            continue

        for filename in os.listdir(input_directory):
            if value in filename:
                old_file_path = os.path.join(input_directory, filename)
                file_extension = os.path.splitext(filename)[1]
                name_with_extension = f"{name}{file_extension}"
                new_file_path = os.path.join(output_directory, name_with_extension)

                # Copy the file to the output directory first
                copied_file_path = shutil.copy(old_file_path, output_directory)

                # Rename the copied file in the output directory
                os.rename(copied_file_path, new_file_path)

                print(f"Copied '{filename}' to '{output_directory}', then renamed to '{name_with_extension}'")



DEFAULT_GRAYJAY_FOLDER = "/data/data/com.futo.platformplayer/files/downloads/"
DEFAULT_MUSIC_FOLDER = "/sdcard/Music/" # + playlist name
DEFAULT_WORK_FOLDER = DEFAULT_MUSIC_FOLDER + "grayjay/"         #/sdcard/Music/grayjay/
DEFAULT_PLAYLIST_JSON = DEFAULT_WORK_FOLDER + 'playlist.json'   #/sdcard/Music/grayjay/playlist.json

def grayjay_pl_dl(grayjay_dl_folder=DEFAULT_GRAYJAY_FOLDER, output_folder=DEFAULT_WORK_FOLDER, grayjay_playlist_json=DEFAULT_PLAYLIST_JSON, convert_to_mp3=True):
    last_object = get_last_object_from_array(grayjay_playlist_json)
    save_object_to_json(output_folder + 'cache.json', last_object)

    crop_cache_string(output_folder + 'cache.json', save_changes=True)
    replace_and_remove_quotes(output_folder + 'cache.json', save_changes=True)
    modified_content = remove_escaped_quotes(output_folder + 'cache.json', save_changes=False)
    useful_json = load_json(modified_content)
    useful_json = filter_json_data(useful_json)

    rename_files_based_on_json(useful_json, grayjay_dl_folder, output_folder)

    if convert_to_mp3:
        convert_folder_to_mp3(output_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grayjay Playlist Downloader and Converter")
    
    # Adding optional arguments
    parser.add_argument("-i", "--input_dir", type=str, default=DEFAULT_GRAYJAY_FOLDER,
                        help="Directory where Grayjay downloads are located (default: /data/data/com.futo.platformplayer/files/downloads/)")
    parser.add_argument("-o", "--output_dir", type=str, default=DEFAULT_WORK_FOLDER,
                        help="Directory where the processed files will be saved (default: /sdcard/Music/grayjay/)")
    parser.add_argument("-p", "--playlist_json", type=str, default=DEFAULT_PLAYLIST_JSON,
                        help="Path to the playlist JSON file (default: /sdcard/Music/grayjay/playlist.json)")
    parser.add_argument("-c", "--convert_to_mp3", action="store_true", default=True,
                        help="Convert downloaded files to MP3 format (default: True)")
    parser.add_argument("-d", "--default", action="store_true", help="Run with default settings")
    
    args = parser.parse_args()
    
    if args.default:
        grayjay_pl_dl()
    else:
        grayjay_pl_dl(grayjay_dl_folder=args.input_dir, output_folder=args.output_dir, grayjay_playlist_json=args.playlist_json, convert_to_mp3=args.convert_to_mp3)
