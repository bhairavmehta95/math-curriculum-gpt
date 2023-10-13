from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GenerationConfig,
    GPTNeoConfig,
    GPTNeoModel,
)


import os
from tqdm import tqdm
import numpy as np
import tiktoken
from datasets import Dataset, load_dataset  # huggingface datasets
import pandas as pd

configuration = GPTNeoConfig(
    **{
        "lr": 5e-4,
        "lr_schedule": "constant",
        "wd": 0.1,
        "adam_beta1": 0.9,
        "adam_beta2": 0.95,
        "context_length": 512,
        "batch_size": 80,
        "gradient_accumulation_steps": 16,
    }
)

# Initializing a model (with random weights) from the EleutherAI/gpt-neo-1.3B style configuration
model = GPTNeoModel(configuration)

tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")

df = pd.read_csv("data/early_math/tiny_math.csv")
dataset = Dataset.from_pandas(df)

textbooks = "\n\n".join(dataset["text"])
print(len(textbooks))
x = tokenizer(textbooks, return_tensors="pt")
print(x)

#     enc = tiktoken.get_encoding("gpt2")
#     total_tokens = 0
#     for name, textbook in zip(dataset["textbook"], dataset["text"]):
#         total_tokens += len(enc.encode_ordinary(textbook))
#         print(name, len(textbook))

#     print(total_tokens)

# prompts = prompt.split("\n\n")
# print([len(p) for p in prompts])

# input_ids = tokenizer.encode(prompt, return_tensors="pt")
# print(input_ids.shape)
