import time
import os
import MySQLdb

def wait_for_database():
    print("Waiting for database...")
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            db_conn = MySQLdb.connect(
                host=os.environ.get('DB_HOST', 'db'),
                user=os.environ.get('DB_USER', 'book-user'),
                passwd=os.environ.get('DB_PASSWORD', 'book-password'),
                db=os.environ.get('DB_NAME', 'book-store'),
                port=3306
            )
            print("Database is available!")
            db_conn.close()
            return True
        except MySQLdb.OperationalError as e:
            print(f'Database unavailable, waiting 1 second... (retry {retry_count + 1}/{max_retries})')
            retry_count += 1
            time.sleep(1)
    
    print("Could not connect to database after multiple retries")
    return False

if __name__ == "__main__":
    if wait_for_database():
        exit(0)
    else:
        exit(1)