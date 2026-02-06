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
        repo_path: "https://github.com/itgoyo/TelegramGroup.git",
        file_path: "README.md",
        old_link: "https://t.me/jiso?start=a_7202424896",
        new_link: "https://t.me/jiso?start=a_6294881820",
        interval_min: int = 60,
        interval_max: int = 120,
    ):
        """
        初始化链接更新器

        Args:
            repo_path: GitHub仓库本地路径
            file_path: 要修改的Markdown文件路径（相对于仓库根目录）
            old_link: 要替换的旧链接
            new_link: 替换后的新链接
            interval_min: 最小检查间隔（分钟）
            interval_max: 最大检查间隔（分钟）
        """
        self.repo_path = Path(repo_path).resolve()
        self.file_path = self.repo_path / file_path
        self.old_link = old_link
        self.new_link = new_link
        self.interval_min = interval_min
        self.interval_max = interval_max

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

    def _check_changes(self) -> bool:
        """检查工作区是否有未提交的更改"""
        status = self._run_git_command(["git", "status"])
        return "Changes not staged for commit" in status or "Untracked files" in status

    def _update_links(self) -> bool:
        """
        检查并更新Markdown文件中的链接

        Returns:
            是否成功更新了文件
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if self.old_link not in content:
                print(f"未找到需要替换的链接: {self.old_link}")
                return False

            updated_content = content.replace(self.old_link, self.new_link)

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            print(f"成功替换链接: {self.old_link} -> {self.new_link}")
            return True

        except Exception as e:
            print(f"更新文件失败: {e}")
            return False

    def _commit_changes(self) -> bool:
        """提交更改到本地仓库"""
        try:
            self._run_git_command(["git", "add", str(self.file_path)])
            commit_msg = (
                f"自动更新Telegram链接 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
            )
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
        print(f"=== Telegram链接自动更新器 ===")
        print(f"仓库: {self.repo_path}")
        print(f"文件: {self.file_path}")
        print(f"替换: {self.old_link} -> {self.new_link}")
        print(f"检查间隔: {self.interval_min}-{self.interval_max}分钟")
        print("-" * 50)

        try:
            while True:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{current_time}] 开始检查...")

                # 检查Git状态
                if self._check_changes():
                    print("警告: 工作区有未提交的更改，跳过此轮检查")
                else:
                    # 检查并更新链接
                    if self._update_links():
                        # 提交和推送
                        if self._commit_changes():
                            self._push_to_remote()
                    else:
                        print("不需要更新")

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
        "--old-link",
        default="https://t.me/jiso?start=a_7202424896",
        help="要替换的旧链接（默认：https://t.me/jiso?start=a_7202424896）",
    )
    parser.add_argument(
        "--new-link",
        default="https://t.me/jiso?start=a_6294881820",
        help="替换后的新链接（默认：https://t.me/jiso?start=a_6294881820）",
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
            old_link=args.old_link,
            new_link=args.new_link,
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
