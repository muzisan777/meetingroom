"""重置数据库脚本"""
import sqlite3
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn = sqlite3.connect('meeting_room.db')
c = conn.cursor()

# 清空所有表数据
tables = ['borrowings', 'bookings', 'items', 'meeting_rooms', 'users', 'organizations']
for table in tables:
    c.execute(f'DELETE FROM {table}')
print('✅ 已清空所有数据表')

# 重置自增ID (如果表存在)
try:
    c.execute("DELETE FROM sqlite_sequence WHERE name IN ('borrowings', 'bookings', 'items', 'meeting_rooms', 'users', 'organizations')")
    print('✅ 已重置自增ID')
except sqlite3.OperationalError:
    print('⚠️ sqlite_sequence 表不存在，跳过')

# 创建默认组织
c.execute("INSERT INTO organizations (name, description, is_active) VALUES (?, ?, ?)", 
          ('默认部门', '默认组织', True))
org_id = c.lastrowid
print(f'✅ 创建默认组织: org_id={org_id}')

# 创建管理员账号 admin / admin123
c.execute("INSERT INTO users (username, email, full_name, hashed_password, org_id, is_admin, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
          ('admin', 'admin@example.com', '管理员', hash_password('admin123'), org_id, True, True))
print('✅ 创建管理员账号: admin / admin123')

# 创建默认会议室
rooms = [
    ('会议室 A', 10, '1 楼 101', '投影仪，白板', '小型会议室'),
    ('会议室 B', 20, '2 楼 201', '投影仪，白板，视频会议', '中型会议室'),
    ('会议室 C', 30, '3 楼 301', '投影仪，白板，视频会议，音响', '大型会议室'),
]
for room in rooms:
    c.execute("INSERT INTO meeting_rooms (name, capacity, location, facilities, description, is_active) VALUES (?, ?, ?, ?, ?, ?)",
              (*room, True))
print('✅ 创建 3 个默认会议室')

# 创建默认物品
items = [
    ('投影仪', '电子设备', 5, 5, '高清投影仪'),
    ('笔记本电脑', '电子设备', 10, 10, '办公笔记本'),
]
for item in items:
    c.execute("INSERT INTO items (name, category, quantity, available_quantity, description, is_active) VALUES (?, ?, ?, ?, ?, ?)",
              (*item, True))
print('✅ 创建 2 个默认物品')

conn.commit()
conn.close()
print('')
print('🎉 数据库重置完成！')