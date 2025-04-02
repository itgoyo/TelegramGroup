import random
import re
import os
import subprocess
from datetime import datetime

def git_operations(script_dir):
    try:
        # 设置git环境变量
        git_env = {
            'GIT_DIR': os.path.join(script_dir, '.git'),
            'GIT_WORK_TREE': script_dir
        }
        
        # 设置Git用户信息
        subprocess.run(['git', 'config', 'user.name', 'AZeC4'], env=git_env, check=True)
        subprocess.run(['git', 'config', 'user.email', 'itgoyo@foxmail.com'], env=git_env, check=True)
        
        # 获取当前日期时间
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Git 操作
        subprocess.run(['git', 'add', '.'], env=git_env, check=True)
        subprocess.run(['git', 'commit', '-m', f"Update README.md - {current_date}"], env=git_env, check=True)
        
        # 获取当前分支名称
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              env=git_env, 
                              capture_output=True, 
                              text=True, 
                              check=True)
        current_branch = result.stdout.strip()
        
        # 使用检测到的分支名进行推送
        subprocess.run(['git', 'push', 'origin', current_branch], env=git_env, check=True)
        
        print(f"Successfully pushed to GitHub on branch {current_branch}!")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def replace_jiso_line(filename):
    # Define the possible IDs
    ids = ['7737195905', '7439567495', '7202424896', '2114110836']
    
    # The template for the line, {} will be replaced with random ID
    line_template = '| 极搜JiSo   | [@jiso](https://t.me/jiso?start=a_{})                       | 帮你找到有趣的群、频道、视频、音乐、电影、新闻 |\n'
    
    # Read the file
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.readlines()
    
    # Find the line to replace
    for i, line in enumerate(content):
        if '极搜JiSo' in line and '@jiso' in line:
            # Replace with a random variation
            random_id = random.choice(ids)
            content[i] = line_template.format(random_id)
            break
    
    # Write back to file
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(content)

if __name__ == "__main__":
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 切换到脚本所在目录
    os.chdir(script_dir)
    
    # 执行文件替换
    replace_jiso_line('README.md')
    
    # 执行git操作
    git_operations(script_dir)