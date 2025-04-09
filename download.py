# -*- coding: utf-8 -*-
#devloper:不要倒卖！！！我辛辛苦苦做的辛辛苦苦搭建的，不是你们的赚钱工具！
import os
import sys
import ctypes
import requests
import platform
import time
from pathlib import Path
from urllib.parse import unquote, urlparse
from tqdm import tqdm

# ================= 配置区域 =================
DOWNLOAD_DIR = Path.home() / "Desktop" / "kaihuarchive"
TIMEOUT = 30
MAX_RETRIES = 3
GITHUB_URL = "https://github.com/renjiwinTECH/easyRDP"
URLS = [
    "不予泄露",
    "不予泄露",
    "不予泄露",
    "不予泄露",
    "不予泄露",
    "不予泄露",
    "不予泄露",
    "不予泄露",
    "不予泄露"
]


# ==========================================

def clear_screen():
    """清屏函数"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_color(text, color='white'):
    """彩色打印函数"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
    }
    end_color = '\033[0m'
    print(f"{colors.get(color, '')}{text}{end_color}")


def check_system():
    """检查系统版本"""
    system_info = platform.uname()

    if system_info.system != 'Windows':
        print_color("\n❌ 不支持的操作系统!", 'red')
        print_color("本软件仅支持Windows系统", 'yellow')
        return False

    try:
        # Windows 10/11 或 Server 2016+
        version_info = platform.platform().split('-')[2]  # 获取NT版本号
        version_num = float(version_info.split('.')[2])  # 10.0.xxxxx

        windows_10_threshold = 10.0  # Windows 10和Server 2016起始版本
        if version_num < windows_10_threshold:
            clear_screen()
            print_color("\n🤨 您的系统版本过低!", 'red')
            print_color("许多软件无法完美兼容!", 'yellow')
            print(f"最低要求: Windows 10 或 Windows Server 2016")
            print(f"当前系统: {platform.platform()}")
            print_color(f"请访问: {GITHUB_URL} 获取支持", 'cyan')
            input("\n按回车键退出...")
            return False
        return True

    except Exception as e:
        print_color(f"\n⚠️ 系统检测异常: {str(e)}", 'yellow')
        print("将继续尝试运行...")
        return True


def show_welcome():
    """显示欢迎界面"""
    clear_screen()
    print_color("✨ 欢迎使用 核心下载器 v2.0", 'magenta')
    print_color("=" * 50, 'blue')
    print_color("自动下载部署云共享机所需的所有软件\n仅需700MB即可完成基础部署", 'cyan')
    print("\n* 集成Office/QQ/微信/浏览器等必备工具")
    print("* 专为多人共享电脑环境优化")
    print("* (开源项目鼓励Star支持开发)")
    print_color("\n🐳 项目地址: " + GITHUB_URL, 'blue')
    print_color("🍵 免费软件 • 禁止倒卖 • 欢迎贡献", 'yellow')
    print_color("\n请喝杯咖啡等候... 下载后会自动安装配置", 'green')
    print_color("=" * 50 + "\n", 'blue')
    time.sleep(2)


def setup_download_dir():
    """创建下载目录"""
    try:
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # 测试写入权限
        test_file = DOWNLOAD_DIR / "download_test.tmp"
        test_file.touch()
        test_file.unlink()

        return True
    except Exception as e:
        print_color(f"❌ 目录创建失败: {str(e)}", 'red')
        return False


def get_filename_from_url(url):
    """从URL提取安全文件名"""
    filename = unquote(url)
    filename = filename.split(':0')[0]  # 去除:0结尾
    filename = os.path.basename(urlparse(filename).path)
    filename = filename.split('?')[0]  # 去除参数

    # Windows中文路径兼容处理
    if sys.platform == 'win32':
        try:
            filename = filename.encode('latin-1').decode('gbk')
        except:
            pass
    return filename


class DownloadManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })

    def check_existing(self, filepath, url):
        """检查文件是否已存在且完整"""
        if not filepath.exists():
            return False

        try:
            # 获取远程文件大小
            head = self.session.head(url, timeout=10)
            remote_size = int(head.headers.get('Content-Length', 0))

            # 对比本地文件
            local_size = os.path.getsize(filepath)
            return local_size == remote_size and remote_size > 0

        except:
            return False

    def download(self, url):
        """执行单文件下载"""
        filename = get_filename_from_url(url)
        save_path = DOWNLOAD_DIR / filename

        # 跳过已存在的完整文件
        if self.check_existing(save_path, url):
            print_color(f"✓ [已存在] {filename}", 'green')
            return True

        print_color(f"↓ 开始下载: {filename}", 'blue')

        for attempt in range(MAX_RETRIES):
            try:
                # 获取文件信息
                response = self.session.get(url, stream=True, timeout=TIMEOUT)
                response.raise_for_status()

                total_size = int(response.headers.get('Content-Length', 0))
                if total_size == 0:
                    raise ValueError("文件大小为0")

                # 绿色进度条配置
                progress = tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=filename[:30].ljust(30),
                    bar_format="{desc} {percentage:3.0f}%|\033[92m{bar:30}\033[0m| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
                    colour='GREEN'
                )

                downloaded = 0
                temp_path = save_path.with_suffix('.downloading')

                # 下载到临时文件
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # 过滤keep-alive空包
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress.update(len(chunk))

                # 重命名为最终文件
                temp_path.rename(save_path)
                progress.close()
                print_color(f"✓ 下载完成: {filename}", 'green')
                return True

            except KeyboardInterrupt:
                raise
            except Exception as e:
                progress.close() if 'progress' in locals() else None
                if attempt < MAX_RETRIES - 1:
                    time.sleep(3)
                    print_color(f"↻ 重试 {attempt + 1}/{MAX_RETRIES}: {filename}", 'yellow')
                    continue

                print_color(f"✗ 下载失败: {filename} - {str(e)[:50]}", 'red')
                if 'temp_path' in locals() and temp_path.exists():
                    temp_path.unlink()
                return False


def main():
    # 系统检查
    if not check_system():
        sys.exit(1)

    # 欢迎界面
    show_welcome()

    # 创建下载目录
    if not setup_download_dir():
        input("按回车键退出...")
        sys.exit(1)

    # 检查管理员权限
    try:
        import win32api
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    except:
        print_color("⚠️ 管理员权限检查失败，将继续运行", 'yellow')

    # 下载文件
    manager = DownloadManager()
    success, total = 0, len(URLS)

    for url in URLS:
        if manager.download(url):
            success += 1

    # 结果统计
    print("\n" + "=" * 50)
    if success == total:
        print_color("✨ 全部下载完成!", 'magenta')
        print("请按以下顺序安装:")
        print("1. Office/WPS\n2. QQ/微信\n3. 浏览器\n4. 其他工具")
    elif success == 0:
        print_color("\n🙈 下载全部失败!", 'red')
        print("可能原因:")
        print("- 网络连接问题")
        print("- 服务器不可用")
        print("- 系统权限限制")
    else:
        print_color(f"\n⚠️ 部分下载完成 ({success}/{total})", 'yellow')

    print_color(f"🎯 下载目录: {DOWNLOAD_DIR}", 'cyan')
    print_color(f"🐱 项目地址: {GITHUB_URL}\n", 'blue')

    if success < total:
        print_color("请检查网络后重试，或访问GitHub提交issue\n别忘了Star支持开发者!", 'yellow')

    input("按回车键退出...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n🛑 下载已被用户中断", 'red')
        sys.exit(0)
    except Exception as e:
        print_color(f"\n‼️ 致命错误: {str(e)}", 'red')
        sys.exit(1)