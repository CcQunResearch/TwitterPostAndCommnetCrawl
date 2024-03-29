# -*- coding: utf-8 -*-
# @Time    :
# @Author  :
# @Email   :
# @File    : record.py
# @Software: PyCharm
# @Note    :
import os
import json

from utils import write_tweet

data_dir = 'Data'

old_filenames = set(json.load(open('filenames.json', 'r', encoding='utf-8')))

now_filenames = set(os.listdir(data_dir))

new_filenames = list(old_filenames | now_filenames)

write_tweet(new_filenames, 'filenames.json')
