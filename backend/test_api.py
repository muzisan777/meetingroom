import requests
import json

# 测试登录
login_data = {
    "username": "admin",
    "password": "admin123"
}
response = requests.post("http://localhost:8000/api/auth/login", data=login_data)
print("Login response:", response.status_code)
if response.status_code == 200:
    token = response.json()["access_token"]
    print("Token:", token[:50] + "...")
    
    # 测试获取预约列表
    headers = {"Authorization": f"Bearer {token}"}
    bookings_response = requests.get("http://localhost:8000/api/bookings", headers=headers)
    print("\nBookings response:", bookings_response.status_code)
    if bookings_response.status_code == 200:
        print("Bookings:", json.dumps(bookings_response.json(), indent=2, default=str))
    else:
        print("Error:", bookings_response.text)
    
    # 测试获取会议室列表
    rooms_response = requests.get("http://localhost:8000/api/rooms", headers=headers)
    print("\nRooms response:", rooms_response.status_code)
    if rooms_response.status_code == 200:
        print("Rooms:", json.dumps(rooms_response.json(), indent=2, default=str))
    else:
        print("Error:", rooms_response.text)
else:
    print("Login failed:", response.text)
