import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import argparse

def load_model(model_path, device: str = 'cuda'):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.to(device)
    model.eval()
    return tokenizer, model

def predict(text, model, tokenizer):
    device=model.device
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
        prediction = torch.argmax(probabilities, dim=-1).item()
    
    id2label = model.config.id2label
    label = id2label[prediction]
    score = probabilities[0][prediction].item()
    
    return label, score

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="./outputs/xlm-roberta-base", help="Path to the trained model.")
    parser.add_argument("--text", type=str, required=True, help="Text to classify.")
    args = parser.parse_args()
    
    tokenizer, model = load_model(args.model_path)
    label, score = predict(args.text, model, tokenizer)

    print(f'label: {label}, score: {score:.4f}')
if __name__ == "__main__":
    main()
