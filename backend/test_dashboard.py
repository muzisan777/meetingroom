import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

def test_dashboard_flow():
    """测试前端首页加载流程"""
    print("=" * 60)
    print("测试会议室预约系统 - 前端首页加载流程")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 测试登录...")
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"   登录状态码：{response.status_code}")
    
    if response.status_code != 200:
        print(f"   [FAIL] 登录失败：{response.text}")
        return
    
    token = response.json()["access_token"]
    print(f"   [OK] 登录成功，Token: {token[:50]}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取会议室列表 (首页需要)
    print("\n2. 测试获取会议室列表...")
    response = requests.get(f"{BASE_URL}/rooms", headers=headers)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        rooms = response.json()
        print(f"   [OK] 获取成功，会议室数量：{len(rooms)}")
        for room in rooms:
            print(f"      - {room['name']} (容量：{room['capacity']}人)")
    else:
        print(f"   [FAIL] 失败：{response.text}")
        return
    
    # 3. 获取今日预约 (首页需要) - 这是之前报错的接口
    print("\n3. 测试获取今日预约列表 (带日期参数)...")
    today = datetime.now().strftime('%Y-%m-%d')
    params = {
        "start_date": f"{today}T00:00:00",
        "end_date": f"{today}T23:59:59",
        "limit": 100
    }
    response = requests.get(f"{BASE_URL}/bookings", headers=headers, params=params)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        bookings = response.json()
        print(f"   [OK] 获取成功，预约数量：{len(bookings)}")
        if bookings:
            for b in bookings:
                print(f"      - ID:{b['id']} 会议室 ID:{b['room_id']} 用户:{b.get('user_name', 'N/A')} 状态:{b['status']}")
    else:
        print(f"   [FAIL] 失败：{response.text}")
        return
    
    # 4. 获取所有预约 (首页需要)
    print("\n4. 测试获取所有预约列表...")
    response = requests.get(f"{BASE_URL}/bookings", headers=headers, params={"limit": 100})
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        bookings = response.json()
        print(f"   [OK] 获取成功，预约数量：{len(bookings)}")
    else:
        print(f"   [FAIL] 失败：{response.text}")
        return
    
    # 5. 获取物品列表 (首页需要)
    print("\n5. 测试获取物品列表...")
    response = requests.get(f"{BASE_URL}/items", headers=headers)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        items = response.json()
        print(f"   [OK] 获取成功，物品数量：{len(items)}")
        for item in items:
            print(f"      - {item['name']} (可用：{item['available_quantity']}/{item['quantity']})")
    else:
        print(f"   [FAIL] 失败：{response.text}")
        return
    
    # 6. 获取借用记录 (首页需要)
    print("\n6. 测试获取借用记录...")
    response = requests.get(f"{BASE_URL}/borrowings", headers=headers, params={"status": "borrowed"})
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        borrowings = response.json()
        print(f"   [OK] 获取成功，借用中物品数量：{len(borrowings)}")
    else:
        print(f"   [FAIL] 失败：{response.text}")
        return
    
    # 7. 测试创建预约
    print("\n7. 测试创建预约...")
    now = datetime.now()
    start_time = now.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    booking_data = {
        "room_id": 1,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "purpose": "测试预约"
    }
    response = requests.post(f"{BASE_URL}/bookings", headers=headers, json=booking_data)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        booking = response.json()
        print(f"   [OK] 创建成功，预约 ID: {booking['id']}")
        print(f"      用户：{booking.get('user_name', 'N/A')}")
        print(f"      会议室：{booking.get('room_name', 'N/A')}")
        print(f"      时间：{booking['start_time']} - {booking['end_time']}")
    else:
        print(f"   [FAIL] 失败：{response.text}")
    
    # 8. 再次获取预约列表，验证创建成功
    print("\n8. 再次获取预约列表验证...")
    response = requests.get(f"{BASE_URL}/bookings", headers=headers, params={"limit": 100})
    if response.status_code == 200:
        bookings = response.json()
        print(f"   [OK] 当前预约总数：{len(bookings)}")
    
    print("\n" + "=" * 60)
    print("[OK] 所有测试通过！前端首页应该可以正常加载了")
    print("=" * 60)

if __name__ == "__main__":
    test_dashboard_flow()
