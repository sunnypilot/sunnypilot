
import time
import cereal.messaging as messaging

def main():
    # 1. 创建一个 SubMaster (监听器)
    # 括号里是你想要监听的频道（Socket），比如 'carState' (车辆状态) 和 'modelV2' (视觉模型输出)
    sm = messaging.SubMaster(['carState', 'modelV2'])

    print("🚀 开始监听系统消息... (请确保后台正在运行 replay)")

    while True:
        # 2. 阻塞并等待接收最新消息，超时时间设为 1000ms
        sm.update(1000)

        # 3. 检查 'carState' 频道有没有新数据进来
        if sm.updated['carState']:
            # 提取车速 (vEgo，单位是 m/s) 和 方向盘转角
            v_ego = sm['carState'].vEgo
            steering_angle = sm['carState'].steeringAngleDeg
            print(f"[车辆状态] 车速: {v_ego:.2f} m/s | 方向盘角度: {steering_angle:.2f}°")

        # 4. 检查 'modelV2' (视觉神经网络的预测结果) 有没有新数据
        if sm.updated['modelV2']:
            # 第一步：强制转换为 Python 标准列表
            probs = list(sm['modelV2'].laneLineProbs)
            # 第二步：加上长度保护，防止某些帧模型没输出完整数据
            if len(probs) >= 2:
                # 第三步：确保强转为原生 float 再进行数学计算
                left_lane_prob = float(probs[1])
                print(f"[视觉模型] 左侧车道线存在概率: {left_lane_prob * 100:.1f}%")
            else:
                print("[视觉模型] 当前帧模型暂未输出完整概率数据")

        # 防止循环过快占用 CPU
        time.sleep(0.01)

if __name__ == "__main__":
    main()