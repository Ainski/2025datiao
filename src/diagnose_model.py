"""诊断模型加载问题"""
import os
import torch
from transformers import AutoConfig

MODEL_PATH = "./train/models/saved_full_model_7b"

print("=" * 60)
print("模型诊断工具")
print("=" * 60)

# 1. 检查文件
print(f"\n[1] 检查模型文件...")
files = os.listdir(MODEL_PATH)
print(f"模型目录内容: {files}")

# 检查模型文件大小
model_file = os.path.join(MODEL_PATH, "model.safetensors")
if os.path.exists(model_file):
    size_gb = os.path.getsize(model_file) / 1024**3
    print(f"model.safetensors 大小: {size_gb:.2f} GB")
else:
    print("错误: model.safetensors 不存在!")

# 2. 检查配置
print(f"\n[2] 检查模型配置...")
try:
    config = AutoConfig.from_pretrained(MODEL_PATH)
    print(f"模型类型: {config.model_type}")
    print(f"架构: {config.architectures}")
    print(f"配置 dtype: {getattr(config, 'torch_dtype', 'N/A')}")
except Exception as e:
    print(f"配置加载失败: {e}")

# 3. 检查 PyTorch 和 CUDA
print(f"\n[3] 环境信息...")
print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# 4. 尝试只加载配置和 tokenizer
print(f"\n[4] 测试 Tokenizer 加载...")
try:
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    print("✓ Tokenizer 加载成功")
except Exception as e:
    print(f"✗ Tokenizer 加载失败: {e}")

# 5. 尝试用不同方式加载模型
print(f"\n[5] 尝试用 CPU 加载（测试模型文件是否完整）...")
try:
    from transformers import AutoModelForCausalLM
    print("开始加载 (使用 CPU)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        device_map="cpu",
        dtype=torch.float32,
        low_cpu_mem_usage=True
    )
    print("✓ CPU 加载成功!")
except Exception as e:
    print(f"✗ CPU 加载失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
