import requests

# 测试登录
print("测试登录 API...")
login_data = {"username": "admin", "password": "admin123"}
response = requests.post("http://localhost:8000/api/auth/login", data=login_data)

print(f"状态码：{response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"[OK] 登录成功！")
    print(f"Token: {data['access_token'][:50]}...")
    print(f"用户：{data.get('username', 'N/A')}")
else:
    print(f"[FAIL] 登录失败：{response.text}")
