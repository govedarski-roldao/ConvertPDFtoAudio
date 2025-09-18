import os
import asyncio
import edge_tts
import pdfplumber
from moviepy import *
import math

pdf_path = "Homo Deus_bg.pdf"
output_mp3 = pdf_path.replace(".pdf", ".mp3")
voice_pt_m = "pt-PT-DuarteNeural"
voice_pt_f = 'pt-PT-RaquelNeural'
voice_bg_m = 'bg-BG-IvanNeural'
voice_bg_f = 'bg-BG-KalinaNeural'
blocks_num = 0
max_chars = 4000
total_characters = 0
output_dir = "output"

print(f"The final audiobook will be saved as: {output_mp3}")


# 1. Extract text from PDF
def extract_text(pdf_path):
    page_count = 0
    full_text = ''
    with pdfplumber.open(pdf_path) as pdf:
        print("📄 PDF file found.")
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Join lines to avoid unnatural pauses
                text = ' '.join(text.splitlines())
                full_text += text + '\n\n'
                page_count += 1
                print(f'✅ Extracted page {page_count}')
    return full_text


# 2. Split text into manageable chunks
def split_into_blocks(text, size=max_chars):
    print("✂️ Splitting text into smaller blocks...")
    return [text[i:i + size] for i in range(0, len(text), size)]


# 3. Generate MP3 files using Edge-TTS
async def generate_mp3_files(blocks, voice, total):
    global blocks_num
    global output_dir
    os.makedirs(output_dir, exist_ok=True)

    for i, block in enumerate(blocks):
        file_name = os.path.join(output_dir, f"part_{i + 1}.mp3")
        communicate = edge_tts.Communicate(text=block, voice=voice, rate="-11%")
        await communicate.save(file_name)
        print(f"🎧 Saved: {file_name} of {total}")
        blocks_num += 1


print(f"Preparing to merge {blocks_num} blocks")


# 4. Merge all MP3 parts into one final file
def merge_mp3_files(output_filename=output_mp3):
    global output_mp3
    print("🎛 Merging audio parts into one file...")
    parts = sorted(
        os.path.join(output_dir, f) for f in os.listdir(output_dir)
        if f.startswith("part_") and f.endswith(".mp3")
    )

    if not parts:
        print("⚠️ No MP3 parts found to merge.")
        return

    audio_clips = [AudioFileClip(part) for part in parts]
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(output_filename)
    print(f"✅ Final audiobook saved as: {output_filename}")

    print("🧹 Cleaning up temporary part files...")
    for part in parts:
        try:
            os.remove(part)
            print(f"🗑 Deleted: {part}")
        except Exception as e:
            print(f"⚠️ Could not delete {part}: {e}")
    print("BOOK CREATED!!!")


# 5. Main execution
if __name__ == "__main__":
    full_text = extract_text(pdf_path)
    total_blocks = math.ceil(len(full_text) / 4000)
    print(f"Counted {len(full_text)} characters")
    blocks = split_into_blocks(full_text)
    asyncio.run(generate_mp3_files(blocks, voice_bg_f, total_blocks))
    merge_mp3_files()
