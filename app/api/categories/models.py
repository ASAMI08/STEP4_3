from app.core.database import get_db_connection

class CategoryModel:
    """カテゴリーモデル - カテゴリー情報の管理"""
    
    @staticmethod
    def get_all_categories():
        """全カテゴリー取得"""
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categories ORDER BY name"
                cursor.execute(sql)
                categories = cursor.fetchall()
            connection.close()
            return categories
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    @staticmethod
    def get_category_by_name(name: str):
        """名前でカテゴリー取得"""
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categories WHERE name = %s"
                cursor.execute(sql, (name,))
                category = cursor.fetchone()
            connection.close()
            return category
        except Exception as e:
            print(f"Error getting category: {e}")
            return None
    
    @staticmethod
    def get_default_categories():
        """デフォルトカテゴリー一覧"""
        return [
            "システム部",
            "経理部",
            "事業企画部",
            "デザイン部",
            "営業部",
            "アート",
            "音楽",
            "法務部",
            "知財部",
            "情セキ部"
        ]
    
    @staticmethod
    def ensure_categories_exist():
        """デフォルトカテゴリーをデータベースに登録"""
        default_categories = CategoryModel.get_default_categories()
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                # カテゴリーテーブルが存在するか確認
                try:
                    cursor.execute("SELECT 1 FROM categories LIMIT 1")
                except:
                    # テーブルが存在しない場合は作成
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(50) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """)
                
                # デフォルトカテゴリーを登録
                for category in default_categories:
                    cursor.execute(
                        "INSERT IGNORE INTO categories (name) VALUES (%s)",
                        (category,)
                    )
            
            connection.close()
            return True
        except Exception as e:
            print(f"Error ensuring categories: {e}")
            return False