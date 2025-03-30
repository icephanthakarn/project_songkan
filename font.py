# Re-import libraries and re-run conversion due to state reset
import zipfile
import os
from pathlib import Path
from fontTools.ttLib import TTFont

# Re-extract ZIP file
zip_path = r"D:\project_year4\web2\front\baansuan_prannok-fonts.zip"
extract_path = r"D:\project_year4\web2\front\baansuan_fonts"
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Locate font folder and list files
font_folder_path = os.path.join(extract_path, 'sukhumvit-set')
font_files = os.listdir(font_folder_path)

# Convert TTF to WOFF2
output_fonts_path = r"D:\project_year4\web2\front\woff2_fonts"
os.makedirs(output_fonts_path, exist_ok=True)

converted_files = []

for ttf_file in font_files:
    if ttf_file.endswith(".ttf"):
        ttf_path = os.path.join(font_folder_path, ttf_file)
        font = TTFont(ttf_path)
        woff2_filename = Path(ttf_file).with_suffix('.woff2').name
        woff2_path = os.path.join(output_fonts_path, woff2_filename)
        font.flavor = 'woff2'
        font.save(woff2_path)
        converted_files.append(woff2_filename)

converted_files
