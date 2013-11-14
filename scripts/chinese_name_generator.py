#!/usr/bin/env python

# based heavily off of  https://github.com/greghaskins/gibberish
  
import string
import random

__all__ = ('generate_name', 'generate_names')

given_names = ["Ah","Ai","An","Bai","Bao","Bo","Chang","Chao","Chen","Cheng","Chin","Chun","Da","Dong","Fen","Fu","Gang","Guo","Hai","He","Heng","Hong","Hua","Huan","Huang","Hui","Jia","Jian","Jiang","Jin","Jing","Ju","Jun","Kun","Lan","Li","Lim","Lin","Ling","Mei","Min","Ming","Mu","Ning","Nuan","Nuo","Ping","Qiang","Qing","Qiu","Rong","Ru","Shi","Shu","Shui","Shun","Su","Tai","Tu","Wei","Wen","Wu","Xiang","Xiu","Xue","Xun","Ya","Yi","Yin","Yong","Yu","Yun","Zan","Zhen","Zheng","Zhi","Zhong","Zhou"]
family_names = ["Li","Wang","Zhang","Liu","Chen","Yang","Zhao","Huang","Zhou","Wu","Xu","Sun","Hu","Zhu","Gao","Lin","He","Guo","Ma","Luo","Liang","Song","Zheng","Xie","Han","Tang","Feng","Yu","Dong","Xiao","Cheng","Cao","Yuan","Deng","Xu","Fu","Shen","Zeng","Peng","Lu","Su","Lu","Jiang","Cai","Jia","Ding","Wei","Xue","Ye","Yan","Yu","Pan","Du","Dai","Xia","Zhong","Wang","Tian","Ren","Jiang","Fan","Fang","Shi","Yao","Tan","Sheng","Zou","Xiong","Jin","Lu","Hao","Kong","Bai","Cui","Kang","Mao","Qiu","Qin","Jiang","Shi","Gu","Hou","Shao","Meng","Long","Wan","Duan","Zhang","Qian","Tang","Yin","Li","Yi","Chang","Wu","Qiao","He","Lai","Gong","Wen"]

def generate_name():
	"""Returns a random consonant-vowel-consonant pseudo-word."""
	names = list(random.choice(s) for s in (family_names, given_names, given_names))
	name = names[0] + ' ' + names[1]
	if(bool(random.getrandbits(1))):
		name += names[2].lower()
	return name

def generate_names(wordcount):
    """Returns a list of ``wordcount`` pseudo-words."""
    return [generate_name() for _ in xrange(wordcount)]


def console_main():
    import sys
    try:
        wordcount = int(sys.argv[1])
    except (IndexError, ValueError):
        wordcount = 1
    print(' '.join(generate_names(wordcount)))


if __name__ == '__main__':
    console_main()
