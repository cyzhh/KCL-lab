import os
from tqdm import tqdm

data = []
sentences = []

directory_path = "/data/Chem_PretrainedData/version_3/"

# with open("/data/Chem_PretrainedData/version_3/converted_output-2.txt",encoding="utf-8") as file:  
    # data = file.read().split("\n")
    
for filename in tqdm(os.listdir(directory_path), desc="Reading Files", unit="file"):
    file_path = os.path.join(directory_path, filename)

    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().split("\n")
            data.extend(content)
``
if data and data[-1] == '':
    data.pop()

with tqdm(total=len(data), desc="Processing Sentences", unit="sentence") as pbar:
    for row in data:
        row = row.strip()
        sentences.append(row)
        pbar.update(1)

# 将处理后的句子写入文件
with open("datasets/train_data.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(sentences))
    
