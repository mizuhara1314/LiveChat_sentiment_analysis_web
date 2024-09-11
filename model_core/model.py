from transformers import  BertModel, BertTokenizer
import torch
import torch.nn as nn
import pandas as pd
import torch.nn.functional as F
import matplotlib.pyplot as plt


class ModelHandler:
   
    def __init__(self, model_path, device='cpu'):
        """
        初始化模型处理类，加载模型和分词器。
        :param model_path: 模型文件路径
        :param device: 使用的设备（默认为 'cpu'）
        """
        self.device = device
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
        
        self.model = torch.load(model_path, map_location=torch.device(self.device))
        self.model.eval()  # 设置模型为评估模式
    
    def load_dataset(self, filepath, max_len):
        """
        加载并编码数据集。
        :param filepath: 文本文件路径
        :param max_len: 最大长度
        :return: 输入 ID 和 attention mask
        """
        sentences = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    sentences.append(line)
        
        input_ids, attention_masks = [], []
        for sentence in sentences:
            encoded_data = self.tokenizer.encode_plus(
                text=sentence,
                add_special_tokens=True,
                max_length=max_len,
                padding='max_length',
                return_attention_mask=True,
                truncation=True
            )
            input_ids.append(encoded_data['input_ids'])
            attention_masks.append(encoded_data['attention_mask'])
        
        input_ids = torch.tensor(input_ids)
        attention_masks = torch.tensor(attention_masks)
        
        return input_ids, attention_masks

    def predict_from_file(self, filepath, max_len=20):
        """
        从文件加载数据并进行预测。
        :param filepath: 测试数据文件路径
        :param max_len: 最大长度
        :return: 预测结果列表
        """
        # 加载数据
        input_ids, attention_masks = self.load_dataset(filepath, max_len)

        # 存储预测结果
        ans = []
        test_result = []
        # 逐条进行预测
        for input_id, attention_mask in zip(input_ids, attention_masks):
            b_input_ids = input_id.unsqueeze(0).to(self.device)
            b_attn_mask = attention_mask.unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(b_input_ids, attention_mask=b_attn_mask)
                prediction = outputs.argmax(dim=1)
                tokens = [self.tokenizer.convert_ids_to_tokens(id.item()) for id in b_input_ids[0]]
                test_result.append([prediction.item(), tokens])
                ans.append(prediction.item())
        # 写入csv文件
        df = pd.DataFrame(test_result)
        df.to_csv('test_result.csv',index=False, header=['predict','text'])
        return ans
    
    def plot_and_save(self, predictions, output_path):
            """
            根据预测结果生成柱状图并保存。
            :param predictions: 预测结果列表（仅包含0和1）
            :param output_path: 图像保存路径
            """
            # 统计类别出现的次数
            counts = [predictions.count(0), predictions.count(1)]
            
            # 创建柱状图
            plt.figure(figsize=(8, 5))
            plt.bar(['Negative (0)', 'Positive (1)'], counts, color=['red', 'green'])
            plt.xlabel('類別')
            plt.ylabel('數量')
            plt.title('預測結果的柱狀圖')
            
            # 保存图像
            plt.savefig(output_path)
            plt.close()