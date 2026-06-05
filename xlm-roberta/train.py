import yaml
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from datasets import load_dataset
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import argparse 
import os 

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='binary')
    acc = accuracy_score(labels, predictions)
    return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to the config file.")
    parser.add_argument("--train_data", type=str, required=True, help="Path to the training data file.")
    parser.add_argument("--val_data", type=str, required=True, help="Path to the validation data file.")
    parser.add_argument("--output_dir", type=str, default='./outputs', help="Directory to save the trained model.")
    args = parser.parse_args()
    
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    max_length = config["tokenizer"]["max_length"]
    config["training"]["output_dir"] = args.output_dir
    os.makedirs(args.output_dir, exist_ok=True)
    
    dataset = load_dataset(
        "csv",
        data_files={
            "train": args.train_data,
            "validation": args.val_data
        }
    )
    
    tokenizer = AutoTokenizer.from_pretrained(config["model"]["name"])
    model = AutoModelForSequenceClassification.from_pretrained(
        config["model"]["name"],
        num_labels=config["model"]["num_labels"],
        id2label=config["model"]["id2label"],
        label2id={v: k for k, v in config["model"]["id2label"].items()}
    )
    
    def tokenize(examples):
        texts = examples["text"]
        items = list(texts)
        items = [str(item) for item in items]
        return tokenizer(
            items,
            truncation=True,
            padding="max_length",
            max_length=max_length
        )
    
    dataset = dataset.map(tokenize, batched=True)
    
    
    training_args = TrainingArguments(**config["training"])
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        compute_metrics=compute_metrics,
    )
    
    trainer.train()
    
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

if __name__ == "__main__":
    main()