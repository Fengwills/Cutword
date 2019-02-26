def letter_cut(vocab,source):
    target=""
    flag = False
    for c in source:
        if target !="" and ((c not in vocab and flag==False) or (c in vocab and flag==True)):
            if c!=' ': 
                target=target+'\t/'
            flag = not flag
        if c==' ':
            continue
        target = target+c

    target = target+'/'
    return target
def maxmatch_cut(vocab,source):
    maxlen=0
    for key in vocab:
        if len(key)>maxlen:
            maxlen = len(key)
    l = len(source)
    p = 0
    result = ""
    while p < l:
        length = min(maxlen, l - p)
        wlen = 1
        for i in range(length, 0, -1):
            if source[p:p + i] in vocab:
                wlen = i
                break
        if source[p:p+wlen]!=' ':
            result = result+source[p:p + wlen]+"/"
        p += wlen
    return result