import sqlite3

conn = sqlite3.connect('TaskSense/data/tasksense.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

# Check schema
if 'all_time_usage' in tables:
    cursor.execute('PRAGMA table_info(all_time_usage)')
    columns = cursor.fetchall()
    print("\nall_time_usage columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check data
    cursor.execute('SELECT COUNT(*) FROM all_time_usage')
    count = cursor.fetchone()[0]
    print(f"\nRows in all_time_usage: {count}")
    
    if count > 0:
        cursor.execute('SELECT app_name, total_minutes FROM all_time_usage LIMIT 5')
        print("\nSample data:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]:.1f}m")

conn.close()
