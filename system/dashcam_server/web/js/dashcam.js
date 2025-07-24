/**
 * 行车记录仪查看器 JavaScript
 */

class DashcamViewer {
    constructor() {
        this.currentPage = 1;
        this.pageLimit = 20;
        this.currentSegment = null;
        this.currentCamera = 'fcamera';
        this.websocket = null;
        this.segments = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadDashcamInfo();
        this.loadSegments();
    }
    
    setupEventListeners() {
        // 筛选按钮
        document.getElementById('apply-filter').addEventListener('click', () => {
            this.currentPage = 1;
            this.loadSegments();
        });
        
        // 刷新按钮
        document.getElementById('refresh-segments').addEventListener('click', () => {
            this.loadSegments();
        });
        
        // 分页按钮
        document.getElementById('prev-page').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadSegments();
            }
        });
        
        document.getElementById('next-page').addEventListener('click', () => {
            this.currentPage++;
            this.loadSegments();
        });
        
        // 视频播放器控制
        document.getElementById('close-video').addEventListener('click', () => {
            this.closeVideoPlayer();
        });
        
        // 摄像头切换
        document.querySelectorAll('.camera-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const camera = e.target.closest('.camera-tab').dataset.camera;
                this.switchCamera(camera);
            });
        });
        
        // 模态框关闭
        document.getElementById('close-error').addEventListener('click', () => {
            this.hideModal('error-modal');
        });
        
        document.getElementById('error-ok').addEventListener('click', () => {
            this.hideModal('error-modal');
        });
        
        document.getElementById('close-detail').addEventListener('click', () => {
            this.hideModal('segment-detail-modal');
        });
        
        document.getElementById('detail-ok').addEventListener('click', () => {
            this.hideModal('segment-detail-modal');
        });
        
        // 点击模态框背景关闭
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket连接已建立');
                this.updateConnectionStatus(true);
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket连接已关闭');
                this.updateConnectionStatus(false);
                // 5秒后重连
                setTimeout(() => this.connectWebSocket(), 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket错误:', error);
                this.updateConnectionStatus(false);
            };
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'pong':
                // 心跳响应
                break;
            case 'segments_updated':
                // 视频段更新
                this.loadSegments();
                break;
            default:
                console.log('未知WebSocket消息:', data);
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (connected) {
            statusElement.innerHTML = '<i class="fas fa-circle"></i> 已连接';
            statusElement.className = 'status-indicator connected';
        } else {
            statusElement.innerHTML = '<i class="fas fa-circle"></i> 连接断开';
            statusElement.className = 'status-indicator disconnected';
        }
    }
    
    async loadDashcamInfo() {
        try {
            const response = await fetch('/api/info');
            if (!response.ok) throw new Error('获取系统信息失败');
            
            const info = await response.json();
            this.updateDashcamInfo(info);
        } catch (error) {
            console.error('加载系统信息失败:', error);
            this.showError('加载系统信息失败: ' + error.message);
        }
    }
    
    updateDashcamInfo(info) {
        document.getElementById('total-segments').textContent = info.total_segments;
        document.getElementById('total-size').textContent = this.formatFileSize(info.total_size);
        document.getElementById('available-cameras').textContent = info.available_cameras.join(', ');
    }
    
    async loadSegments() {
        this.showLoading(true);
        
        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                limit: this.pageLimit
            });
            
            // 添加筛选参数
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;
            const cameraFilter = document.getElementById('camera-filter').value;
            
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            if (cameraFilter) params.append('camera', cameraFilter);
            
            const response = await fetch(`/api/segments?${params}`);
            if (!response.ok) throw new Error('获取视频段列表失败');
            
            const data = await response.json();
            this.segments = data.segments;
            this.renderSegments(data.segments);
            this.updatePagination(data);
            
        } catch (error) {
            console.error('加载视频段失败:', error);
            this.showError('加载视频段失败: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    renderSegments(segments) {
        const grid = document.getElementById('segments-grid');
        const template = document.getElementById('segment-card-template');
        
        grid.innerHTML = '';
        
        segments.forEach(segment => {
            const card = template.content.cloneNode(true);
            const cardElement = card.querySelector('.segment-card');
            
            cardElement.dataset.segmentId = segment.segment_id;
            
            // 填充数据
            card.querySelector('.segment-time').textContent = 
                new Date(segment.timestamp).toLocaleString('zh-CN');
            card.querySelector('.segment-duration').textContent = 
                this.formatDuration(segment.duration);
            card.querySelector('.segment-cameras').textContent = 
                `摄像头: ${Object.keys(segment.cameras).join(', ')}`;
            card.querySelector('.segment-size').textContent = 
                `大小: ${this.formatFileSize(segment.size)}`;
            
            // 添加事件监听器
            card.querySelector('.play-segment').addEventListener('click', () => {
                this.playSegment(segment);
            });
            
            card.querySelector('.segment-detail').addEventListener('click', () => {
                this.showSegmentDetail(segment);
            });
            
            grid.appendChild(card);
        });
    }
    
    updatePagination(data) {
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        const pageInfo = document.getElementById('page-info');
        
        prevBtn.disabled = data.page <= 1;
        nextBtn.disabled = !data.has_next;
        pageInfo.textContent = `第 ${data.page} 页 (共 ${data.total} 条)`;
    }
    
    async playSegment(segment) {
        this.currentSegment = segment;
        
        // 显示视频播放器
        document.getElementById('video-player-container').style.display = 'block';
        document.getElementById('segments-container').style.display = 'none';
        
        // 更新标题
        document.getElementById('video-title').textContent = 
            `视频播放 - ${new Date(segment.timestamp).toLocaleString('zh-CN')}`;
        
        // 更新摄像头选项卡
        this.updateCameraTabs(segment.cameras);
        
        // 播放默认摄像头
        const availableCameras = Object.keys(segment.cameras);
        const defaultCamera = availableCameras.includes(this.currentCamera) 
            ? this.currentCamera 
            : availableCameras[0];
        
        this.switchCamera(defaultCamera);
    }
    
    updateCameraTabs(availableCameras) {
        document.querySelectorAll('.camera-tab').forEach(tab => {
            const camera = tab.dataset.camera;
            tab.disabled = !availableCameras.hasOwnProperty(camera);
            tab.classList.remove('active');
        });
    }
    
    async switchCamera(camera) {
        if (!this.currentSegment || !this.currentSegment.cameras[camera]) {
            return;
        }
        
        this.currentCamera = camera;
        
        // 更新选项卡状态
        document.querySelectorAll('.camera-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.camera === camera);
        });
        
        // 加载视频
        const video = document.getElementById('main-video');
        const videoUrl = `/api/video/${this.currentSegment.segment_id}/${camera}`;
        
        video.src = videoUrl;
        video.load();
    }
    
    closeVideoPlayer() {
        document.getElementById('video-player-container').style.display = 'none';
        document.getElementById('segments-container').style.display = 'block';
        
        // 停止视频播放
        const video = document.getElementById('main-video');
        video.pause();
        video.src = '';
        
        this.currentSegment = null;
    }
    
    async showSegmentDetail(segment) {
        try {
            const response = await fetch(`/api/segments/${segment.segment_id}`);
            if (!response.ok) throw new Error('获取视频段详情失败');
            
            const detail = await response.json();
            this.renderSegmentDetail(detail);
            this.showModal('segment-detail-modal');
            
        } catch (error) {
            console.error('获取视频段详情失败:', error);
            this.showError('获取视频段详情失败: ' + error.message);
        }
    }
    
    renderSegmentDetail(segment) {
        const content = document.getElementById('segment-detail-content');
        
        content.innerHTML = `
            <div class="detail-grid">
                <div class="detail-item">
                    <strong>段ID:</strong> ${segment.segment_id}
                </div>
                <div class="detail-item">
                    <strong>时间:</strong> ${new Date(segment.timestamp).toLocaleString('zh-CN')}
                </div>
                <div class="detail-item">
                    <strong>时长:</strong> ${this.formatDuration(segment.duration)}
                </div>
                <div class="detail-item">
                    <strong>总大小:</strong> ${this.formatFileSize(segment.size)}
                </div>
                <div class="detail-item">
                    <strong>包含音频:</strong> ${segment.has_audio ? '是' : '否'}
                </div>
                <div class="detail-item">
                    <strong>可用摄像头:</strong>
                    <ul>
                        ${Object.entries(segment.cameras).map(([camera, path]) => 
                            `<li>${camera}: ${path.split('/').pop()}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    showLoading(show) {
        document.getElementById('loading-indicator').style.display = show ? 'block' : 'none';
        document.getElementById('segments-grid').style.display = show ? 'none' : 'grid';
    }
    
    showModal(modalId) {
        document.getElementById(modalId).style.display = 'flex';
    }
    
    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }
    
    showError(message) {
        document.getElementById('error-message').textContent = message;
        this.showModal('error-modal');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new DashcamViewer();
});
