# Specify your source and destination directories here

import os
import shutil
import sys

def get_next_available_name(base_path, base_name):
    counter = 0
    base_name = "-".join(base_name.split("-")[0:-1])
    print(base_name)
    new_name = f"{base_name}-{counter}"
    while os.path.exists(os.path.join(base_path, new_name)):
        new_name = f"{base_name}-{counter}"
        counter += 1
    return new_name

def copy_folders(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        if "tmp" in item:
            continue
        if os.path.isdir(src_path):
            dst_path = os.path.join(dst, item)
            if os.path.exists(dst_path):
                new_name = get_next_available_name(dst, item)
                dst_path = os.path.join(dst, new_name)
            os.makedirs(dst_path)
            shutil.copy(os.path.join(src_path, "cov-all.log"), os.path.join(dst_path, "cov-all.log"))

copy_folders(sys.argv[1], sys.argv[2])
