#!/usr/bin/env python3
"""
自动替换Markdown文件中的Telegram链接并提交到GitHub的脚本

功能：
- 定期检查指定的Markdown文件
- 替换特定的Telegram链接
- 自动提交到GitHub仓库
"""

import os
import re
import time
import random
import subprocess
from datetime import datetime
from pathlib import Path


class MarkdownLinkUpdater:
    """自动更新Markdown文件中Telegram链接的类"""

    def __init__(
        self,
        repo_path: str,
        file_path: str,
        link_id_1: str,
        link_id_2: str,
        interval_min: int = 60,
        interval_max: int = 120,
    ):
        """
        初始化链接更新器

        Args:
            repo_path: GitHub仓库本地路径
            file_path: 要修改的Markdown文件路径（相对于仓库根目录）
            link_id_1: 第一个链接ID（默认：7202424896）
            link_id_2: 第二个链接ID（默认：6294881820）
            interval_min: 最小检查间隔（分钟）
            interval_max: 最大检查间隔（分钟）
        """
        self.repo_path = Path(repo_path).resolve()
        self.file_path = self.repo_path / file_path
        self.link_id_1 = link_id_1
        self.link_id_2 = link_id_2
        self.interval_min = interval_min
        self.interval_max = interval_max
        self.last_replacement = None  # 记录最后一次替换的方向

        self._validate_config()

    def _validate_config(self):
        """验证配置的有效性"""
        if not self.repo_path.is_dir():
            raise ValueError(f"仓库路径不存在: {self.repo_path}")

        if not self.file_path.is_file():
            raise ValueError(f"文件不存在: {self.file_path}")

        if self.interval_min <= 0 or self.interval_max <= 0:
            raise ValueError("检查间隔必须是正数")

        if self.interval_min > self.interval_max:
            raise ValueError("最小间隔不能大于最大间隔")

    def _run_git_command(self, command: list) -> str:
        """在仓库目录中执行Git命令"""
        try:
            result = subprocess.run(
                command, cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git命令失败: {e}")
            print(f"错误输出: {e.stderr}")
            return ""

    def _check_file_changes(self) -> bool:
        """检查目标文件是否有未提交的更改"""
        status = self._run_git_command(["git", "status", "--porcelain", str(self.file_path)])
        # 如果有输出，说明文件有未提交的更改
        return bool(status.strip())

    def _update_links(self) -> bool:
        """
        检查并更新Markdown文件中的链接（轮换替换）

        Returns:
            是否成功更新了文件
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 构建两个方向的匹配模式
            pattern_1 = rf'https://t\.me/jiso\?start=a_{re.escape(self.link_id_1)}'
            pattern_2 = rf'https://t\.me/jiso\?start=a_{re.escape(self.link_id_2)}'
            
            # 检查当前文件中存在哪个链接
            has_link_1 = bool(re.search(pattern_1, content))
            has_link_2 = bool(re.search(pattern_2, content))
            
            if has_link_1 and has_link_2:
                print(f"文件中同时存在两个链接ID，建议手动检查")
                return False
            elif has_link_1:
                # 找到link_id_1，替换为link_id_2
                pattern = pattern_1
                replacement = f'https://t.me/jiso?start=a_{self.link_id_2}'
                current_id = self.link_id_1
                target_id = self.link_id_2
                self.last_replacement = f"{self.link_id_1} -> {self.link_id_2}"
            elif has_link_2:
                # 找到link_id_2，替换为link_id_1
                pattern = pattern_2
                replacement = f'https://t.me/jiso?start=a_{self.link_id_1}'
                current_id = self.link_id_2
                target_id = self.link_id_1
                self.last_replacement = f"{self.link_id_2} -> {self.link_id_1}"
            else:
                print(f"未找到需要替换的jiso链接（{self.link_id_1} 或 {self.link_id_2}）")
                return False

            # 执行替换
            updated_content = re.sub(pattern, replacement, content)
            
            # 计算替换次数
            count = len(re.findall(pattern, content))

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            print(f"成功替换 {count} 个jiso链接: {current_id} -> {target_id}")
            return True

        except Exception as e:
            print(f"更新文件失败: {e}")
            return False

    def _commit_changes(self) -> bool:
        """提交更改到本地仓库"""
        try:
            self._run_git_command(["git", "add", str(self.file_path)])
            commit_msg = "add somethings"
            self._run_git_command(["git", "commit", "-m", commit_msg])
            print("提交成功")
            return True
        except Exception as e:
            print(f"提交失败: {e}")
            return False

    def _push_to_remote(self) -> bool:
        """推送到远程仓库"""
        try:
            print("正在推送到远程仓库...")
            self._run_git_command(["git", "push"])
            print("推送成功")
            return True
        except Exception as e:
            print(f"推送失败: {e}")
            return False

    def run(self) -> None:
        """启动自动更新程序"""
        print(f"=== Telegram链接自动更新器（轮换模式） ===")
        print(f"仓库: {self.repo_path}")
        print(f"文件: {self.file_path}")
        print(f"轮换ID: {self.link_id_1} <-> {self.link_id_2}")
        print(f"检查间隔: {self.interval_min}-{self.interval_max}分钟")
        print("-" * 50)

        try:
            while True:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{current_time}] 开始检查...")

                # 直接尝试更新链接
                if self._update_links():
                    # 提交和推送
                    if self._commit_changes():
                        self._push_to_remote()
                else:
                    print("不需要更新或更新失败")

                # 随机等待1-2小时
                wait_time = random.randint(
                    self.interval_min * 60, self.interval_max * 60
                )
                print(
                    f"等待 {wait_time // 60} 分钟 {wait_time % 60} 秒后进行下一次检查..."
                )
                time.sleep(wait_time)

        except KeyboardInterrupt:
            print("\n程序已停止")
        except Exception as e:
            print(f"\n程序错误: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="自动替换Markdown文件中的Telegram链接并提交到GitHub"
    )
    parser.add_argument("repo_path", help="GitHub仓库的本地路径")
    parser.add_argument(
        "file_path", help="要修改的Markdown文件路径（相对于仓库根目录）"
    )
    parser.add_argument(
        "--link-id-1",
        default="7202424896",
        help="第一个链接ID（默认：7202424896）",
    )
    parser.add_argument(
        "--link-id-2",
        default="6294881820",
        help="第二个链接ID（默认：6294881820）",
    )
    parser.add_argument(
        "--min-interval", type=int, default=60, help="最小检查间隔（分钟，默认：60）"
    )
    parser.add_argument(
        "--max-interval", type=int, default=120, help="最大检查间隔（分钟，默认：120）"
    )

    args = parser.parse_args()

    try:
        updater = MarkdownLinkUpdater(
            repo_path=args.repo_path,
            file_path=args.file_path,
            link_id_1=args.link_id_1,
            link_id_2=args.link_id_2,
            interval_min=args.min_interval,
            interval_max=args.max_interval,
        )
        updater.run()

    except ValueError as e:
        print(f"配置错误: {e}")
        return 1
    except Exception as e:
        print(f"程序错误: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
