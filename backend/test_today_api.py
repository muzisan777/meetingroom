import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# 登录普通用户
print("登录普通用户 user1...")
login_data = {"username": "user1", "password": "user123"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

if response.status_code == 200:
    token = response.json()["access_token"]
    user = response.json()["user"]
    print(f"[OK] 登录成功：{user['username']} (ID: {user['id']})")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试新接口：获取今日所有预约
    print("\n测试新接口：GET /api/bookings/today")
    response = requests.get(f"{BASE_URL}/bookings/today", headers=headers)
    print(f"状态码：{response.status_code}")
    
    if response.status_code == 200:
        bookings = response.json()
        print(f"\n[OK] 返回的预约数量：{len(bookings)}")
        print(f"\n所有预约详情:")
        for i, b in enumerate(bookings, 1):
            status = b.get('status', 'unknown')
            status_mark = "[X]" if status == 'cancelled' else "[OK]"
            print(f"{i}. {status_mark} ID:{b['id']} 会议室:{b['room_id']} 用户 ID:{b['user_id']} 用户名:{b.get('user_name', 'N/A')} 时间:{b['start_time'][:16]} 状态:{status}")
        
        # 统计有效预约
        valid_bookings = [b for b in bookings if b.get('status') != 'cancelled']
        print(f"\n有效预约数量：{len(valid_bookings)}")
        print(f"已取消数量：{len(bookings) - len(valid_bookings)}")
    else:
        print(f"错误：{response.text}")
else:
    print(f"登录失败：{response.text}")
