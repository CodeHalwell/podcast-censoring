import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset, Dataset # type: ignore


device: str = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype: torch.dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id: str = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

dataset: Dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
sample: dict = dataset[0]["audio"]

result: dict = pipe(sample, return_timestamps=True, language='en')
print(result["text"])







