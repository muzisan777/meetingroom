import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

print("=" * 60)
print("会议室预约系统 - 前后端 API 验证")
print("=" * 60)

# 1. 测试登录
print("\n1. 测试登录接口")
login_data = {"username": "admin", "password": "admin123"}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
print(f"   状态码：{response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   [OK] 登录成功")
    print(f"   Token: {data['access_token'][:50]}...")
    print(f"   用户信息:")
    user = data.get('user', {})
    print(f"     - ID: {user.get('id')}")
    print(f"     - 用户名：{user.get('username')}")
    print(f"     - 姓名：{user.get('full_name')}")
    print(f"     - 是否管理员：{user.get('is_admin')}")
    
    token = data['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 测试获取今日预约
    print("\n2. 测试获取今日预约")
    response = requests.get(f"{BASE_URL}/bookings/today", headers=headers)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        bookings = response.json()
        print(f"   [OK] 获取成功，共 {len(bookings)} 条")
        if bookings:
            b = bookings[0]
            print(f"   第一条预约:")
            print(f"     - ID: {b.get('id')}")
            print(f"     - 用户 ID: {b.get('user_id')}")
            print(f"     - 用户名：{b.get('user_name')}")
            print(f"     - 部门：{b.get('user_org_name')}")
            print(f"     - 会议室 ID: {b.get('room_id')}")
            print(f"     - 会议室名：{b.get('room_name')}")
            print(f"     - 状态：{b.get('status')}")
    else:
        print(f"   [FAIL] {response.text}")
    
    # 3. 测试获取所有预约
    print("\n3. 测试获取所有预约")
    response = requests.get(f"{BASE_URL}/bookings", headers=headers, params={"limit": 100})
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        bookings = response.json()
        print(f"   [OK] 获取成功，共 {len(bookings)} 条")
    else:
        print(f"   [FAIL] {response.text}")
    
    # 4. 测试获取会议室列表
    print("\n4. 测试获取会议室列表")
    response = requests.get(f"{BASE_URL}/rooms", headers=headers)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        rooms = response.json()
        print(f"   [OK] 获取成功，共 {len(rooms)} 个")
    else:
        print(f"   [FAIL] {response.text}")
    
    # 5. 测试获取物品列表
    print("\n5. 测试获取物品列表")
    response = requests.get(f"{BASE_URL}/items", headers=headers)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        items = response.json()
        print(f"   [OK] 获取成功，共 {len(items)} 个")
    else:
        print(f"   [FAIL] {response.text}")
    
    print("\n" + "=" * 60)
    print("[OK] 所有 API 测试通过！")
    print("=" * 60)
else:
    print(f"   [FAIL] {response.text}")
    print("\n[ERROR] 登录失败，无法继续测试")
