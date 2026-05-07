import sqlite3
from datetime import datetime, timedelta
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn = sqlite3.connect('meeting_room.db')
c = conn.cursor()

# 插入组织
c.execute("INSERT INTO organizations (name, description, is_active) VALUES (?, ?, ?)", 
          ("技术部", "技术研发部门", True))
org_id = c.lastrowid

# 插入管理员用户 (密码：admin123)
c.execute("INSERT INTO users (username, email, full_name, hashed_password, org_id, is_admin, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
          ("admin", "admin@example.com", "管理员", hash_password("admin123"), org_id, True, True))

# 插入普通用户 (密码：user123)
c.execute("INSERT INTO users (username, email, full_name, hashed_password, org_id, is_admin, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
          ("user1", "user1@example.com", "张三", hash_password("user123"), org_id, False, True))

# 插入会议室
c.execute("INSERT INTO meeting_rooms (name, capacity, location, facilities, description, is_active) VALUES (?, ?, ?, ?, ?, ?)",
          ("会议室 A", 10, "1 楼 101", "投影仪，白板", "小型会议室", True))
c.execute("INSERT INTO meeting_rooms (name, capacity, location, facilities, description, is_active) VALUES (?, ?, ?, ?, ?, ?)",
          ("会议室 B", 20, "2 楼 201", "投影仪，白板，视频会议", "中型会议室", True))
c.execute("INSERT INTO meeting_rooms (name, capacity, location, facilities, description, is_active) VALUES (?, ?, ?, ?, ?, ?)",
          ("会议室 C", 30, "3 楼 301", "投影仪，白板，视频会议，音响", "大型会议室", True))

# 插入物品
c.execute("INSERT INTO items (name, category, quantity, available_quantity, description, is_active) VALUES (?, ?, ?, ?, ?, ?)",
          ("投影仪", "电子设备", 5, 5, "高清投影仪", True))
c.execute("INSERT INTO items (name, category, quantity, available_quantity, description, is_active) VALUES (?, ?, ?, ?, ?, ?)",
          ("笔记本电脑", "电子设备", 10, 10, "办公笔记本", True))

conn.commit()
conn.close()

print("Test data created successfully!")
print("- Admin user: admin / admin123")
print("- Normal user: user1 / user123")
