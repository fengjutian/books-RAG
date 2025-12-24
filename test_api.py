#!/usr/bin/env python3
"""
测试Kimi API连接
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取配置
api_key = os.getenv("MOONSHOT_API_KEY")
api_base = os.getenv("MOONSHOT_API_BASE", "https://api.moonshot.cn/v1")
model = os.getenv("MOONSHOT_MODEL", "kimi-k2-turbo-preview")

print(f"API Base: {api_base}")
print(f"Model: {model}")
print(f"API Key: {api_key[:10]}...{api_key[-10:]}")

# 创建客户端
client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

try:
    # 测试列表模型（简单的API调用）
    print("\n测试API连接...")
    models = client.models.list()
    print("✅ API连接成功！")
    print("可用模型:")
    for model in models.data:
        print(f"  - {model.id}")
        
    # 测试聊天功能
    print("\n测试聊天功能...")
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "你好，请简单回复'测试成功'"}],
        max_tokens=50
    )
    print(f"✅ 聊天测试成功: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ API测试失败: {e}")
    print("\n建议:")
    print("1. 检查API密钥是否正确")
    print("2. 确认账户有API访问权限") 
    print("3. 尝试使用其他API服务")