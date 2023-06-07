#!/usr/bin/env python3

import sys
import urllib3
import csv
from os import remove
import mimetypes
import yaml
import re

def download_iana_mimes():
    media_types = ["application", "audio", "font", "image", "message", "model", "multipart", "text", "video"]
    http = urllib3.PoolManager()
    iana_dict = {}

    for type in media_types:
        # pull updated MIME type CSVs from the IANA registry
        url = "https://www.iana.org/assignments/media-types/" + type + ".csv"
        file = type + ".csv"
        with http.request("GET", url, preload_content=False) as r:
            # write to working dir
            with open(file, "wb") as f:
                f.write(r.read())
        # parse the CSV and pull out the mime types
        with open(file, 'r') as f:
            csv_reader = csv.DictReader(f)
            mime_types = [row['Template'] for row in csv_reader]
            for mt in mime_types:
                file_extensions = mimetypes.guess_all_extensions(mt)
                for fe in file_extensions:
                    if fe and mt:
                        iana_dict.update({mt: fe})
                    elif mt:
                        iana_dict.update({mt + '.unk'})
        # clean up
        remove(file)
    return iana_dict

def download_magic_mimes():
    magic_dict = {}
    http = urllib3.PoolManager()
    url = "https://raw.githubusercontent.com/magic/mime-types/master/src/mimes.mjs"

    with http.request("GET", url, preload_content=False) as r:
        mimes_mjs = r.data.decode('utf-8')

    fe_pattern = re.compile(r"  (.*):")
    mt_pattern = re.compile(r": \'(.*)\',")

    file_extensions = fe_pattern.findall(mimes_mjs)
    mime_types = mt_pattern.findall(mimes_mjs)

    magic_dict.update(zip(mime_types, file_extensions))

    return magic_dict

def main():
    # download and parse MIME types from IANA
    iana_dict = download_iana_mimes()

    # download and parse MIME types from libmagic
    magic_dict = download_magic_mimes()

    # merge, sort, dedup, and write to fileextraction_defaults.yaml
    merged_dict = {**iana_dict, **magic_dict}
    sorted_dict = sorted(merged_dict.keys())
    dedup_dict = {mime_type: merged_dict[mime_type] for mime_type in sorted(set(sorted_dict))}
    formatted1 = re.sub(r'\n', r'\n      - ', yaml.dump(dedup_dict, default_flow_style = False), count=0)
    formatted2 = re.sub(r'^', r'      - ', formatted1) # first line edge case
    formatted3 = re.sub(r': ', r': misc#  ', formatted2)

    with open('fileextraction_defaults.yaml', 'w') as fe_yaml:
        fe_yaml.write("zeek:\n  policy:\n    file_extraction:\n")
        fe_yaml.write(formatted3)
    return 0

if __name__ == '__main__':
    main()
else:
    sys.exit()