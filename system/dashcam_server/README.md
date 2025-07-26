# 行车记录仪查看器

这是一个为 openpilot/sunnypilot 开发的行车记录仪查看接口，支持通过Web浏览器和移动设备查看录制的行车视频。

## 功能特性

### 🎥 多摄像头支持
- **前置摄像头 (fcamera)**: 主要道路视图，高质量HEVC编码
- **驾驶员摄像头 (dcamera)**: 驾驶员监控视图
- **广角摄像头 (ecamera)**: 广角道路视图
- **低质量摄像头 (qcamera)**: 包含音频的低质量视图

### 🌐 多客户端支持
- **Web界面**: 完整功能的桌面浏览器界面
- **移动端界面**: 针对手机优化的响应式界面
- **API接口**: RESTful API支持第三方应用集成

### 📱 核心功能
- 视频段浏览和搜索
- 实时视频播放
- 日期范围筛选
- 摄像头类型筛选
- 视频下载
- 系统信息显示
- WebSocket实时更新

## 安装和使用

### 1. 启动服务器

#### 基本启动
```bash
cd /path/to/openpilot
python system/dashcam_server/start_dashcam_server.py
```

#### 高级选项
```bash
# 指定端口
python system/dashcam_server/start_dashcam_server.py --port 8080

# 启用调试模式
python system/dashcam_server/start_dashcam_server.py --debug

# 查看服务器状态
python system/dashcam_server/start_dashcam_server.py --status

# 停止服务器
python system/dashcam_server/start_dashcam_server.py --stop
```

### 2. 访问界面

#### Web界面
打开浏览器访问: `http://设备IP:8082`

#### 从设置界面访问
在 sunnypilot 设置中找到"行车记录仪查看器"按钮，点击"打开"即可。

## API 接口

### 标准API

#### 获取系统信息
```
GET /api/info
```

#### 获取视频段列表
```
GET /api/segments?page=1&limit=20&start_date=2024-01-01&end_date=2024-01-31&camera=fcamera
```

#### 获取视频段详情
```
GET /api/segments/{segment_id}
```

#### 视频流
```
GET /api/video/{segment_id}/{camera}
```

### 移动端API

#### 获取移动端优化的系统信息
```
GET /api/mobile/info
```

#### 获取移动端优化的视频段列表
```
GET /api/mobile/segments?page=1&limit=10
```

#### 获取视频段详情
```
GET /api/mobile/segments/{segment_id}
```

#### 获取缩略图
```
GET /api/mobile/thumbnail/{segment_id}
```

#### 视频流
```
GET /api/mobile/stream/{segment_id}/{camera}
```

#### 视频下载
```
GET /api/mobile/download/{segment_id}/{camera}
```

## 文件结构

```
system/dashcam_server/
├── dashcam_server.py          # 主服务器
├── mobile_api.py              # 移动端API
├── start_dashcam_server.py    # 启动脚本
├── web/                       # Web界面文件
│   ├── index.html            # 主界面
│   ├── mobile.html           # 移动端界面
│   ├── css/
│   │   └── style.css         # 样式文件
│   └── js/
│       └── dashcam.js        # JavaScript逻辑
└── README.md                  # 说明文档
```

## 配置要求

### 系统要求
- Python 3.8+
- aiohttp
- aiofiles
- openpilot/sunnypilot 环境

### 网络要求
- 设备需要在同一网络中
- 默认端口: 8082 (可配置)
- 支持WebSocket连接

### 存储要求
- 视频文件存储在 `/data/media/0/realdata/` (设备)
- 或 `~/.comma/media/0/realdata/` (PC)

## 使用说明

### Web界面使用

1. **浏览视频段**: 在主界面查看所有录制的视频段
2. **筛选视频**: 使用日期范围和摄像头类型筛选
3. **播放视频**: 点击"播放"按钮观看视频
4. **切换摄像头**: 在播放界面切换不同摄像头视角
5. **查看详情**: 点击"详情"按钮查看视频段详细信息

### 移动端使用

1. **触摸友好**: 针对触摸屏优化的界面
2. **响应式设计**: 自适应不同屏幕尺寸
3. **简化操作**: 精简的功能布局
4. **离线缓存**: 支持基本的离线浏览

### API集成

开发者可以使用提供的RESTful API集成到自己的应用中:

```python
import requests

# 获取系统信息
response = requests.get('http://device-ip:8082/api/info')
info = response.json()

# 获取视频段列表
response = requests.get('http://device-ip:8082/api/segments')
segments = response.json()

# 下载视频
video_url = f'http://device-ip:8082/api/video/{segment_id}/fcamera'
```

## 故障排除

### 常见问题

1. **无法访问界面**
   - 检查服务器是否正常启动
   - 确认端口没有被占用
   - 检查防火墙设置

2. **视频无法播放**
   - 确认浏览器支持HEVC/H.264解码
   - 检查视频文件是否存在
   - 尝试不同的摄像头

3. **移动端显示异常**
   - 使用现代移动浏览器
   - 确保网络连接稳定
   - 清除浏览器缓存

### 日志查看

服务器日志保存在 `/tmp/dashcam_server.log`

```bash
tail -f /tmp/dashcam_server.log
```

### 性能优化

1. **大量视频段**: 使用分页和筛选功能
2. **网络带宽**: 优先使用qcamera进行预览
3. **存储空间**: 定期清理旧视频文件

## 开发和扩展

### 添加新功能

1. 在 `dashcam_server.py` 中添加新的API端点
2. 在 `web/js/dashcam.js` 中添加前端逻辑
3. 更新 `web/css/style.css` 添加样式

### 自定义界面

可以通过修改CSS和JavaScript文件来自定义界面外观和行为。

### 第三方集成

使用提供的API接口可以轻松集成到现有的车队管理系统或监控平台中。

## 许可证

本项目遵循 MIT 许可证，详见项目根目录的 LICENSE 文件。

## 贡献

欢迎提交问题报告和功能请求到项目的 GitHub 仓库。
