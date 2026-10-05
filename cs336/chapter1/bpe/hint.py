
# 在 Python 中，字符串以 Unicode 形式存储。每个字符对应一个唯一的码点（code point），可以通过 ord() 函数获取其整数值
print(ord("s")) # 115
print(ord("牛")) # 29275

# 使用 chr() 函数将整数转换为对应的 Unicode 字符
print(chr(115)) # s

# 为了文本转换成字节序列， 我们需要使用到 utf-8 编码
print("你好".encode("utf-8")) # b'xe4\xbd\x93\xe5\x9b\xbd'


# 尽管 Unicode 标准为每个字符定义了唯一的代码点（即一个整数），但直接在 Unicode 代码点上训练分词器并不可行。主要原因有两个：一是 Unicode 字符总数庞大（目前已定义的字符超过 15 万个），导致词汇表规模过大；二是大多数字符在实际文本中极为罕见，造成词汇表高度稀疏，不利于模型学习和泛化。
# 为解决这一问题，我们转而使用 Unicode 编码方案 将文本转换为字节序列，并在字节级别上构建分词器。Unicode 定义了多种编码格式，其中最常用的是 UTF-8、UTF-16 和 UTF-32。在这些编码中，UTF-8 是当前互联网上最主流的编码方式，据估计超过 98% 的网页都采用 UTF-8。
# UTF-8 的一个重要特性是：它将每个 Unicode 字符编码为 1 到 4 个字节的序列（对于基本 ASCII 字符仅用 1 字节，而中文、表情符号等则使用 3 或 4 字节），兼容 ASCII 且可变长，高效且广泛支持。

test_string = "hello, guangze"
utf8_encoded = test_string.encode("utf-8")
print(utf8_encoded)
print(type(utf8_encoded))

# 拆解字节值 （0-255 整数值）
list(utf8_encoded)
# 验证可逆性
print(len(utf8_encoded),len(test_string))
print(utf8_encoded.decode("utf-8")) # hello, guangze



# 问题
# Q: 为什么我们倾向于在 UTF-8 编码的字节上训练分词器， 而不是 UTF-16 或 UTF-32 ?  比较这些编码对不同输入字符串的输出可能有所帮助。
def decode_uft8_bytes_to_str_wrong(bytestring: bytes):
    return "".join([bytes([b]).decode("utf-8") for b in bytestring])

# 上文提到过, python 存储字符串使用的是 unicode 编码, 使用 unicode 编码进行 utf-8 解码, 会导致错误
# decode_uft8_bytes_to_str_wrong("coffee")  # 崩  TypeError: 'str' object cannot be interpreted as an integer
print(decode_uft8_bytes_to_str_wrong("hello".encode("utf-8")))  

# 虽然字节级标记化能够有效缓解单词级标记器面临的词汇表外问题，但将文本分解为单个字节会导致输入序列过长。例如，一个包含10个单词的句子在单词级模型中可能仅对应10个标记，而在字节级模型中却可能膨胀至50个甚至更多标记，具体取决于单词长度。这种扩展显著增加了模型每一步的计算量，拖慢训练速度。同时，过长的序列也给语言建模带来挑战，因为它在数据中引入了更复杂的长期依赖关系。
# 子字标记化（subword tokenization）则介于单词级和字节级之间，提供了一种折中方案。与仅有256个条目的字节级词汇表不同，子词标记器通过扩大词汇量来更高效地压缩原始字节序列。其核心思想是：如果某些字节序列（如 b'the'）在训练数据中频繁出现，就将其合并为一个单独的标记，从而将原本多个字节组成的序列压缩为一个单元。这样既能保持对罕见词和未知词的处理能力，又能显著缩短平均序列长度。
# 如何选择这些子词单元？Sennrich 等人（2016）提出采用字节对编码（Byte Pair Encoding, BPE），这是一种源自数据压缩技术的算法。BPE 通过迭代地查找并合并出现频率最高的相邻字节对，逐步构建出一组高效的子词单元。每次合并都会引入一个新的符号来代表该字节对，并将其加入词汇表。这一过程持续进行，直到达到预设的词汇表大小。由于BPE优先合并高频模式，因此最终的词汇表能最大程度地提升整体压缩效率——常见词或词片段更可能被表示为单一标记。
# 在本任务中，我们将实现一种基于字节的BPE分词器，其词汇项由原始字节及其合并后的序列表示。这种方法结合了字节级分词器的鲁棒性与子词级的高效性，在处理未登录词的同时保持合理的序列长度。整个构建词汇表的过程也被称为“训练”BPE分词器，是实现高效文本表示的关键步骤。
