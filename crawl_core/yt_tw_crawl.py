import re
from opencc import OpenCC
from chat_downloader import ChatDownloader
import pytchat
import time



class Crawler:
    def __init__(self):
        self.cc = OpenCC('t2s')

    def crawl_chat(self, url, output_file):
        # 判断是YouTube还是Twitch的URL
        if "youtube" in url:
            # 如果是YouTube URL，调用YouTube爬取方法
            original_traditional_data = self.fetch_youtube_chat(url)
        elif "twitch" in url:
            # 如果是Twitch URL，调用Twitch爬取方法
            original_traditional_data = self.fetch_twitch_chat(url)
        else:
            raise ValueError("不支持的URL，请提供YouTube或Twitch的链接")
        
        # 将繁体字串转换为简体
        simplified_result = [self.cc.convert(text) for text in original_traditional_data]

        # 保存简体数据到文件
        self.save_to_file(simplified_result, output_file)
      
        return original_traditional_data  # 返回原始繁体数据

    def fetch_twitch_chat(self, url):
        # 抓取Twitch聊天内容
        chat = ChatDownloader().get_chat(url, max_messages=5)

        result = []
        for message in chat:
            if len(message["message"]) <= 25:
                result.append(message["message"])

        # 提取中文字符
        filtered_result = [self.extract_chinese(text) for text in result if self.extract_chinese(text)]
        return filtered_result

    def fetch_youtube_chat(self, url):
        # 使用pytchat抓取YouTube聊天内容，直接传入完整的URL
        chat = pytchat.create(video_id=url)
        result = []
        
        # 设置爬取的持续时间
        start_time = time.time()
        while chat.is_alive():
            for c in chat.get().sync_items():
                message = c.message.split(":")[0]
                if len(message) <= 25:  # 只处理长度小于等于25的消息
                    result.append(message)
                
            
            # 限制爬取时间为5秒
            if time.time() - start_time > 8:
                break
        
        # 提取中文字符
        filtered_result = [self.extract_chinese(text) for text in result if self.extract_chinese(text)]
        return filtered_result

    def extract_chinese(self, text):
        # 使用正则表达式匹配中文字符
        return ''.join(re.findall(r'[\u4e00-\u9fff]', text))

    def save_to_file(self, data, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(item + '\n')
