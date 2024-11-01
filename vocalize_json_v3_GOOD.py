import json
import subprocess
import tempfile
import os
import re

def vocalize_arabic_in_json(input_json_file, output_json_file, jar_path):
    # Load the JSON data
    with open(input_json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Prepare a temporary file for the Arabic text
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_input_file:
        for key, value in data.items():
            if isinstance(value, str):
                # Extract Arabic text from the string using regex
                arabic_texts = re.findall(r'[\u0600-\u06FF]+', value)
                if arabic_texts:  # If there are Arabic texts
                    for arabic_text in arabic_texts:
                        temp_input_file.write(arabic_text + '\n')

    temp_input_file_path = temp_input_file.name

    # Prepare a temporary output file for diacritized text
    temp_output_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')

    try:
        # Run the Farasa diacritization tool
        subprocess.run(
            ["java", "-jar", jar_path, "-i", temp_input_file_path, "-o", temp_output_file.name],
            check=True
        )

        # Read the diacritized output
        with open(temp_output_file.name, 'r', encoding='utf-8') as temp_output:
            diacritized_lines = [line.strip() for line in temp_output.readlines()]

        # Update the original JSON with diacritized text
        diacritized_index = 0
        for key in data.keys():
            value = data[key]
            if isinstance(value, str):
                # Replace only the Arabic parts with their diacritized versions
                def replace_arabic(match):
                    nonlocal diacritized_index
                    arabic_word = match.group(0)
                    if diacritized_index < len(diacritized_lines):
                        diacritized_word = diacritized_lines[diacritized_index]
                        diacritized_index += 1
                        return diacritized_word  # Return the diacritized word
                    return arabic_word  # In case there's an issue, return the original word

                # Replace Arabic words in the value
                updated_value = re.sub(r'[\u0600-\u06FF]+', replace_arabic, value)
                data[key] = updated_value

    finally:
        # Clean up temporary files
        os.remove(temp_input_file_path)
        os.remove(temp_output_file.name)

    # Write the updated data back to a new JSON file
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    input_json_filename = "ar_sa.json"  # Your input JSON file
    output_json_filename = "diacritized_ar_sa.json"  # Output JSON file with diacritized text
    jar_file_path = "/home/reng/Downloads/QCRI/Dev/ArabicNLP/Farasa/FarasaDiacritizeJar/dist/FarasaDiacritizeJar.jar"  # Path to the jar file

    vocalize_arabic_in_json(input_json_filename, output_json_filename, jar_file_path)
