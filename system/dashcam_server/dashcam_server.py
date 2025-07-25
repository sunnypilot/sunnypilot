#!/usr/bin/env python3
"""
行车记录仪查看服务器
支持Web和移动端客户端访问行车记录仪视频
"""

import os
import json
import asyncio
import logging
import tempfile
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

from aiohttp import web, WSMsgType
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web import StreamResponse

from openpilot.system.hardware.hw import Paths
from openpilot.common.params import Params
from openpilot.system.loggerd.config import SEGMENT_LENGTH

SEGMENT_LENGTH = 60  # 默认段长度60秒

# 配置
DEFAULT_PORT = 8009
VIDEO_EXTENSIONS = {'.hevc', '.ts', '.mp4'}
SUPPORTED_CAMERAS = ['fcamera', 'dcamera', 'ecamera', 'qcamera']

@dataclass
class VideoSegment:
    """视频段信息"""
    segment_id: str
    route_name: str
    segment_num: int
    timestamp: datetime
    duration: int
    cameras: Dict[str, str]  # camera_type -> file_path
    size: int
    has_audio: bool

@dataclass
class RouteInfo:
    """路线信息"""
    route_name: str
    start_time: datetime
    end_time: datetime
    segment_count: int
    total_size: int
    available_cameras: List[str]
    segments: List[VideoSegment]

@dataclass
class DashcamInfo:
    """行车记录仪信息"""
    total_routes: int
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
            self.logger.warning(f"日志目录不存在: {self.log_root}")
            return segments

        # 遍历所有目录
        for segment_dir in self.log_root.iterdir():
            if not segment_dir.is_dir():
                continue

            # 解析目录名格式: <index>--<route_name>--<segment_num>
            try:
                parts = segment_dir.name.split('--')
                if len(parts) != 3:
                    self.logger.debug(f"跳过格式不匹配的目录: {segment_dir.name}")
                    continue

                route_name = parts[1]
                segment_num = int(parts[2])

                # 使用目录的修改时间作为这个segment的时间戳
                # 这样可以反映实际的文件创建时间，而不是推算的时间
                dir_stat = segment_dir.stat()
                timestamp = datetime.fromtimestamp(dir_stat.st_mtime)

                segment = self._parse_segment_dir(segment_dir, route_name, segment_num, timestamp)
                if segment:
                    segments.append(segment)

            except (ValueError, IndexError) as e:
                self.logger.debug(f"跳过无效目录 {segment_dir.name}: {e}")
                continue

        return sorted(segments, key=lambda x: (x.route_name, x.segment_num))

    def _parse_segment_dir(self, segment_dir: Path, route_name: str, segment_num: int, timestamp: datetime) -> Optional[VideoSegment]:
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
            route_name=route_name,
            segment_num=segment_num,
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
            # 从目录名解析信息: <index>--<route_name>--<segment_num>
            parts = segment_id.split('--')
            if len(parts) != 3:
                return None

            route_name = parts[1]
            segment_num = int(parts[2])

            # 使用目录的修改时间作为时间戳
            dir_stat = segment_path.stat()
            timestamp = datetime.fromtimestamp(dir_stat.st_mtime)

            return self._parse_segment_dir(segment_path, route_name, segment_num, timestamp)
        except (ValueError, IndexError):
            return None

    def get_routes(self) -> List[RouteInfo]:
        """获取所有路线信息"""
        segments = self.scan_segments()
        routes_dict = {}

        # 按route_name分组
        for segment in segments:
            route_name = segment.route_name
            if route_name not in routes_dict:
                routes_dict[route_name] = []
            routes_dict[route_name].append(segment)

        routes = []
        for route_name, route_segments in routes_dict.items():
            # 按segment_num排序
            route_segments.sort(key=lambda x: x.segment_num)

            # 计算路线信息 - 使用实际的最小和最大时间戳
            timestamps = [seg.timestamp for seg in route_segments]
            start_time = min(timestamps)
            end_time = max(timestamps) + timedelta(seconds=SEGMENT_LENGTH)  # 最后一段的结束时间
            total_size = sum(seg.size for seg in route_segments)

            # 获取所有可用摄像头
            all_cameras = set()
            for seg in route_segments:
                all_cameras.update(seg.cameras.keys())

            routes.append(RouteInfo(
                route_name=route_name,
                start_time=start_time,
                end_time=end_time,
                segment_count=len(route_segments),
                total_size=total_size,
                available_cameras=sorted(all_cameras),
                segments=route_segments
            ))

        # 按开始时间排序，最新的在前
        return sorted(routes, key=lambda x: x.start_time, reverse=True)

    def get_route_by_name(self, route_name: str) -> Optional[RouteInfo]:
        """根据名称获取路线信息"""
        routes = self.get_routes()
        for route in routes:
            if route.route_name == route_name:
                return route
        return None

    def get_dashcam_info(self) -> DashcamInfo:
        """获取行车记录仪总体信息"""
        routes = self.get_routes()

        if not routes:
            return DashcamInfo(
                total_routes=0,
                total_segments=0,
                total_size=0,
                available_cameras=[],
                date_range=(datetime.now(), datetime.now())
            )

        total_segments = sum(route.segment_count for route in routes)
        total_size = sum(route.total_size for route in routes)
        all_cameras = set()
        for route in routes:
            all_cameras.update(route.available_cameras)

        # 获取时间范围
        earliest_time = min(route.start_time for route in routes)
        latest_time = max(route.end_time for route in routes)

        return DashcamInfo(
            total_routes=len(routes),
            total_segments=total_segments,
            total_size=total_size,
            available_cameras=sorted(all_cameras),
            date_range=(earliest_time, latest_time)
        )

class DashcamServer:
    """行车记录仪服务器"""

    def __init__(self, port: int = DEFAULT_PORT, log_root: str = None):
        self.port = port
        if log_root is None:
          log_root = Paths.log_root()
        self.file_manager = VideoFileManager(log_root)
        self.app = web.Application()
        self.logger = logging.getLogger(__name__)
        # HLS临时文件目录
        self.hls_temp_dir = Path(tempfile.gettempdir()) / "dashcam_hls"
        self.hls_temp_dir.mkdir(exist_ok=True)
        # HLS缓存管理 - 简单的文件缓存，不需要session
        self.hls_cache = {}  # f"{segment_id}_{camera}" -> {path, created_time}
        self._setup_routes()
        # 启动清理任务
        asyncio.create_task(self._cleanup_hls_cache())

    def _setup_routes(self):
        """设置路由"""
        # API路由
        self.app.router.add_get('/api/info', self.get_dashcam_info)
        self.app.router.add_get('/api/routes', self.get_routes)
        self.app.router.add_get('/api/routes/{route_name}', self.get_route_detail)
        self.app.router.add_get('/api/segments', self.get_segments)
        self.app.router.add_get('/api/segments/{segment_id}', self.get_segment_detail)
        # HLS视频流路由
        self.app.router.add_get('/api/hls/{segment_id}/{camera}/playlist.m3u8', self.get_hls_playlist)
        self.app.router.add_get('/api/hls/{segment_id}/{camera}/{filename}', self.get_hls_segment)
        # 保留原有的直接视频流路由作为备用
        self.app.router.add_get('/api/video/{segment_id}/{camera}', self.stream_video)

        # 静态文件服务
        static_path = Path(__file__).parent / 'web'
        self.app.router.add_static('/css', static_path / 'css', name='css')
        self.app.router.add_static('/js', static_path / 'js', name='js')
        self.app.router.add_static('/webfonts', static_path / 'webfonts', name='webfonts')
        self.app.router.add_get('/', self.route_view_handler)
        self.app.router.add_get('/mobile.html', self.mobile_handler)
        self.app.router.add_get('/mobile_routes.html', self.route_view_handler)
        self.app.router.add_get('/route_player.html', self.route_player_handler)

    async def route_demo_handler(self, request):
        static_path = Path(__file__).parent / 'web' / 'demo.html'
        return FileResponse(static_path)

    async def test_hls_handler(self, request):
        """HLS测试页面处理"""
        static_path = Path(__file__).parent / 'web' / 'test_hls.html'
        return FileResponse(static_path)

    async def mobile_handler(self, request):
        """移动端页面处理"""
        static_path = Path(__file__).parent / 'web' / 'mobile.html'
        return FileResponse(static_path)

    async def route_view_handler(self, request):
        """路线视图页面处理"""
        static_path = Path(__file__).parent / 'web' / 'mobile_routes.html'
        return FileResponse(static_path)

    async def route_player_handler(self, request):
        """路线播放器页面处理"""
        static_path = Path(__file__).parent / 'web' / 'route_player.html'
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

    async def get_routes(self, request):
        """获取路线列表API"""
        try:
            # 分页参数
            page = int(request.query.get('page', 1))
            limit = int(request.query.get('limit', 20))

            # 日期过滤
            start_date = request.query.get('start_date')
            end_date = request.query.get('end_date')

            routes = self.file_manager.get_routes()

            # 日期过滤
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                routes = [r for r in routes if r.start_time >= start_dt]

            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                routes = [r for r in routes if r.end_time <= end_dt]

            # 分页
            total = len(routes)
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            page_routes = routes[start_idx:end_idx]

            # 转换为可序列化的格式
            serializable_routes = []
            for route in page_routes:
                route_dict = asdict(route)
                # 转换datetime为字符串
                route_dict['start_time'] = route.start_time.isoformat()
                route_dict['end_time'] = route.end_time.isoformat()
                # 不包含segments详情，只包含基本信息
                route_dict.pop('segments', None)
                serializable_routes.append(route_dict)

            return web.json_response({
                'routes': serializable_routes,
                'total': total,
                'page': page,
                'limit': limit,
                'has_next': end_idx < total
            })

        except Exception as e:
            self.logger.error(f"获取路线列表失败: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def get_route_detail(self, request):
        """获取路线详情API"""
        route_name = request.match_info['route_name']

        try:
            route = self.file_manager.get_route_by_name(route_name)
            if not route:
                return web.json_response({'error': '路线不存在'}, status=404)

            # 转换为可序列化的格式
            route_dict = asdict(route)
            route_dict['start_time'] = route.start_time.isoformat()
            route_dict['end_time'] = route.end_time.isoformat()

            # 转换segments
            serializable_segments = []
            for seg in route.segments:
                seg_dict = asdict(seg)
                seg_dict['timestamp'] = seg.timestamp.isoformat()
                serializable_segments.append(seg_dict)

            route_dict['segments'] = serializable_segments

            return web.json_response(route_dict)

        except Exception as e:
            self.logger.error(f"获取路线详情失败: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def get_segments(self, request):
        """获取视频段列表API"""
        try:
            # 分页参数
            page = int(request.query.get('page', 1))
            limit = int(request.query.get('limit', 20))

            # 过滤参数
            start_date = request.query.get('start_date')
            end_date = request.query.get('end_date')
            route_name = request.query.get('route_name')

            segments = self.file_manager.scan_segments()

            # 路线过滤
            if route_name:
                segments = [s for s in segments if s.route_name == route_name]

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

    async def get_hls_playlist(self, request):
        """获取HLS播放列表"""
        segment_id = request.match_info['segment_id']
        camera = request.match_info['camera']

        segment = self.file_manager.get_segment_by_id(segment_id)
        if not segment or camera not in segment.cameras:
            return web.json_response({'error': '视频文件不存在'}, status=404)

        video_path = segment.cameras[camera]
        if not Path(video_path).exists():
            return web.json_response({'error': '视频文件不存在'}, status=404)

        # 使用segment_id和camera作为唯一标识
        cache_key = f"{segment_id}_{camera}"

        # 检查是否已经生成过HLS文件
        if cache_key in self.hls_cache:
            cache_dir = self.hls_cache[cache_key]['path']
            playlist_path = cache_dir / "playlist.m3u8"

            if playlist_path.exists():
                # 更新访问时间
                self.hls_cache[cache_key]['last_access'] = time.time()

                # 读取并返回播放列表
                with open(playlist_path, 'r') as f:
                    playlist_content = f.read()

                return web.Response(
                    text=playlist_content,
                    content_type='application/vnd.apple.mpegurl',
                    headers={
                        'Access-Control-Allow-Origin': '*',
                        'Cache-Control': 'no-cache'
                    }
                )

        # 生成新的HLS文件
        cache_dir = self.hls_temp_dir / cache_key
        cache_dir.mkdir(exist_ok=True)
        playlist_path = cache_dir / "playlist.m3u8"

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-f", "hls",
            "-hls_time", "6",  # 每个段6秒
            "-hls_list_size", "0",  # 保留所有段
            "-hls_segment_filename", str(cache_dir / "segment_%03d.ts"),
            "-y",  # 覆盖输出文件
            str(playlist_path)
        ]

        # 如果没有音频，移除音频流
        if not segment.has_audio:
            cmd.extend(["-an"])

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )

            # 等待FFmpeg完成
            await proc.wait()

            # 检查播放列表是否生成
            if not playlist_path.exists():
                return web.json_response({'error': 'HLS生成失败'}, status=500)

            # 保存缓存信息
            self.hls_cache[cache_key] = {
                'path': cache_dir,
                'created_time': time.time(),
                'last_access': time.time()
            }

            # 读取并返回播放列表
            with open(playlist_path, 'r') as f:
                playlist_content = f.read()

            return web.Response(
                text=playlist_content,
                content_type='application/vnd.apple.mpegurl',
                headers={
                    'Access-Control-Allow-Origin': '*',
                    'Cache-Control': 'no-cache'
                }
            )

        except Exception as e:
            self.logger.error(f"HLS生成失败: {e}")
            return web.json_response({'error': 'HLS生成失败'}, status=500)

    async def get_hls_segment(self, request):
        """获取HLS视频段"""
        segment_id = request.match_info['segment_id']
        camera = request.match_info['camera']
        filename = request.match_info['filename']

        # 使用segment_id和camera作为缓存键
        cache_key = f"{segment_id}_{camera}"

        if cache_key not in self.hls_cache:
            return web.json_response({'error': 'HLS缓存不存在'}, status=404)

        cache_dir = self.hls_cache[cache_key]['path']
        file_path = cache_dir / filename

        if not file_path.exists():
            return web.json_response({'error': 'HLS段文件不存在'}, status=404)

        # 更新访问时间
        self.hls_cache[cache_key]['last_access'] = time.time()

        return FileResponse(
            file_path,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'video/mp2t'
            }
        )

    async def stream_video(self, request):
        """原有的直接视频流方法，作为备用"""
        segment_id = request.match_info['segment_id']
        camera = request.match_info['camera']
        segment = self.file_manager.get_segment_by_id(segment_id)

        if not segment or camera not in segment.cameras:
            return web.json_response({'error': '视频文件不存在'}, status=404)

        video_path = segment.cameras[camera]
        if not Path(video_path).exists():
            return web.json_response({'error': '视频文件不存在'}, status=404)

        # 启动 ffmpeg 子进程，实时转码
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-f", "mp4",
            "-vcodec", "libx264",
            "-preset", "ultrafast",
            "-g", "48",  # 关键帧间隔
            "-movflags", "frag_keyframe+default_base_moof",
            "-an",
            "pipe:1"
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )

        resp = StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': 'video/mp4',
                'Transfer-Encoding': 'chunked',
            }
        )
        await resp.prepare(request)

        try:
            while True:
                chunk = await proc.stdout.read(8192)
                if not chunk:
                    break
                await resp.write(chunk)
        finally:
            await proc.wait()

        return resp

    async def _cleanup_hls_cache(self):
        """清理过期的HLS缓存"""
        while True:
            try:
                current_time = time.time()
                expired_caches = []

                for cache_key, cache_info in self.hls_cache.items():
                    # 如果缓存超过2小时未访问，标记为过期
                    if current_time - cache_info['last_access'] > 7200:
                        expired_caches.append(cache_key)

                for cache_key in expired_caches:
                    cache_info = self.hls_cache.pop(cache_key)

                    # 删除临时文件
                    if cache_info['path'].exists():
                        try:
                            shutil.rmtree(cache_info['path'])
                        except:
                            pass

                    self.logger.info(f"清理过期HLS缓存: {cache_key}")

            except Exception as e:
                self.logger.error(f"清理HLS缓存失败: {e}")

            # 每10分钟清理一次
            await asyncio.sleep(600)

    async def start_server(self):
        """启动服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()

        self.logger.info(f"行车记录仪服务器启动在端口 {self.port}")
        print(f"行车记录仪服务器启动在 http://0.0.0.0:{self.port}")
        print(f"行车记录仪服务器启动在 http://localhost:{self.port}")


async def main():
  params = Params()
  params.put("DashcamServerPid", str(os.getpid()))
  port = int(params.get("DashcamServerPort", encoding='utf-8'))

  logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join("/tmp/", "dashcam_server.log"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )

  server = DashcamServer(port=port)
  await server.start_server()

  # 用 asyncio.Event() 代替 sleep 循环，让任务优雅持久运行
  await asyncio.Event().wait()


if __name__ == '__main__':
  try:
    asyncio.run(main())
  except (KeyboardInterrupt, SystemExit):
    print("行车记录仪服务器已停止")
