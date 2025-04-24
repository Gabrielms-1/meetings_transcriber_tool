import json
import logging
from contextlib import asynccontextmanager
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
import torch
import uvicorn
import asyncio
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger() 

log_dir = "/home/ubuntu/meetings_transcriber_tool/logs" 
os.makedirs(log_dir, exist_ok=True)
error_log_file = os.path.join(log_dir, "api_execution_errors.log")
file_handler = logging.FileHandler(error_log_file)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

lock = asyncio.Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_name = "Qwen2.5-7B-Instruct-AWQ"
    #model_path = f"/home/ubuntu/hf_models/"
    model_path = f"Qwen/Qwen2.5-7B-Instruct-AWQ"
    logging.info(f"Loading model from {model_path}")
    app.state.model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype="auto",
        device_map="auto",
        # local_files_only=True,
        low_cpu_mem_usage=True
    ).eval()
    logging.info("Model loaded successfully")
    app.state.tokenizer = AutoTokenizer.from_pretrained(model_path)
    logging.info("Tokenizer loaded successfully")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health(): 
    return {"status": "ok"}

@app.post("/summarize")
async def infer(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=415, detail="Only .json files are supported")

    content = await file.read()
    try:
        dialogue = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    logging.info("Starting summarization...")
    prompt = (
        "You are a helpful assistant that summarizes and organizes a conversation. "
        "The conversation is separated by the turns of each participant, separated by Speaker letters (A, B, C, etc.).\n\n"
        + json.dumps(dialogue, ensure_ascii=False, indent=2)
        + "\n\nPlease generate a long text in markdown that synthesizes and organizes this conversation. "
        "Explain what happened, decisions made, and then a paragraph with next steps."
    )

    inputs = app.state.tokenizer(prompt, return_tensors="pt").to(app.state.model.device)

    async def generate_stream():
        try:
            async with lock:
                with torch.inference_mode():
                    for output in app.state.model.generate(
                        **inputs,
                        max_new_tokens=1024,
                        temperature=0.7,
                        do_sample=True,
                        stream=True
                    ):
                        text = app.state.tokenizer.decode(output, skip_special_tokens=True)
                        yield text
        except Exception as e:
            logging.error(f"Error during streaming generation: {e}", exc_info=True)
            yield "\n\n**Error during inference**"

    return StreamingResponse(generate_stream(), media_type="text/plain")

if __name__ == "__main__":
    logging.info("Starting server...")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
