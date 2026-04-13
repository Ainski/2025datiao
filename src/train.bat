@echo off

if exist "./train/model/qwen_7b/config.json" (
    echo Model already exists. Skipping download.
) else (
    echo Downloading model...
    pip install modelscope
    modelscope download --model deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --local_dir ./train/model/qwen_7b
)

if /i "%~1"=="--eval-text" (
    python main.py --train --eval-text "%~2"
) else (
    python main.py --train
)