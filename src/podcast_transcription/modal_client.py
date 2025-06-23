"""
Modal cloud integration for podcast transcription using H100 GPUs and Whisper-large-v3.
"""

import modal

cuda_version = "12.4.0"  # should be no greater than host CUDA version
flavor = "devel"  #  includes full CUDA toolkit
operating_sys = "ubuntu22.04"
tag = f"{cuda_version}-{flavor}-{operating_sys}"

image = (
    modal.Image.from_registry(f"nvidia/cuda:{tag}", add_python="3.11")
    .apt_install(
        "git",
        "ffmpeg",
    )
    .pip_install(
        "torch>=2.1.0",
        "torchaudio>=2.1.0", 
        "numpy<2.0",
        index_url="https://download.pytorch.org/whl/cu121",
    )
    .pip_install(
        "transformers",
        "ffmpeg-python",
    )
)
app = modal.App("example-base-whisper", image=image)

GPU_CONFIG = "H100"

CACHE_DIR = "/cache"
cache_vol = modal.Volume.from_name("whisper-cache", create_if_missing=True)

@app.cls(
    gpu=GPU_CONFIG,
    volumes={CACHE_DIR: cache_vol},
    scaledown_window=60 * 2,   # Scale down after 2 minutes (faster resource release)
    timeout=60 * 60,           # Max 1 hour per task
)
@modal.concurrent(max_inputs=15)
class Model:
    @modal.enter()
    def setup(self):
        import torch
        import warnings
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

        # Suppress specific warnings for cleaner output
        warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        model_id = "openai/whisper-large-v3"
        
        print(f"Loading model: {model_id}")
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, 
            torch_dtype=torch_dtype, 
            low_cpu_mem_usage=True, 
            use_safetensors=True,
            cache_dir=CACHE_DIR
        )
        model.to(device)
        
        processor = AutoProcessor.from_pretrained(model_id, cache_dir=CACHE_DIR)
        
        # Create pipeline with improved parameters
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
            return_timestamps=True,
        )

    @modal.method()
    def transcribe(self, audio_url: str, language: str | None = None):
        import requests # type: ignore
        import os

        response = requests.get(audio_url)
        # Save the audio file locally
        with open("downloaded_audio.wav", "wb") as audio_file:
            audio_file.write(response.content)

        if not os.path.exists("downloaded_audio.wav"):
            raise FileNotFoundError("Audio file not found: downloaded_audio.wav")
        
        print(f"Transcribing: downloaded_audio.wav")
        
        # Prepare generation kwargs to avoid conflicts with forced_decoder_ids
        generate_kwargs = {
            "task": "transcribe",  # Explicitly set task
        }
        
        if language:
            generate_kwargs["language"] = language
            # Clear any forced_decoder_ids to avoid conflicts
            generate_kwargs["forced_decoder_ids"] = None  # type: ignore
            print(f"Using language: {language}")
        else:
            print("Using automatic language detection")
        
        try:
            # Call pipeline with proper parameters
            result = self.pipe("downloaded_audio.wav", generate_kwargs=generate_kwargs)
            return result
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            return None


# ## Run the model
@app.local_entrypoint()
def main():
    url = "https://pub-ebe9e51393584bf5b5bea84a67b343c2.r2.dev/examples_english_english.wav"

    result = Model().transcribe.remote(url, language='en')
    
    if result:
        print("\n" + "="*50)
        print("TRANSCRIPTION RESULT:")
        print("="*50)
        print(result["text"])
        
        # Print timestamps if available
        if "chunks" in result and result["chunks"]:
            print("\n" + "="*50)
            print("TIMESTAMPED SEGMENTS:")
            print("="*50)
            for chunk in result["chunks"]:
                timestamp = chunk.get("timestamp", "N/A")
                text = chunk.get("text", "")
                print(f"[{timestamp}] {text}")
    else:
        print("Transcription failed.") 