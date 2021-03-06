# -*- coding: utf-8 -*-

'''
create by : joshua zou
create date : 2017.11.28
Purpose: check tecent ai api
'''


import requests
import base64
import hashlib
import time
import random
import os,string,glob
from PIL import Image 
from io import BytesIO
from urllib.parse import urlencode
from urllib import parse
import json


class TencentAPIMsg(object):
    def __init__(self,AppID=None,AppKey=None):
        '''
        图形OCR
        appid=000
        AppKey=0000
        '''
        if not AppID: AppID = '1100000000000'
        if not AppKey: AppKey = 'ZV1w0000000000'
        self.__app_id= AppID 
        self.__app_key= AppKey 
        self.__img_base64str=None
        
    def get_random_str(self):
        """ 随机生成16位字符串
        @return: 16位字符串
        """
        rule = string.ascii_lowercase + string.digits
        str = random.sample(rule, 32)
        return "".join(str)
    
    def get_time_stamp(self):
        return str(int(time.time()))
    
    def __get_image_base64str__(self,image):
        if not isinstance(image,Image.Image):return None 
        outputBuffer = BytesIO()
        image.save(outputBuffer, format='JPEG')
        imgbase64 = base64.b64encode(outputBuffer.getvalue())
        return imgbase64
    
    def __get_imgfile_base64str__(self,image):
        if not isinstance(image, str): return None
        if not os.path.isfile(image): return None

        with open(image,'rb') as fp:
            imgbase64 = base64.b64encode(fp.read())
            return imgbase64
        
    def get_img_base64str(self,image):
        if isinstance(image, str): 
            self.__img_base64str= self.__get_imgfile_base64str__(image)
        elif isinstance(image,Image.Image):
            self.__img_base64str= self.__get_image_base64str__(image)
        return self.__img_base64str.decode()
    
    # 生成签名相关算法
    def get_param_sign_str(self,param_dict):
        sb = '';
        for k in sorted(param_dict.keys()):
            if (0 < len(sb)):
                sb += '&' + k + '=' + parse.quote_plus(param_dict[k]);
            else:
                sb += k + '=' + parse.quote_plus(param_dict[k])
        sign_str = self.gen_str_md5(sb + '&app_key=' + self.__app_key)
        return sign_str

    # MD5加密方法
    def gen_str_md5(self,rawstr):
        hash = hashlib.md5()  # md5对象，md5不能反解，但是加密是固定的，就是关系是一一对应，所以有缺陷，可以被对撞出来
        hash.update(bytes(rawstr, encoding='utf-8'))  # 要对哪个字符串进行加密，就放这里
        return hash.hexdigest().upper();

    # 组装字典，MD5加密方法
    '''
    ======================================
    tencent获得参数对列表N（字典升级排序）
    ======================================
    1\依照算法第一步要求，对参数对进行排序，得到参数对列表N如下。
    参数名 	参数值
    app_id 	10000
    nonce_str 	20e3408a79
    text 	腾讯开放平台
    time_stamp 	1493449657
    
    2\按URL键值拼接字符串T
    依照算法第二步要求，将参数对列表N的参数对进行URL键值拼接，值使用URL编码，URL编码算法用大写字母，例如%E8，而不是小写%e8，得到字符串T如下：
    app_id=10000&nonce_str=20e3408a79&text=%E8%85%BE%E8%AE%AF%E5%BC%80%E6%94%BE%E5%B9%B3%E5%8F%B0&time_stamp=1493449657
    
    3\拼接应用密钥，得到字符串S
    依照算法第三步要求，将应用密钥拼接到字符串T的尾末，得到字符串S如下。
    app_id=10000&nonce_str=20e3408a79&text=%E8%85%BE%E8%AE%AF%E5%BC%80%E6%94%BE%E5%B9%B3%E5%8F%B0&time_stamp=1493449657&app_key=a95eceb1ac8c24ee28b70f7dbba912bf
    
    4\计算MD5摘要，得到签名字符串
    依照算法第四步要求，对字符串S进行MD5摘要计算得到签名字符串如。
    e8f6f347d549fe514f0c9c452c95da9d
    
    5\转化md5签名值大写
    对签名字符串所有字母进行大写转换，得到接口请求签名，结束算法。
    E8F6F347D549FE514F0C9C452C95DA9D
    
    6\最终请求数据
    在完成签名计算后，即可得到所有接口请求数据，进一步完成API的调用。
    text 	腾讯开放平台 	接口请求数据，UTF-8编码
    app_id 	10000 	应用标识
    time_stamp 	1493449657 	请求时间戳（秒级），用于防止请求重放
    nonce_str 	20e3408a79 	请求随机字符串，用于保证签名不可预测
    sign 	E8F6F347D549FE514F0C9C452C95DA9D 	请求签名    
    '''
    def gen_dict_md5(self,req_dict,app_key):
        if not isinstance(req_dict,dict) :return None 
        if not isinstance(app_key,str) or not app_key:return None 
        
        try:
            #方法1，自己写urlencode函数
            #md5text =self.get_param_sign_str(req_dict)
            
            #方法2，先对字典排序，排序之后，写app_key，再urlencode
            sort_dict= sorted(req_dict.items(), key=lambda item:item[0], reverse = False)
            sort_dict.append(('app_key',app_key))
            sha = hashlib.md5()
            rawtext= urlencode(sort_dict).encode()
            sha.update(rawtext)
            md5text= sha.hexdigest().upper()
            #print(1)
            #字典可以在函数中改写
            if md5text: req_dict['sign']=md5text
            return md5text
        except Exception as e:
            return   None

    #生成字典
    def init_req_dict(self, req_dict,app_id=None, app_key=None,time_stamp=None, nonce_str=None):
        """用MD5算法生成安全签名"""
        if not req_dict.get('app_id'): 
            if not app_id: app_id= self.__app_id
            req_dict['app_id']= app_id
       
        #nonce_str 字典无值
        if not req_dict.get('time_stamp'): 
            if not time_stamp: time_stamp= self.get_time_stamp()
            req_dict['time_stamp']= time_stamp
        
        if not req_dict.get('nonce_str'): 
            if not nonce_str: nonce_str= self.get_random_str()
            req_dict['nonce_str']= nonce_str
        #app_key 取系统参数。
        if not app_key: app_key= self.__app_key        
        md5key= self.gen_dict_md5(req_dict, app_key)
        return md5key

TencentAPI = {
    # 基本文本分析API
    "nlp_wordseg":    {
        'APINAME': '分词',  # API中文简称
        'APIDESC': '对文本进行智能分词识别，支持基础词与混排词粒度',  # API描述
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_wordseg',  # API请求URL
        'APIPARA': 'text'  # API非公共参数
    },
    "nlp_wordpos":    {
        'APINAME': '词性标注',
        'APIDESC': '对文本进行分词，同时为每个分词标注正确的词性',
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_wordpos',
        'APIPARA': 'text'
    },
    'nlp_wordner':    {
        'APINAME': '专有名词识别',
        'APIDESC': '对文本进行专有名词的分词识别，找出文本中的专有名词',
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_wordner',
        'APIPARA': 'text'
    },
    'nlp_wordsyn':    {
        'APINAME': '同义词识别',
        'APIDESC': '识别文本中存在同义词的分词，并返回相应的同义词',
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_wordsyn',
        'APIPARA': 'text'
    },

    # 计算机视觉--OCR识别API
    "ocr_generalocr":    {
        'APINAME': '通用OCR识别',
        'APIDESC': '识别上传图像上面的字段信息',
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr',
        'APIPARA': 'image'
    },
    "ocr_idcardocr":    {
        'APINAME': '身份证OCR识别',
        'APIDESC': '识别身份证图像上面的详细身份信息',
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_idcardocr',
        'APIPARA': 'image,card_type'
    },
    "ocr_bcocr":    {
        'APINAME': '名片OCR识别',
        'APIDESC': '识别名片图像上面的字段信息',
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_bcocr',
        'APIPARA': 'image'
    },
    "ocr_driverlicenseocr": {
        'APINAME': '行驶证驾驶证OCR识别',
        'APIDESC': '识别行驶证或驾驶证图像上面的字段信息',
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_driverlicenseocr',
        'APIPARA': 'image,type'
    },
    "ocr_bizlicenseocr": {
        'APINAME': '营业执照OCR识别',
        'APIDESC': '识别营业执照上面的字段信息',
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_bizlicenseocr',
        'APIPARA': 'image'
    },
    "ocr_creditcardocr": {
        'APINAME': '银行卡OCR识别',
        'APIDESC': '识别银行卡上面的字段信息',
        'APIURL': 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_creditcardocr',
        'APIPARA': 'image'
    },
}
