# 仓颉 Lora

仓颉语言 Lora，基于标准库文档和 Cangjie-TPC 代码训练。

> 建议使用 InternLM2.5 版本

## 基于 InternLM2.5-7B-Chat

[Lora](https://github.com/Zxilly/Cangjie-Lora/releases/tag/Lora-3)

[完整模型](https://huggingface.co/Zxilly/intern2_5-cangjie)

[Q5_K_M GGUF量化](https://huggingface.co/Zxilly/intern2_5-cangjie-Q5_K_M-GGUF)

[Ollama 模型](https://ollama.com/Zxilly/intern2_5-cangjie)

## 基于 Qwen2-7B-Instruct

[Lora](https://github.com/Zxilly/Cangjie-Lora/releases/tag/Lora-2)

[完整模型](https://huggingface.co/Zxilly/qwen2-cangjie)

[Q5_K_M GGUF量化](https://huggingface.co/Zxilly/qwen2-cangjie-Q5_K_M-GGUF)

[Ollama 模型](https://ollama.com/Zxilly/qwen2-cangjie)

## 使用方式

### Ollama

```bash
ollama run Zxilly/intern2_5-cangjie
```

### llama.cpp

#### Cli

```bash
llama-cli --hf-repo Zxilly/intern2_5-cangjie-Q5_K_M-GGUF --hf-file intern2_5-cangjie-q5_k_m.gguf -p "用仓颉写一个 Hello World"
```

#### Server

```bash
llama-server --hf-repo Zxilly/intern2_5-cangjie-Q5_K_M-GGUF --hf-file intern2_5-cangjie-q5_k_m.gguf -c 2048
```