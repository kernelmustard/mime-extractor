# mime-extractor
This is python script to generate the fileextraction_defaults.yaml file used by Security Onion's so-zeek. By default it is a pain to format and manage, especially if you want more than the default extracted MIME types in a Security Onion setup. It downloads and merges the list of official MIME types on iana.org and the list of MIME types libmagic uses to identify files. 

# Setup
1. Create venv to isolate packages
```
python -m venv /path/to/venv
source /path/to/venv/bin/activate # if *nix OS
\path\to\venv\Scripts\activate # if Windows OS
```
ref: https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-virtual-environments

2. Install requirements
```
 python -m pip install -r requirements.txt
 ```

# Issues
- The generated fileextraction_defaults.yaml has a trailing "      - " because of unoptimized regex, which will break if you drop it straight into a Security Onion deployment. Simply delete that line.