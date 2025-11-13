import os
import re

def find_files_by_number(target_number):
    root_dir = 'dsdl_specs'
    matched_files = []
    pattern = re.compile(rf'^{target_number}\..+')

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if pattern.match(filename):
                matched_files.append(os.path.join(dirpath, filename))


    filename = os.path.basename(matched_files[0])  
    parts = filename.split('.')  
    return parts[1]


print(find_files_by_number(1010))

