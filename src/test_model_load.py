"""测试模型加载脚本"""
import sys
import traceback
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

MODEL_PATH = "./train/models/saved_full_model_7b"

print("=" * 60)
print("测试模型加载")
print("=" * 60)

print(f"\n模型路径: {MODEL_PATH}")
print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 可用: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

try:
    print("\n[1/2] 加载模型 (这可能需要几分钟)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        device_map="auto",
        dtype=torch.float16,
        low_cpu_mem_usage=True
    )
    print("✓ 模型加载成功")
    
    print("\n[2/2] 加载 Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    print("✓ Tokenizer 加载成功")
    
    print("\n" + "=" * 60)
    print("所有组件加载成功！")
    print("=" * 60)
    
    # 测试推理
    print("\n测试推理...")
    input_text = "你好"
    inputs = tokenizer(input_text, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=20)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"输入: {input_text}")
    print(f"输出: {result}")
    
except Exception as e:
    print(f"\n✗ 加载失败: {e}")
    traceback.print_exc()
    sys.exit(1)
