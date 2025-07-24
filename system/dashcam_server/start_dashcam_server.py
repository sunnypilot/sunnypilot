#!/usr/bin/env python3
"""
行车记录仪服务器启动脚本
自动检测并启动合适的服务器模式
"""

import os
import sys
import argparse
import logging
import asyncio
import signal
from pathlib import Path

from openpilot.common.params import Params
from openpilot.system.hardware.hw import Paths
from system.dashcam_server.dashcam_server import DashcamServer

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class DashcamServerManager:
    """行车记录仪服务器管理器"""

    def __init__(self):
        self.server = None
        self.params = Params()
        self.logger = logging.getLogger(__name__)
        self.running = False

    def setup_logging(self, debug: bool = False):
        """设置日志"""
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('/tmp/dashcam_server.log')
            ]
        )

    def check_prerequisites(self) -> bool:
        """检查运行前提条件"""
        # 检查日志目录是否存在
        log_root = Paths.log_root()
        if not os.path.exists(log_root):
            self.logger.error(f"日志目录不存在: {log_root}")
            return False

        # 检查是否有视频文件
        log_path = Path(log_root)
        has_videos = False
        for item in log_path.iterdir():
            if item.is_dir():
                for video_file in item.iterdir():
                    if video_file.suffix in {'.hevc', '.ts', '.mp4'}:
                        has_videos = True
                        break
                if has_videos:
                    break

        if not has_videos:
            self.logger.warning("未找到视频文件，服务器仍将启动")

        return True

    def create_server(self, port: int) -> DashcamServer:
        """创建服务器实例"""
        self.logger.info("启动标准Web服务器")
        return DashcamServer(port)

    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            self.logger.info(f"收到信号 {signum}，正在关闭服务器...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def start_server(self, port: int = 8082, debug: bool = False):
        """启动服务器"""
        self.setup_logging(debug)
        self.setup_signal_handlers()

        self.logger.info("正在启动行车记录仪服务器...")

        # 检查前提条件
        if not self.check_prerequisites():
            self.logger.error("前提条件检查失败")
            return False

        try:
            # 创建服务器
            self.server = self.create_server(port)

            # 启动服务器
            await self.server.start_server()
            self.running = True

            self.logger.info(f"服务器已启动在端口 {port}")
            self.logger.info(f"移动端界面: http://localhost:{port}")

            # 保存服务器状态到参数
            try:
                self.params.put("DashcamServerRunning", "1")
                self.params.put("DashcamServerPort", str(port))
            except Exception as e:
                self.logger.warning(f"无法保存参数状态: {e}")
                # 继续运行，不影响服务器功能

            # 保持运行
            while self.running:
                await asyncio.sleep(1)

            return True

        except Exception as e:
            self.logger.error(f"启动服务器失败: {e}")
            return False
        finally:
            # 清理
            try:
                self.params.put("DashcamServerRunning", "0")
            except Exception as e:
                self.logger.warning(f"无法清理参数状态: {e}")
            self.logger.info("服务器已停止")

    def get_server_status(self) -> dict:
        """获取服务器状态"""
        running = self.params.get("DashcamServerRunning") == b"1"
        port = self.params.get("DashcamServerPort")

        return {
            'running': running,
            'port': int(port) if port else None,
            'log_root': Paths.log_root(),
            'pid': os.getpid() if running else None
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="行车记录仪服务器")
    parser.add_argument('--port', type=int, default=8082, help='服务器端口 (默认: 8082)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--status', action='store_true', help='显示服务器状态')
    parser.add_argument('--stop', action='store_true', help='停止运行中的服务器')

    args = parser.parse_args()

    manager = DashcamServerManager()

    # 显示状态
    if args.status:
        status = manager.get_server_status()
        print("行车记录仪服务器状态:")
        print(f"  运行状态: {'运行中' if status['running'] else '已停止'}")
        if status['port']:
            print(f"  端口: {status['port']}")
        if status['pid']:
            print(f"  进程ID: {status['pid']}")
        print(f"  日志目录: {status['log_root']}")
        return

    # 停止服务器
    if args.stop:
        params = Params()
        params.put("DashcamServerRunning", "0")
        print("已发送停止信号")
        return

    # 启动服务器
    try:
        success = asyncio.run(manager.start_server(
            port=args.port,
            debug=args.debug
        ))

        if not success:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
