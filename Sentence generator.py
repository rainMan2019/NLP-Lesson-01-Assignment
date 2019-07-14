#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：albert time:2019-07-09
import random2
import pandas as pd
import re
from collections import Counter
import jieba
#人类语言
homan = """
query=> date question 
require=>verb noun
verb=>打开|查找|关闭
noun=>微信|相机|电话簿
date=>昨天|今天|明天|后天
question=>下雨吗|星期几
"""
#机器语言
assistant = """
ask=>word person thing
word=>请问|对不起
person=>你|您|我
thing=>需要什么帮助|没听懂您的话
"""
def create_grammar(grammar_str, split='=>', line_split='\n'):
    grammar = {}
    for line in grammar_str.split(line_split):
        if not line.strip(): continue
        exp, stmt = line.split(split)
        grammar[exp.strip()] = [s.split() for s in stmt.split('|')]
    return grammar
#生成语法
homan_grammar=create_grammar(homan)
assistant_grammar=create_grammar(assistant)
#print(homan_grammar)
#print(assistant_grammar)

#生成句子
def generate(gram, target):
    if target not in gram: return target  # means target is a terminal expression
    expaned = [generate(gram, t) for t in random2.choice(gram[target])]
    return ''.join([e if e != '/n' else '\n' for e in expaned if e != 'null'])

#生成n个句子
def generate_n(n):
    for i in range(n):
        print(generate(assistant_grammar, 'ask')+"======"+generate(homan_grammar, 'require'))

#generate_n(30)

filename = r'C:\Users\DELL\Desktop\NLP\lesson01\movie_comments.csv'
content = pd.read_csv(filename, encoding='gb18030')
# content = content.astype(str)
#print(content.head())
articles = content['id,link,name,comment,star'].tolist()
# 把所有中文提取出来
def token(string):
    # we will learn the regular expression next course.
    string1 = re.findall(u'[\u4e00-\u9fa5]', string)
    return re.findall('\w+', str(string1))
articles_clean = [''.join(token(str(a)))for a in articles]  #获得所有文本

with open(r'C:\Users\DELL\Desktop\NLP\lesson01\article_clean.txt', 'w') as f:
    for a in articles_clean:
        f.write(a + '\n')
def cut(string): return list(jieba.cut(string))
TOKEN = []
for i, line in enumerate((open(r'C:\Users\DELL\Desktop\NLP\lesson01\article_clean.txt'))):
    #if i % 100 == 0: print(i)
    if i > 10000: break
    TOKEN += cut(line)

words_count = Counter(TOKEN)
#print(words_count.most_common(100))

def prob_1(word):
    return words_count[word] / len(TOKEN)
TOKEN = [str(t) for t in TOKEN]
TOKEN_2_GRAM = [''.join(TOKEN[i:i+2]) for i in range(len(TOKEN[:-2]))]
words_count_2 = Counter(TOKEN_2_GRAM)
#print(words_count_2.most_common(100))
def prob_2(word1, word2):
    if word1 + word2 in words_count_2: return words_count_2[word1+word2] / len(TOKEN_2_GRAM)
    else:
        return 1 / len(TOKEN_2_GRAM)

#句子的概率
def get_probablity(sentence):
    words = cut(sentence)
    sentence_pro = 1
    for i, word in enumerate(words[:-1]):
        next_ = words[i + 1]
        probability = prob_2(word, next_)
        sentence_pro *= probability
    return sentence_pro
#print(get_probablity('小明今天抽奖抽到一台苹果手机'))
def generate_best(grammer,n):
    result = []
    for sen in [generate(gram=grammer, target='ask' if grammer == assistant_grammar else random2.choice(['query','require']) ) for i in range(n)]:
        result.append((sen,get_probablity(sen)))
        #print('sentence: {} with Prb: {}'.format(sen, get_probablity(sen)))
    print(sorted(result , key=lambda x: x[1]))
generate_best(homan_grammar,20)