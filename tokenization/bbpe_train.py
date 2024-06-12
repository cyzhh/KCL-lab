from bbpe import BBPETokenizer

# 读取训练文件
with open("datasets/train_data.txt", "r", encoding="utf-8") as f:
    data = f.read()
# 训练模型
vocab_size = 32000  # 词表大小
vocab_outfile = "32k.json"  # 保存词表文件名
merges_outfile = "merges_32k.txt"  # 保存合并字节的词表)
BBPETokenizer.train_tokenizer(data, vocab_size, vocab_outfile=vocab_outfile, merges_outfile=merges_outfile)