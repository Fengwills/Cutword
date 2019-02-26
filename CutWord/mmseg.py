#语料库处理之后的形式为 词语 词频
#例如 生活 2 ，这样方便插入字典树。

# -*- coding: UTF-8 -*-
# 打开一个文件
#coding:utf-8

import sys
import  codecs
import re
import math
from operator import itemgetter, attrgetter

#字典树部分
class trie:
    root={}
    END='/'

    def add(self,word,cnt):
        node=self.root
        for c in word:
            node=node.setdefault(c,{})
        node[self.END]=cnt

    def find(self,word):
        node=self.root
        for c in word:
            if(c not in node):
                return 0
            node=node[c]
        if(self.END in node):
            return int(node[self.END])
        return 0

#构建字典树部分
Trie=trie()
fin=codecs.open("处理后语料.txt","r","utf-8")
num=fin.readline()
num=int(num)
for i in range(0,num):
    s=fin.readline()
    a=s.split()
    k=a[0].encode('utf-8')
    v=int(a[1].encode('utf-8'))
    Trie.add(a[0],a[1])
fin.close()

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

#mmseg算法部分
while(True):
    tmp=input("请输入需要分词的句子:")
    if(tmp=="-MM"):
        break
    sentence=""
    for c in tmp:
        if(is_chinese(c)):
            sentence=sentence+c
    #候选词的类
    class candidate(object):
        length=0#总长度
        avelen=0#平均长度
        variance=0.0#方差
        lsum=0.0#单子频的自然对数集合
        num=0.0#词语数量
        words=[]

    candidates=[]
    Allwords=[]
    n = len(sentence)
    i=0;
    while(i<n):
        candidates=[]
        for j in range(i+1,n+1):
            #一个词
            a=sentence[i:j]
            x=Trie.find(a)
            if(x!=0):
                can = candidate()
                can.words=[]
                can.num=1
                can.words.append(a)
                can.length=j-i
                can.avelen=can.length
                can.variance=0.0
                if(len(a)==1):
                    can.lsum=math.log(x)
                candidates.append(can)
            for k in range(j+1,n+1):
                #两个词
                a = sentence[i:j]
                b = sentence[j:k]
                x = Trie.find(a)
                y = Trie.find(b)
                if ((x != 0 and y != 0 )):
                    can = candidate()
                    can.words = []
                    can.words.append(a)
                    can.words.append(b)
                    can.num=2
                    can.length = (k - i)
                    can.avelen = (len(a) + len(b)) / 2.0
                    can.variance = (len(a) - can.avelen) ** 2 + (len(b) - can.avelen) ** 2
                    can.lsum = 0
                    if (len(a) == 1):
                        can.lsum += math.log(x)
                    if (len(b) == 1):
                        can.lsum += math.log(y)
                    candidates.append(can)
                for l in range(k+1,n+1):
                    #三个词
                    a=sentence[i:j]
                    b=sentence[j:k]
                    c=sentence[k:l]
                    x=Trie.find(a)
                    y=Trie.find(b)
                    z=Trie.find(c)
                    if((x!=0 and y!=0 and z!=0)):
                        can=candidate()
                        can.words=[]
                        can.words.append(a)
                        can.words.append(b)
                        can.words.append(c)
                        can.num=3
                        can.length=(l-i)
                        can.avelen=(len(a)+len(b)+len(c))/3.0
                        can.variance=(len(a)-can.avelen)**2+(len(b)-can.avelen)**2+(len(c)-can.avelen)**2
                        can.lsum=0
                        if(len(a)==1):
                            can.lsum+=math.log(x)
                        if(len(b)==1):
                            can.lsum+=math.log(y)
                        if(len(c)==1):
                            can.lsum+=math.log(z)
                        candidates.append(can)
        if(len(candidates)!=0):
            candidates = sorted(candidates, key=attrgetter('lsum'),reverse=True)
            candidates = sorted(candidates, key=attrgetter('variance'))
            candidates=sorted(candidates,key=attrgetter('length','avelen'),reverse=True)
            for x in range(0,candidates[0].num):
                Allwords.append(candidates[0].words[x])
            i=i+candidates[0].length
        #如果找不到三个分词的词语则尝试使用simple方法
        else:
            update=False
            for j in range(n+1,i+1):
                w=sentence[i:j]
                if(Trie.find(w)!=0):
                    update=True
                    i=j
                    Allwords.append(w)
                    break
            if(update==False):
                w = sentence[i:i+1]
                Allwords.append(w)
                i=i+1
    ans=[]
    for c in Allwords:
        print (c.encode('utf-8')),
    print ("")