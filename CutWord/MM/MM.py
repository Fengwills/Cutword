from config import test_data_path
from config import test_result_path
from config import Punctuation
from config import Number
from config import English
from config import train_data_path
from config import span
import math
word_dict=set()
def load_dict():
    file = open('dic.txt',encoding='utf-8')
    try:
        for line in file:
            word_dict.add(line.rstrip('\n'))
    finally:
        file.close()

test_str='扬帆远东做与中国合作的先行'
max_len=12 #最长词条字符数
class Prepostgram():
    def __init__(self):
        self._WordDict={}
        self._NextDict={}
        self._wordsize=0#词典大小
        self._nextsize=0#nextdict大小
    def Training(self):
        train_file = open(train_data_path,encoding='utf-8')
        self._NextDict['BEG']={}
        trainsize=0
        for line in train_file:
            line = line.strip()
            line = line.split(' ')
            linelist=[]
            for word in line:
                if word not in Punctuation:
                    linelist.append(word)

            trainsize=len(linelist)
            for pos,word in enumerate(linelist):
                if word not in self._WordDict:
                    self._WordDict[word]=1
                else:
                    self._WordDict[word]+=1
                word1,word2='',''
                if pos==0:
                    word1,word2='<BEG>',word
                elif pos==len(linelist)-1:
                    word1,word2=word,'<END>'
                else:
                    word1,word2=word,linelist[pos+1]

                if word1 not in self._NextDict:
                    self._NextDict[word1]={}
                elif word2 not in self._NextDict[word1]:
                    self._NextDict[word1][word2]=1
                else:
                    self._NextDict[word1][word2]+=1
        print("train done...")
        print("total train data length"+str(trainsize))
        self._wordsize=len(self._WordDict)
        self._nextsize=len(self._NextDict)
        print("word dict size"+str(self._wordsize))
        print("next word dict size"+str(self._nextsize))
    def CalSegProbability(self,ParseList):
        p = 0
        # 由于概率很小，对连乘做了取对数处理转化为加法
        for pos, words in enumerate(ParseList):
            if pos < len(ParseList) - 1:
                # 乘以后面词的条件概率
                word1, word2 = words, ParseList[pos + 1]
                # if not self._NextDict.has_key(word1):
                if word1 not in self._NextDict:
                    # 加1平滑
                    p += math.log(1.0 / self._nextsize)
                else:
                    # 加1平滑
                    fenzi, fenmu = 1.0, self._nextsize
                    for key in self._NextDict[word1]:
                        if key == word2:
                            fenzi += self._NextDict[word1][word2]
                        fenmu += self._NextDict[word1][key]
                    p += math.log((fenzi / fenmu))
            # 乘以第一个词的概率
            if (pos == 0 and words != u'<BEG>') or (pos == 1 and ParseList[0] == u'<BEG>'):
                # if self._WordDict.has_key(words):
                if words in self._WordDict:
                    p += math.log(float(self._WordDict[words]) + 1 / self._wordsize + self._nextsize)
                else:
                    # 加1平滑
                    p += math.log(1 / self._wordsize + self._nextsize)
        return p
    def BigramSeg(self,test_str):
        ParseList1 = MMsegMain(test_str)
        ParseList2 = RMMSegMain(test_str)
        ParseList1.insert(0, u'<BEG>')
        ParseList1.append(u'<END>')
        ParseList2.insert(0, u'<BEG>')
        ParseList2.append(u'<END>')
        # 根据前向最大匹配和后向最大匹配得到得到句子的两个词序列（添加BEG和END作为句子的开始和结束）

        # 记录最终选择后拼接得到的句子
        ParseList = []

        # CalList1和CalList2分别记录两个句子词序列不同的部分
        CalList1 = []
        CalList2 = []

        # pos1和pos2记录两个句子的当前字的位置，cur1和cur2记录两个句子的第几个词
        pos1 = pos2 = 0
        cur1 = cur2 = 0
        while (1):
            if cur1 == len(ParseList1) and cur2 == len(ParseList2):
                break
            # 如果当前位置一样
            if pos1 == pos2:
                # 当前位置一样，并且词也一样
                if len(ParseList1[cur1]) == len(ParseList2[cur2]):
                    pos1 += len(ParseList1[cur1])
                    pos2 += len(ParseList2[cur2])
                    # 说明此时得到两个不同的词序列，根据bigram选择概率大的
                    # 注意算不同的时候要考虑加上前面一个词和后面一个词，拼接的时候再去掉即可
                    if len(CalList1) > 0:
                        CalList1.insert(0, ParseList[-1])
                        CalList2.insert(0, ParseList[-1])
                        # if cur1 < len(ParseList1) - 1:
                        if cur1 < len(ParseList1):
                            CalList1.append(ParseList1[cur1])
                            CalList2.append(ParseList2[cur2])

                        p1 = self.CalSegProbability(self,CalList1)
                        p2 = self.CalSegProbability(self,CalList2)
                        if p1 > p2:
                            CalList = CalList1
                        else:
                            CalList = CalList2
                        CalList.remove(CalList[0])
                        # if cur1 < len(ParseList1) - 1:
                        if cur1 < len(ParseList1):
                            CalList.remove(ParseList1[cur1])
                        for words in CalList:
                            ParseList.append(words)
                        CalList1 = []
                        CalList2 = []
                    ParseList.append(ParseList1[cur1])
                    cur1 += 1
                    cur2 += 1
                # pos1相同，len(ParseList1[cur1])不同，向后滑动，不同的添加到list中
                elif len(ParseList1[cur1]) > len(ParseList2[cur2]):
                    CalList2.append(ParseList2[cur2])
                    pos2 += len(ParseList2[cur2])
                    cur2 += 1
                else:
                    CalList1.append(ParseList1[cur1])
                    pos1 += len(ParseList1[cur1])
                    cur1 += 1
            else:
                # pos1不同，而结束的位置相同，两个同时向后滑动
                if pos1 + len(ParseList1[cur1]) == pos2 + len(ParseList2[cur2]):
                    CalList1.append(ParseList1[cur1])
                    CalList2.append(ParseList2[cur2])
                    pos1 += len(ParseList1[cur1])
                    pos2 += len(ParseList2[cur2])
                    cur1 += 1
                    cur2 += 1
                elif pos1 + len(ParseList1[cur1]) > pos2 + len(ParseList2[cur2]):
                    CalList2.append(ParseList2[cur2])
                    pos2 += len(ParseList2[cur2])
                    cur2 += 1
                else:
                    CalList1.append(ParseList1[cur1])
                    pos1 += len(ParseList1[cur1])
                    cur1 += 1
        ParseList.remove(u'<BEG>')
        ParseList.remove(u'<END>')
        return ParseList
    def SeparWords(self,mode):
        print("start separte words...")

        test_file = open(test_data_path, 'r', encoding='utf-8')
        result_file = open(test_result_path, 'w', encoding='utf-8')
        for line in test_file:
            SpecialDict = {}
            line = line.strip()
            Senlist = []
            flag = 0  # 判断数字和英文单词
            tmp_words = ''
            for sentence in line:
                if sentence in Number or sentence in English:
                    if tmp_words != '':
                        if flag == 0:
                            Senlist.append(tmp_words)
                            tmp_words = ''
                            flag = 1
                    else:
                        flag = 1
                    tmp_words += sentence
                elif sentence in Punctuation:
                    if flag == 1:
                        SpecialDict[tmp_words] = 1
                        Senlist.append(tmp_words)
                        Senlist.append(sentence)
                        flag = 0
                        tmp_words = ''
                    if tmp_words != '':
                        Senlist.append(tmp_words)
                        Senlist.append(sentence)
                    tmp_words = ''
                else:
                    if flag == 1:
                        SpecialDict[tmp_words] = 1
                        Senlist.append(tmp_words)
                        flag = 0
                        tmp_words = ''
                    tmp_words += sentence
            if (tmp_words != ''):
                Senlist.append(tmp_words)
            tmp_words = ''
            for sentence in Senlist:
                if sentence not in Punctuation and sentence not in SpecialDict:
                    if (mode == 'pre'):
                        result = MMsegMain(sentence)
                    if (mode == 'post'):
                        result = RMMSegMain(sentence)
                    else:
                        result =self.BigramSeg(sentence)
                    for word in result:
                        tmp_words += ' ' + word
                else:
                    tmp_words = tmp_words + ' ' + sentence
            result_file.write(tmp_words + '\n')
            tmp_words = ''
    def BigramSeg(self, test_str):
        ParseList1 = MMsegMain(test_str)
        ParseList2 = RMMSegMain(test_str)
        ParseList1.insert(0, u'<BEG>')
        ParseList1.append(u'<END>')
        ParseList2.insert(0, u'<BEG>')
        ParseList2.append(u'<END>')
        # 根据前向最大匹配和后向最大匹配得到得到句子的两个词序列（添加BEG和END作为句子的开始和结束）
        # 记录最终选择后拼接得到的句子
        ParseList = []
        # CalList1和CalList2分别记录两个句子词序列不同的部分
        CalList1 = []
        CalList2 = []
        # pos1和pos2记录两个句子的当前字的位置，cur1和cur2记录两个句子的第几个词
        pos1 = pos2 = 0
        cur1 = cur2 = 0
        while (1):
            if cur1 == len(ParseList1) and cur2 == len(ParseList2):
                break
            # 如果当前位置一样
            if pos1 == pos2:
                # 当前位置一样，并且词也一样
                if len(ParseList1[cur1]) == len(ParseList2[cur2]):
                    pos1 += len(ParseList1[cur1])
                    pos2 += len(ParseList2[cur2])
                    # 说明此时得到两个不同的词序列，根据bigram选择概率大的
                    # 注意算不同的时候要考虑加上前面一个词和后面一个词，拼接的时候再去掉即可
                    if len(CalList1) > 0:
                        CalList1.insert(0, ParseList[-1])
                        CalList2.insert(0, ParseList[-1])
                        # if cur1 < len(ParseList1) - 1:
                        if cur1 < len(ParseList1):
                            CalList1.append(ParseList1[cur1])
                            CalList2.append(ParseList2[cur2])
                        p1 = self.CalSegProbability(CalList1)
                        p2 = self.CalSegProbability(CalList2)
                        if p1 > p2:
                            CalList = CalList1
                        else:
                            CalList = CalList2
                        CalList.remove(CalList[0])
                        # if cur1 < len(ParseList1) - 1:
                        if cur1 < len(ParseList1):
                            CalList.remove(ParseList1[cur1])
                        for words in CalList:
                            ParseList.append(words)
                        CalList1 = []
                        CalList2 = []
                    ParseList.append(ParseList1[cur1])
                    cur1 += 1
                    cur2 += 1
                # pos1相同，len(ParseList1[cur1])不同，向后滑动，不同的添加到list中
                elif len(ParseList1[cur1]) > len(ParseList2[cur2]):
                    CalList2.append(ParseList2[cur2])
                    pos2 += len(ParseList2[cur2])
                    cur2 += 1
                else:
                    CalList1.append(ParseList1[cur1])
                    pos1 += len(ParseList1[cur1])
                    cur1 += 1
            else:
                # pos1不同，而结束的位置相同，两个同时向后滑动
                if pos1 + len(ParseList1[cur1]) == pos2 + len(ParseList2[cur2]):
                    CalList1.append(ParseList1[cur1])
                    CalList2.append(ParseList2[cur2])
                    pos1 += len(ParseList1[cur1])
                    pos2 += len(ParseList2[cur2])
                    cur1 += 1
                    cur2 += 1
                elif pos1 + len(ParseList1[cur1]) > pos2 + len(ParseList2[cur2]):
                    CalList2.append(ParseList2[cur2])
                    pos2 += len(ParseList2[cur2])
                    cur2 += 1
                else:
                    CalList1.append(ParseList1[cur1])
                    pos1 += len(ParseList1[cur1])
                    cur1 += 1
        ParseList.remove(u'<BEG>')
        ParseList.remove(u'<END>')
        return ParseList
def MMSeg(sen):
    if sen=='':
        return ''
    if len(sen)==1:
        return sen
    if sen in word_dict:
        return sen
    else :
        sen = sen[0:len(sen)-1]
        result = MMSeg(sen)
        return result
def MMsegMain(test_str):
    result=[]
    while(test_str):
        sen = test_str[0:max_len]
        r = MMSeg(sen)
        result.append(r)
        test_str = test_str[len(r):]
    return result
def RMMSeg(sen):
    if sen =='':
        return ''
    if len(sen)==1:
        return sen
    if sen in word_dict:
        return sen
    else:
        sen = sen[1:]
        result = RMMSeg(sen)
        return result
def RMMSegMain(test_str):
    result=[]
    while (test_str):
        if len(test_str)>max_len:
            sen = test_str[len(test_str) - max_len:]
        else:
            sen = test_str
        # print("sen: " + sen)
        r = RMMSeg(sen)
        result.append(r);
        test_str = test_str[0:len(test_str)-len(r)]
        # print("test: " + test_str)
    result.reverse()
    return result


def SeparWords(mode):
    print("start separte words...")

    test_file = open(test_data_path,'r',encoding='utf-8')
    result_file = open(test_result_path,'w',encoding='utf-8')
    for line in test_file:
        SpecialDict={}
        line = line.strip()
        Senlist = []
        flag = 0#判断数字和英文单词
        tmp_words=''
        for sentence in line:
            if sentence in Number or sentence in English:
                if tmp_words!='':
                    if flag==0:
                        Senlist.append(tmp_words)
                        tmp_words=''
                        flag=1
                else:
                    flag=1
                tmp_words += sentence
            elif sentence in Punctuation:
                if flag==1:
                    SpecialDict[tmp_words]=1
                    Senlist.append(tmp_words)
                    Senlist.append(sentence)
                    flag=0
                    tmp_words=''
                if tmp_words!='':
                    Senlist.append(tmp_words)
                    Senlist.append(sentence)
                tmp_words=''
            else:
                if flag==1:
                    SpecialDict[tmp_words]=1
                    Senlist.append(tmp_words)
                    flag=0
                    tmp_words=''
                tmp_words+=sentence
        if(tmp_words!=''):
            Senlist.append(tmp_words)
        tmp_words=''
        for sentence in Senlist:
            if sentence not in Punctuation and sentence not in SpecialDict:
                if(mode=='pre'):
                    result = MMsegMain(sentence)
                if(mode=='post'):
                    result = RMMSegMain(sentence)
                else:
                    result = BigramSeg(sentence)
                for word in result:
                    tmp_words += ' ' + word
            else:
                tmp_words=tmp_words+' '+sentence
        result_file.write(tmp_words+'\n')
        tmp_words=''
if __name__ == '__main__':
    # load_dict()
    p = Prepostgram()
    p.Training()
    word_dict=p._WordDict
    p.SeparWords('bigram')
