# Installation 
1. Create a conda environment with `PyTorch` support. The codebase was tested with `torch2.6.0+cuda12.4`
```bash
conda create -n spam python=3.10
conda activate spam
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
```

2. Install other dependencies
```bash
pip install transformers datasets scikit-learn accelerate tensorboard tensorboardX pkg_resources
```

# Training 
```bash
bash scripts/train.sh 
```
The training process is tested on 4 `NVIDIA H100` GPUs, taking about two hours 

# Inference 
```bash
python inference.py --model_path <> --text <>
```
`model_path` can be either your local checkpoint (`./outputs/xlm-roberta-base`) or our pretrained model (`kudouKID/mroberta-spam-v2`)
