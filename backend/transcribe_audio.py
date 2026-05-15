import whisper
import os

model = whisper.load_model("base")

audio_dir = "./app/dataset/listening/audio"
output_dir = "./app/dataset/listening/transcript"

os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(audio_dir):

    if file.endswith(".mp3"):

        audio_path = os.path.join(
            audio_dir,
            file
        )

        print(f"Transcribing {file}...")

        result = model.transcribe(
            audio_path
        )

        transcript = result["text"]

        txt_name = file.replace(
            ".mp3",
            ".txt"
        )

        txt_path = os.path.join(
            output_dir,
            txt_name
        )

        with open(
            txt_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(transcript)

        print(f"Saved: {txt_name}")

print("All audio transcribed!")