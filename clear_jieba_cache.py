# clear_jieba_cache.py
import os
import tempfile
import shutil

def clear_jieba_cache():
    """删除 jieba 在临时目录中生成的缓存文件"""
    temp_dir = tempfile.gettempdir()
    cache_file = os.path.join(temp_dir, 'jieba.cache')
    
    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
            print(f"✅ 已成功删除 jieba 缓存文件: {cache_file}")
        except Exception as e:
            print(f"❌ 删除失败: {e}")
    else:
        print("ℹ️  jieba 缓存文件不存在，无需清理。")

if __name__ == "__main__":
    clear_jieba_cache()