import os
import re
import requests
import argparse
from urllib.parse import urlparse
from pathlib import Path
from tqdm import tqdm

def download_image(url, output_dir):
    """下载图片到指定目录并显示进度条"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 从URL中提取文件名
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = f"image_{hash(url)}.jpg"  # 如果URL中没有文件名，生成一个
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取文件总大小（字节）
        total_size = int(response.headers.get('content-length', 0))
        
        # 保存图片并显示进度条
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as f:
            with tqdm(
                total=total_size, 
                unit='B', 
                unit_scale=True, 
                unit_divisor=1024,
                desc=f"下载 {filename[:20]}..."  # 限制描述长度
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤掉保持连接的新块
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        return filepath
    except Exception as e:
        print(f"\n下载图片失败: {url}, 错误: {e}")
        return None

def process_markdown_file(input_path):
    """处理Markdown文件"""
    print(f"\n开始处理文件: {input_path}")
    
    # 读取Markdown内容
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建输出目录结构
    input_path_obj = Path(input_path)
    relative_path = input_path_obj.parent.relative_to(input_path_obj.anchor)
    output_dir = Path("data") / relative_path / input_path_obj.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找所有图片标记
    pattern = r'!\[(.*?)\]\((.*?)\)'
    matches = re.findall(pattern, content)
    
    if not matches:
        print("未找到需要下载的图片")
        return
    
    print(f"找到 {len(matches)} 张需要下载的图片")
    
    # 替换图片路径
    new_content = content
    downloaded_count = 0
    
    for alt_text, img_url in matches:
        if img_url.startswith(('http://', 'https://')):
            # 下载图片
            print(f"\n处理图片: {alt_text[:20]}...")
            local_path = download_image(img_url, output_dir)
            if local_path:
                # 计算相对于Markdown文件所在目录的相对路径
                relative_path = os.path.relpath(local_path, start=input_path_obj.parent)
                # 替换Windows路径分隔符为统一的正斜杠
                relative_path = relative_path.replace('\\', '/')
                # 替换Markdown中的图片路径
                new_content = new_content.replace(
                    f'![{alt_text}]({img_url})',
                    f'![{alt_text}]({relative_path})'
                )
                downloaded_count += 1
    
    print(f"\n下载完成: {downloaded_count}/{len(matches)} 张图片下载成功")
    
    # 删除旧文件
    try:
        os.remove(input_path)
        print(f"已删除旧文件: {input_path}")
    except OSError as e:
        print(f"删除旧文件失败: {e}")
        return
    
    # 生成新文件（使用原文件名）
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"处理完成! 新文件已保存到: {input_path}")

def main():
    parser = argparse.ArgumentParser(description='Markdown图片下载与路径替换工具')
    parser.add_argument('filepath', help='Markdown文件路径')
    args = parser.parse_args()
    
    if not os.path.isfile(args.filepath):
        print("错误: 指定的文件不存在")
        return
    
    process_markdown_file(args.filepath)

if __name__ == '__main__':
    main()