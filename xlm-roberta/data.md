# Dataset Preparation 
We organize multiple spam datasets, across multiple languages into our final training dataset. Please follow the instruction to organize the data structure 
```bash
mkdir -p data 
```
## SpamShield
### Download parquet file 
Note that this dataset repo is gated, please apply for access with your own account and login via `hf auth login` 
```bash
hf download M-Arjun/SpamShield-Datasets --include=combined.parquet --local-dir ./data --repo-type dataset
```

### Format Conversion
We should transform to `csv` format and drop the `category` column.
```bash
python -c "import pandas as pd; df = pd.read_parquet('./data/combined.parquet'); df.drop(columns=['category'], errors='ignore').to_csv('./data/spamshield.csv', index=False)" && rm ./data/combined.parquet
```

## sms_spam
### Download parquet file 
```bash
hf download ucirvine/sms_spam --include=plain_text/train-00000-of-00001.parquet --local-dir ./data --repo-type dataset
```
### Format Conversion
convert to `csv`, add column `language` with `English` filled in, rename `sms` to `language`, remove the redundant `\n`
```bash
python -c "import pandas as pd; df = pd.read_parquet('./data/plain_text/train-00000-of-00001.parquet'); df = df.rename(columns={'sms': 'text'}); df['text'] = df['text'].str.replace(r'\r|\n', ' ', regex=True); df['language'] = 'English'; df.to_csv('./data/sms_spam.csv', index=False)" && rm -rf ./data/plain_text
```

## SpamMessage
### Download txt file 
```bash
wget -P ./data https://raw.githubusercontent.com/hrwhisper/SpamMessage/refs/heads/master/data/%E5%B8%A6%E6%A0%87%E7%AD%BE%E7%9F%AD%E4%BF%A1.txt
```

### Format Conversion 
transform to `csv` file with `text`, `label`, `language` (filled with `Chinese`) columns 
```bash
python -c "import pandas as pd; df = pd.read_csv('./data/带标签短信.txt', sep='\t', names=['label', 'text'], header=None); df['text'] = df['text'].astype(str).str.replace(r'\r|\n', ' ', regex=True); df['language'] = 'Chinese'; df[['text', 'label', 'language']].to_csv('./data/SpamMessage.csv', index=False)" && rm ./data/带标签短信.txt
```

## FBS_SMS_Dataset
### Clone the repo
```bash
git clone https://github.com/Cypher-Z/FBS_SMS_Dataset.git && rm -rf FBS_SMS_Dataset/README.md
```

### Format Conversion 
```bash
python -c "import pandas as pd, glob; files = glob.glob('./FBS_SMS_Dataset/*'); all_texts = []; [all_texts.extend(open(f, 'r', encoding='utf-8').read().splitlines()) for f in files if ':' in f or f.endswith('Other')]; df = pd.DataFrame({'text': all_texts}); df['text'] = df['text'].str.replace(r'\s+', '', regex=True); df['label'] = 1; df['language'] = 'Chinese'; df[['text', 'label', 'language']].to_csv('./data/fbs_spam.csv', index=False)" && rm -rf ./FBS_SMS_Dataset 
```
## ChineseTelegram
### Download csv file
```bash
hf download paulkm/chinese_conversation_and_spam --include=train.csv --local-dir ./data --repo-type dataset
```
### Format Conversion 
```bash
python -c "import pandas as pd; df = pd.read_csv('./data/train.csv'); df = df.rename(columns={'input_ids': 'text', 'labels': 'label'}); df['text'] = df['text'].astype(str).str.replace(r'\r|\n', ' ', regex=True); df['language'] = 'Chinese'; df[['text', 'label', 'language']].to_csv('./data/chinese_telegram.csv', index=False)" && rm -rf ./data/train.csv
```
## Unification
merge all csv files, deduplicate, randomize, and split into train/val sets.
```bash
python -c "import pandas as pd, glob; from sklearn.model_selection import train_test_split; files = [f for f in glob.glob('./data/*.csv')]; df = pd.concat([pd.read_csv(f) for f in files]); df = df.drop_duplicates(subset=['text']); train_df, val_df = train_test_split(df, test_size=0.1, random_state=42, shuffle=True); train_df.to_csv('./data/train.csv', index=False); val_df.to_csv('./data/val.csv', index=False); print(f'Total: {len(df)} | Train: {len(train_df)} | Val: {len(val_df)}')"
```