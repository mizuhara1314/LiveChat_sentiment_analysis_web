import re
from opencc import OpenCC
from chat_downloader import ChatDownloader

class Crawler:
    def __init__(self):
        self.cc = OpenCC('t2s')

    def crawl_chat(self, url, output_file):
        # 抓取Twitch聊天内容
        chat = ChatDownloader().get_chat(url, max_messages=5)

        result = []
        for message in chat:
            if len(message["message"]) <= 25:
                result.append(message["message"])

        # 提取中文字符
        filtered_result = [self.extract_chinese(text) for text in result if self.extract_chinese(text)]
        
        # 保存原始繁体数据
        original_traditional_data = filtered_result.copy()

        # 将繁体字串转换为简体
        simplified_result = [self.cc.convert(text) for text in filtered_result]

        # 保存简体数据到文件
        self.save_to_file(simplified_result, output_file)
        
        return original_traditional_data  # 返回原始繁体数据

    def extract_chinese(self, text):
        # 使用正则表达式匹配中文字符
        return ''.join(re.findall(r'[\u4e00-\u9fff]', text))

    def save_to_file(self, data, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(item + '\n')
