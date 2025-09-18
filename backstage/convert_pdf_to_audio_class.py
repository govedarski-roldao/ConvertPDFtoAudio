import os
import math
import asyncio
import pdfplumber
import edge_tts
from moviepy import *  # <- como pediste


class PDF2Audiobook:
    """
    Converte PDF -> audiobook MP3 usando:
      - pdfplumber (extração de texto)
      - edge_tts (síntese de fala)
      - moviepy (junção de partes)
    """

    VOICE_PT_M = "pt-PT-DuarteNeural"
    VOICE_PT_F = "pt-PT-RaquelNeural"
    VOICE_BG_M = "bg-BG-IvanNeural"
    VOICE_BG_F = "bg-BG-KalinaNeural"

    def __init__(
            self,
            pdf_path: str,
            voice: str = VOICE_BG_F,
            output_dir: str = "output",
            max_chars: int = 4000,
            rate: str = "-11%",
            output_mp3: str | None = None,
    ):
        self.pdf_path = pdf_path
        self.voice = voice
        self.output_dir = output_dir
        self.max_chars = max_chars
        self.rate = rate
        self.output_mp3 = output_mp3 or os.path.splitext(pdf_path)[0] + ".mp3"

        self.blocks = []
        self.total_chars = 0

    # 1) Extração de texto
    def extract_text(self) -> str:
        if not os.path.isfile(self.pdf_path):
            raise FileNotFoundError(f"PDF não encontrado: {self.pdf_path}")

        print(f"📄 PDF file found: {self.pdf_path}")
        text_acc = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    text_acc.append(" ".join(text.splitlines()))
                    print(f"✅ Extracted page {i}")
                else:
                    print(f"ℹ️ Page {i} had no extractable text.")
        full_text = "\n\n".join(text_acc)
        self.total_chars = len(full_text)
        print(f"Counted {self.total_chars} characters")
        return full_text

    # 2) Split em blocos
    def split_into_blocks(self, text: str) -> list[str]:
        print("✂️ Splitting text into smaller blocks...")
        self.blocks = [text[i:i + self.max_chars] for i in range(0, len(text), self.max_chars)]
        return self.blocks

    # 3) Geração de MP3 (assíncrono)
    async def _generate_mp3_files_async(self, blocks: list[str], total: int):
        os.makedirs(self.output_dir, exist_ok=True)
        for i, block in enumerate(blocks, start=1):
            file_name = os.path.join(self.output_dir, f"part_{i:04d}.mp3")
            communicate = edge_tts.Communicate(text=block, voice=self.voice, rate=self.rate)
            await communicate.save(file_name)
            print(f"🎧 Saved: {file_name} of {total}")

    def generate_mp3_files(self):
        if not self.blocks:
            print("⚠️ No blocks to synthesize.")
            return
        total_blocks = math.ceil(self.total_chars / self.max_chars) if self.total_chars else len(self.blocks)
        asyncio.run(self._generate_mp3_files_async(self.blocks, total_blocks))

    # 4) Merge das partes
    def merge_mp3_files(self, output_filename: str | None = None, cleanup_parts: bool = True):
        out = output_filename or self.output_mp3
        print("🎛 Merging audio parts into one file...")

        if not os.path.isdir(self.output_dir):
            print("⚠️ Output directory does not exist.")
            return None

        parts = sorted(
            os.path.join(self.output_dir, f)
            for f in os.listdir(self.output_dir)
            if f.startswith("part_") and f.endswith(".mp3")
        )
        if not parts:
            print("⚠️ No MP3 parts found to merge.")
            return None

        audio_clips = [AudioFileClip(p) for p in parts]
        final_audio = concatenate_audioclips(audio_clips)
        final_audio.write_audiofile(out)
        print(f"✅ Final audiobook saved as: {out}")

        # fechar handles
        for clip in audio_clips:
            try:
                clip.close()
            except Exception:
                pass
        try:
            final_audio.close()
        except Exception:
            pass

        if cleanup_parts:
            print("🧹 Cleaning up temporary part files...")
            for p in parts:
                try:
                    os.remove(p)
                    print(f"🗑 Deleted: {p}")
                except Exception as e:
                    print(f"⚠️ Could not delete {p}: {e}")

        print("BOOK CREATED!!!")
        return out

    # 5) Pipeline completo
    def run(self) -> str | None:
        text = self.extract_text()
        if not text.strip():
            print("⚠️ Extracted text is empty. Aborting.")
            return None
        self.split_into_blocks(text)
        self.generate_mp3_files()
        return self.merge_mp3_files()


# Exemplo de utilização
if __name__ == "__main__":
    maker = PDF2Audiobook(
        pdf_path="Homo Deus_bg.pdf",
        voice=PDF2Audiobook.VOICE_BG_F,
        output_dir="output",
        max_chars=4000,
        rate="-11%",
    )
    maker.run()
