import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# 登录管理员
print("登录管理员...")
login_data = {"username": "admin", "password": "admin123"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取今日预约
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n获取今日预约 ({today})...")
    params = {
        "start_date": f"{today}T00:00:00",
        "end_date": f"{today}T23:59:59",
        "limit": 100
    }
    response = requests.get(f"{BASE_URL}/bookings", headers=headers, params=params)
    
    if response.status_code == 200:
        bookings = response.json()
        print(f"\n今日预约总数：{len(bookings)}")
        print(f"\n所有预约详情:")
        for i, b in enumerate(bookings, 1):
            status = b.get('status', 'unknown')
            status_mark = "[X]" if status == 'cancelled' else "[OK]"
            print(f"{i}. {status_mark} ID:{b['id']} 会议室:{b['room_id']} 用户:{b.get('user_name', b['user_id'])} 时间:{b['start_time'][:16]} 状态:{status}")
        
        # 统计有效预约
        valid_bookings = [b for b in bookings if b.get('status') != 'cancelled']
        print(f"\n有效预约数量：{len(valid_bookings)}")
        print(f"已取消数量：{len(bookings) - len(valid_bookings)}")
    else:
        print(f"错误：{response.text}")
else:
    print(f"登录失败：{response.text}")
