import sentencepiece as spm

if __name__ == "__main__":
    ### 加载模型
    model_path = "vs128k_msl30.model"
    tokenizer = spm.SentencePieceProcessor()
    tokenizer.load(model_path)

    paths = [
        '/data/Chem_PretrainedData/version_3/converted_output-2.txt',
        '/data/Chem_PretrainedData/version_3/converted_output-6.txt'
    ]

    for path in paths:
        lines = []
        with open(path, 'r') as file:
            for i in range(10000): 
                line = file.readline()
                if not line:
                    break
                lines.append(line.strip())

        text = '\n'.join(lines)

        ### 计算byte数量和token数量
        byte_text = text.encode()
        num_bytes = len(byte_text)
        tokens = tokenizer.encode_as_pieces(text)
        num_tokens = len(tokens)

        ### 计算压缩率
        compression_rate = num_bytes / num_tokens
        print(f"压缩率: {compression_rate}")