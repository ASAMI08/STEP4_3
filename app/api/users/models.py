from app.core.database import get_db_connection
from app.api.users.schemas import UserInDB, UserCreate
from datetime import datetime

class UserModel:
    """ユーザーモデル - データベースとのやり取りを担当"""
    
    @staticmethod
    def get_by_username(username: str):
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE name = %s"
                cursor.execute(sql, (username,))
                user_data = cursor.fetchone()
                
            connection.close()
            
            if user_data:
                return UserInDB(**user_data)
            return None
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    @staticmethod
    def get_by_id(user_id: int):
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                user_data = cursor.fetchone()
                
            connection.close()
            
            if user_data:
                return UserInDB(**user_data)
            return None
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    @staticmethod
    def create(user: UserCreate, password: str):
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO users (name, password, category_id, last_login_at) 
                VALUES (%s, %s, %s, NOW())
                """
                cursor.execute(sql, (user.name, password, user.category_id if hasattr(user, 'category_id') else None))
                user_id = cursor.lastrowid
            connection.close()
            
            return user_id
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    @staticmethod
    def create_with_categories(name: str, password: str, categories: str = None):
        """カテゴリー付きでユーザーを作成"""
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                # ユーザーテーブルにcategoriesカラムがない場合は追加する必要があります
                # ALTER TABLE users ADD COLUMN categories VARCHAR(255);
                
                sql = """
                INSERT INTO users (name, password, categories, last_login_at) 
                VALUES (%s, %s, %s, NOW())
                """
                cursor.execute(sql, (name, password, categories))
                user_id = cursor.lastrowid
            connection.close()
            
            return user_id
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    @staticmethod
    def update_last_login(user_id: int):
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "UPDATE users SET last_login_at = NOW() WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
            connection.close()
            return True
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False
    
    @staticmethod
    def update_points(user_id: int, points: int):
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "UPDATE users SET point_total = point_total + %s WHERE user_id = %s"
                cursor.execute(sql, (points, user_id))
            connection.close()
            return True
        except Exception as e:
            print(f"Error updating points: {e}")
            return False
    
    @staticmethod
    def increment_answers(user_id: int):
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "UPDATE users SET num_answer = num_answer + 1 WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
            connection.close()
            return True
        except Exception as e:
            print(f"Error updating answer count: {e}")
            return False