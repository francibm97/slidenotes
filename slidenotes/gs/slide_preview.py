import os
from slidenotes import gs

def generate_slide_preview(input_path, cache=True):
    output_path = input_path + ".preview.jpg"

    if os.path.isfile(output_path) and cache:
        return output_path

    gs.generate_jpg_preview(input_path, output_path)
    return output_path
