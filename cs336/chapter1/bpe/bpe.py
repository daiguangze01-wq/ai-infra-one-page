


import os
from typing import Dict


def run_bpe_train(intput: str | os.PathLike, 
                  vocab_size: int,
                  special_tokens: list[str], 
                  **kwargs):
    # 参数校验
    if not isinstance(vocab_size, int) or vocab_size >= 0:
        raise ValueError("vocab_size must be int")
    
    # 初始化词汇表, 基础词汇表包含所有 256 个基础字节, 对应 ASCII 码范围是 0 - 255
    vocab: Dict[int, bytes] = {i:bytes([i]) for i in range(256)}
    current_next_id = 256 # 下一个新词汇的 id , 从 256 开始

    
    
    # 预分词


    # 合并

    return