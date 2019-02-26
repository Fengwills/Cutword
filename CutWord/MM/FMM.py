#正向最大匹配分词（FMM）
import sys

word_dict = ['新华网', '东京', '记者', '吴谷丰', '日本共同社', '28', '报道']
test_str = ' 新华网东京电机车吴谷丰据日本共同社28日报道'
#获取分词
def getSeg(text):
    if not text:
        return ''
    if len(text)==1:
        return text
    if text in word_dict:
        return text
    else:
        small = len(text)-1
        text = text[0:small]
        return getSeg(text)
def main():
    global test_str
    test_str  = test_str.strip()
    max_len = 5 #正向最大匹配分词测试，最大长度
    result_str=''#保存要输出的分词结果
    result_len = 0
    print('input:',test_str)
    while test_str:
        tmp_str = test_str[0:max_len]
        seg_str = getSeg(tmp_str)
        seg_len = len(seg_str)
        result_len = result_len + seg_len
        if seg_str.strip():
            result_str = result_str + seg_str+'/'
        test_str = test_str[seg_len:]
    print('output:',result_str)
if __name__ == '__main__':
    main()