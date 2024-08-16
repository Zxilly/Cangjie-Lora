# 仓颉 Lora

基于 Qwen2-Instruct 的仓颉语言 Lora，基于标准库文档和 Cangjie-TPC 代码训练。

[Lora](https://huggingface.co/Zxilly/qwen2-cangjie-lora)

[完整模型](https://huggingface.co/Zxilly/qwen2-cangjie)

[Q5_K_M GGUF量化](https://huggingface.co/Zxilly/qwen2-cangjie-Q5_K_M-GGUF)

[Ollama 模型](https://ollama.com/Zxilly/qwen2-cangjie)

## 使用方式

### Ollama

```bash
ollama run Zxilly/qwen2-cangjie
```

### llama.cpp

#### Cli

```bash
llama-cli --hf-repo Zxilly/qwen2-cangjie-Q5_K_M-GGUF --hf-file qwen2-cangjie-q5_k_m.gguf -p "用仓颉写一个 Hello World"
```

#### Server

```bash
llama-server --hf-repo Zxilly/qwen2-cangjie-Q5_K_M-GGUF --hf-file qwen2-cangjie-q5_k_m.gguf -c 2048
```