#!/usr/bin/env python3
"""
行车记录仪查看服务器
支持Web和移动端客户端访问行车记录仪视频
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

from aiohttp import web, WSMsgType
from aiohttp.web_fileresponse import FileResponse

from openpilot.system.hardware.hw import Paths
from openpilot.common.params import Params
from openpilot.system.loggerd.config import SEGMENT_LENGTH

# 配置
DEFAULT_PORT = 8008
VIDEO_EXTENSIONS = {'.hevc', '.ts', '.mp4'}
SUPPORTED_CAMERAS = ['fcamera', 'dcamera', 'ecamera', 'qcamera']

@dataclass
class VideoSegment:
    """视频段信息"""
    segment_id: str
    timestamp: datetime
    duration: int
    cameras: Dict[str, str]  # camera_type -> file_path
    size: int
    has_audio: bool

@dataclass
class DashcamInfo:
    """行车记录仪信息"""
    total_segments: int
    total_size: int
    available_cameras: List[str]
    date_range: Tuple[datetime, datetime]

class VideoFileManager:
    """视频文件管理器"""

    def __init__(self, log_root: str):
        self.log_root = Path(log_root)
        self.params = Params()
        self.logger = logging.getLogger(__name__)

    def scan_segments(self) -> List[VideoSegment]:
        """扫描所有视频段"""
        segments = []

        if not self.log_root.exists():
            print("test")
            return segments

        # 遍历所有日期目录
        for date_dir in self.log_root.iterdir():
            if not date_dir.is_dir():
                continue

            # 解析目录名格式: dongle_id|timestamp--segment_num
            try:
                dir_parts = date_dir.name.split('|')
                if len(dir_parts) != 2:
                    continue

                parts = dir_parts[1].split('--')
                if len(parts) < 3:
                  continue
                timestamp_part = '--'.join(parts[:2])  # "2025-07-24--11-50-10"
                timestamp = datetime.strptime(timestamp_part, '%Y-%m-%d--%H-%M-%S')

                segment = self._parse_segment_dir(date_dir, timestamp)
                if segment:
                    segments.append(segment)

            except (ValueError, IndexError) as e:
                self.logger.debug(f"跳过无效目录 {date_dir.name}: {e}")
                continue

        return sorted(segments, key=lambda x: x.timestamp, reverse=True)

    def _parse_segment_dir(self, segment_dir: Path, timestamp: datetime) -> Optional[VideoSegment]:
        """解析单个段目录"""
        cameras = {}
        total_size = 0
        has_audio = False

        # 扫描视频文件
        for file_path in segment_dir.iterdir():
            if file_path.suffix not in VIDEO_EXTENSIONS:
                continue

            file_name = file_path.stem
            if file_name in SUPPORTED_CAMERAS:
                cameras[file_name] = str(file_path)
                total_size += file_path.stat().st_size

                # 检查是否有音频（qcamera通常包含音频）
                if file_name == 'qcamera':
                    has_audio = True

        if not cameras:
            return None

        return VideoSegment(
            segment_id=segment_dir.name,
            timestamp=timestamp,
            duration=SEGMENT_LENGTH,
            cameras=cameras,
            size=total_size,
            has_audio=has_audio
        )

    def get_segment_by_id(self, segment_id: str) -> Optional[VideoSegment]:
        """根据ID获取视频段"""
        segment_path = self.log_root / segment_id
        if not segment_path.exists():
            return None

        try:
            # 从目录名解析时间戳
            dir_parts = segment_id.split('|')
            if len(dir_parts) != 2:
                return None

            parts = dir_parts[1].split('--')
            if len(parts) < 3:
              return None
            timestamp_part = '--'.join(parts[:2])
            timestamp = datetime.strptime(timestamp_part, '%Y-%m-%d--%H-%M-%S')

            return self._parse_segment_dir(segment_path, timestamp)
        except (ValueError, IndexError):
            return None

    def get_dashcam_info(self) -> DashcamInfo:
        """获取行车记录仪总体信息"""
        segments = self.scan_segments()

        if not segments:
            return DashcamInfo(
                total_segments=0,
                total_size=0,
                available_cameras=[],
                date_range=(datetime.now(), datetime.now())
            )

        total_size = sum(seg.size for seg in segments)
        all_cameras = set()
        for seg in segments:
            all_cameras.update(seg.cameras.keys())

        return DashcamInfo(
            total_segments=len(segments),
            total_size=total_size,
            available_cameras=sorted(all_cameras),
            date_range=(segments[-1].timestamp, segments[0].timestamp)
        )

class DashcamServer:
    """行车记录仪服务器"""

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        log_root = Paths.log_root()
        self.file_manager = VideoFileManager(log_root)
        self.app = web.Application()
        self.logger = logging.getLogger(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """设置路由"""
        # API路由
        self.app.router.add_get('/api/info', self.get_dashcam_info)
        self.app.router.add_get('/api/segments', self.get_segments)
        self.app.router.add_get('/api/segments/{segment_id}', self.get_segment_detail)
        self.app.router.add_get('/api/video/{segment_id}/{camera}', self.stream_video)

        # WebSocket for real-time updates
        self.app.router.add_get('/ws', self.websocket_handler)

        # 静态文件服务
        static_path = Path(__file__).parent / 'web'
        self.app.router.add_static('/css', static_path / 'css', name='css')
        self.app.router.add_static('/js', static_path / 'js', name='js')
        self.app.router.add_get('/', self.mobile_handler)
        self.app.router.add_get('/mobile.html', self.mobile_handler)

    async def mobile_handler(self, request):
        """移动端页面处理"""
        static_path = Path(__file__).parent / 'web' / 'mobile.html'
        return FileResponse(static_path)

    async def get_dashcam_info(self, request):
        """获取行车记录仪信息API"""
        try:
            info = self.file_manager.get_dashcam_info()
            info_dict = asdict(info)

            # 转换datetime为字符串
            if 'date_range' in info_dict and info_dict['date_range']:
                info_dict['date_range'] = [
                    info_dict['date_range'][0].isoformat() if info_dict['date_range'][0] else None,
                    info_dict['date_range'][1].isoformat() if info_dict['date_range'][1] else None
                ]

            return web.json_response(info_dict)
        except Exception as e:
            self.logger.error(f"获取行车记录仪信息失败: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def get_segments(self, request):
        """获取视频段列表API"""
        try:
            # 分页参数
            page = int(request.query.get('page', 1))
            limit = int(request.query.get('limit', 20))

            # 日期过滤
            start_date = request.query.get('start_date')
            end_date = request.query.get('end_date')

            segments = self.file_manager.scan_segments()

            # 日期过滤
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                segments = [s for s in segments if s.timestamp >= start_dt]

            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                segments = [s for s in segments if s.timestamp <= end_dt]

            # 分页
            total = len(segments)
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            page_segments = segments[start_idx:end_idx]

            # 转换segments为可序列化的格式
            serializable_segments = []
            for seg in page_segments:
                seg_dict = asdict(seg)
                # 转换datetime为字符串
                seg_dict['timestamp'] = seg.timestamp.isoformat()
                serializable_segments.append(seg_dict)

            return web.json_response({
                'segments': serializable_segments,
                'total': total,
                'page': page,
                'limit': limit,
                'has_next': end_idx < total
            })

        except Exception as e:
            self.logger.error(f"获取视频段列表失败: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def get_segment_detail(self, request):
        """获取视频段详情API"""
        segment_id = request.match_info['segment_id']

        try:
            segment = self.file_manager.get_segment_by_id(segment_id)
            if not segment:
                return web.json_response({'error': '视频段不存在'}, status=404)

            # 转换为可序列化的格式
            segment_dict = asdict(segment)
            segment_dict['timestamp'] = segment.timestamp.isoformat()

            return web.json_response(segment_dict)

        except Exception as e:
            self.logger.error(f"获取视频段详情失败: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def stream_video(self, request):
        """视频流API"""
        segment_id = request.match_info['segment_id']
        camera = request.match_info['camera']

        try:
            segment = self.file_manager.get_segment_by_id(segment_id)
            if not segment or camera not in segment.cameras:
                return web.json_response({'error': '视频文件不存在'}, status=404)

            video_path = Path(segment.cameras[camera])
            if not video_path.exists():
                return web.json_response({'error': '视频文件不存在'}, status=404)

            # 检查用户代理，判断是否为移动设备
            user_agent = request.headers.get('User-Agent', '').lower()
            is_mobile = any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipad'])

            # 检查是否需要转换格式
            file_ext = video_path.suffix.lower()

            if is_mobile and file_ext == '.hevc':
                # 移动端不支持HEVC，返回转换提示或使用qcamera
                if 'qcamera' in segment.cameras:
                    # 重定向到qcamera（通常是.ts格式，兼容性更好）
                    qcamera_path = Path(segment.cameras['qcamera'])
                    return FileResponse(
                        qcamera_path,
                        headers={
                            'Accept-Ranges': 'bytes',
                            'Content-Type': 'video/mp2t',
                            'X-Fallback-Camera': 'qcamera'
                        }
                    )
                else:
                    return web.json_response({
                        'error': '移动设备不支持HEVC格式，请使用qcamera或等待转换功能'
                    }, status=415)

            # 设置正确的Content-Type
            if file_ext == '.ts':
                content_type = 'video/mp2t'
            elif file_ext == '.hevc':
                content_type = 'video/mp4'  # 某些浏览器可能支持
            elif file_ext == '.mp4':
                content_type = 'video/mp4'
            else:
                content_type = 'application/octet-stream'

            # 支持Range请求用于视频流
            return FileResponse(
                video_path,
                headers={
                    'Accept-Ranges': 'bytes',
                    'Content-Type': content_type,
                    'X-Original-Format': file_ext
                }
            )

        except Exception as e:
            self.logger.error(f"视频流失败: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def websocket_handler(self, request):
        """WebSocket处理器"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self._handle_ws_message(ws, data)
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket错误: {ws.exception()}')
        except Exception as e:
            self.logger.error(f'WebSocket处理错误: {e}')

        return ws

    async def _handle_ws_message(self, ws, data):
        """处理WebSocket消息"""
        msg_type = data.get('type')

        if msg_type == 'ping':
            await ws.send_str(json.dumps({'type': 'pong'}))
        elif msg_type == 'subscribe_updates':
            # 实现实时更新订阅
            pass

    async def start_server(self):
        """启动服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()

        self.logger.info(f"行车记录仪服务器启动在端口 {self.port}")
        print(f"行车记录仪服务器启动在 http://0.0.0.0:{self.port}")


async def main():
  logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join("/tmp/", "dashcam_server.log"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )

  server = DashcamServer()
  await server.start_server()

  # 用 asyncio.Event() 代替 sleep 循环，让任务优雅持久运行
  await asyncio.Event().wait()


if __name__ == '__main__':
  try:
    asyncio.run(main())
  except (KeyboardInterrupt, SystemExit):
    print("行车记录仪服务器已停止")
