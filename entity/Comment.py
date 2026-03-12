from entity.db_connection import get_db_connection

class CommentEntity:

    def add_comment(self,articleID,userID,text):

        conn = get_db_connection()
        cursor = conn.cursor()

        sql="""
        INSERT INTO Comment(articleID,userID,commentText,created_at)
        VALUES(%s,%s,%s,NOW())
        """

        cursor.execute(sql,(articleID,userID,text))
        conn.commit()
        conn.close()
