import torch
import warnings
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import os

# Suppress specific warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

def setup_device_and_dtype():
    """Setup device and torch dtype based on available hardware."""
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    print(f"Device set to use {device}")
    return device, torch_dtype

def load_whisper_model(model_id: str = "openai/whisper-large-v3"):
    """Load and setup Whisper model and processor."""
    device, torch_dtype = setup_device_and_dtype()
    
    print(f"Loading model: {model_id}")
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, 
        torch_dtype=torch_dtype, 
        low_cpu_mem_usage=True, 
        use_safetensors=True
    )
    model.to(device)
    
    processor = AutoProcessor.from_pretrained(model_id)
    
    # Create pipeline with improved parameters
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True,  # Move this to pipeline creation
    )
    
    return pipe

def transcribe_audio(pipe, audio_file: str, language: str | None = None):
    """Transcribe audio file with optional language specification."""
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    
    print(f"Transcribing: {audio_file}")
    
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
        result = pipe(audio_file, generate_kwargs=generate_kwargs)
        return result
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

def main():
    """Main transcription function."""
    audio_file = 'downloaded_audio.wav'
    
    # Load model and create pipeline
    pipe = load_whisper_model()
    
    result = transcribe_audio(pipe, audio_file, language='en')
    
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

if __name__ == "__main__":
    main()
