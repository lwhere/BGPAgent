import vllm
from vllm import LLM
from vllm import LLM, SamplingParams

prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
#/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3.1-8B-Instruct
#/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3___1-70B-Instruct
llm = LLM(
    worker_use_ray=True,
    model="/root/autodl-tmp/ms-cache/hub/LLM-Research/Meta-Llama-3___1-70B-Instruct",
    trust_remote_code=True,
    tensor_parallel_size=4,
    dtype="half",
    gpu_memory_utilization=0.9,
    max_model_len=4096
)

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")