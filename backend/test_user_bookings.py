import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

# 登录普通用户
print("登录普通用户 user1...")
login_data = {"username": "user1", "password": "user123"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
print(f"登录状态码：{response.status_code}")

if response.status_code == 200:
    token = response.json()["access_token"]
    user = response.json()["user"]
    print(f"[OK] 登录成功：{user['username']}")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取普通用户的预约列表
    print("\n获取 user1 的预约列表...")
    response = requests.get(f"{BASE_URL}/bookings", headers=headers)
    print(f"状态码：{response.status_code}")
    if response.status_code == 200:
        bookings = response.json()
        print(f"[OK] 获取成功，预约数量：{len(bookings)}")
        if bookings:
            for b in bookings:
                print(f"  - ID:{b['id']} 会议室:{b['room_id']} 时间:{b['start_time']} 状态:{b['status']}")
        else:
            print("[INFO] 暂无预约记录")
    else:
        print(f"[FAIL] {response.text}")
else:
    print(f"[FAIL] {response.text}")
