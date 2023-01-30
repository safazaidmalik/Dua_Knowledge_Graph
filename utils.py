# Selected utility functions from:
# https://alraqmiyyat.github.io/2013/01-02.html


import pyarabic.araby as araby
import pyarabic.number as number
from pyarabic.araby import strip_harakat, strip_tashkeel, strip_tatweel, normalize_hamza, tokenize, sentence_tokenize, is_arabicrange
import unicodedata, re

def normalize_arabic(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()

def normalize_alaf(text):
    return text.replace('إ', 'ا')

def normalizeArabic(text):
    text = re.sub("[إأٱآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    return(text)

def deNormalize(text):
    alifs           = '[إأٱآا]'
    alifReg         = '[إأٱآا]'
    # -------------------------------------
    alifMaqsura     = '[يى]'
    alifMaqsuraReg  = '[يى]'
    # -------------------------------------
    taMarbutas      = 'ة'
    taMarbutasReg   = '[هة]'
    # -------------------------------------
    hamzas          = '[ؤئء]'
    hamzasReg       = '[ؤئءوي]'
    # Applying deNormalization
    text = re.sub(alifs, alifReg, text)
    text = re.sub(alifMaqsura, alifMaqsuraReg, text)
    text = re.sub(taMarbutas, taMarbutasReg, text)
    text = re.sub(hamzas, hamzasReg, text)
    return text

def deNoise(text):
    noise = re.compile(""" ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    text = re.sub(noise, '', text)
    return text


# str1 = normalize_alaf("الاسراء")
# str2 = normalize_alaf("الإسراء")
# print("string 1 = ", str1)
# print("string 2 = ", str2)
# if str1 == str2:
#     print("same")
# else:
#     print("different")


# from pyarabic.araby import tokenize, is_arabicrange, strip_tashkeel

# res = tokenize("( القصص: 24 )", conditions=is_arabicrange, morphs=strip_tashkeel)
# print(res)
# print(is_arabicrange('( القصص: 24 )'))
