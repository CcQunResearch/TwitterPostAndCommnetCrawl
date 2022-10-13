# -*- coding: utf-8 -*-
# @Time    : 2022/10/13 16:05
# @Author  : CcQun
# @Email   : 13698603020@163.com
# @File    : record.py
# @Software: PyCharm
# @Note    :
import os
import json

from utils import write_tweet

data_dir = 'Data'
filenames = os.listdir(data_dir)

write_tweet(filenames,'filenames.json')