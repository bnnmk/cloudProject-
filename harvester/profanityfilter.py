import os
import re

"""
https://github.com/void4/profilter/blob/master/blacklist.txt
https://github.com/areebbeigh/profanityfilter/blob/master/profanityfilter/data/badwords.txt
https://github.com/ben174/profanity/blob/master/profanity/data/wordlist.txt
"""


def load_txt():
    ABS_PATH = os.path.dirname(os.path.realpath(__file__))

    with open(ABS_PATH + '/badwords.txt') as myfile:
        lines = myfile.readlines()

    simple_words = set()
    complex_words = set()

    for line in lines:
        line = line.strip()

        if line:
            line = line.lower()

            if re.match(r'^\w.*\w$', line):
                simple_words.add(line)
            else:
                complex_words.add(line)

    patterns = set()
    for word in simple_words:
        patterns.add(re.compile(r'\b%s\b' % re.escape(word), re.IGNORECASE))
    for word in complex_words:
        patterns.add(re.compile(r'(?<=\W)%s(?=\W)' % re.escape(word), re.IGNORECASE))

    return patterns


PATTERNS = load_txt()


def detect(text):
    for pattern in PATTERNS:
        if pattern.search(' %s ' % text):
            return 1
    return 0


if __name__ == '__main__':
    words = [
        's.o.b.',
        'sh!+',
        'shi+',
        '@$$',

        'abc sh!+ 123',
        'abc sh!+',
        'sh!+ 123',

        'ashi+',
        'shi+1',
    ]

    for word in words:
        print(detect(word))
