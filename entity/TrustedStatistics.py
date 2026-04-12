from entity.db_connection import get_db_connection  


class TrustedStatistic:

    def get_stat_by_metric(self, metric_key, country=None, year=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT * FROM Trusted_Statistics
            WHERE metric_key = %s
        """
        params = [metric_key]

        if country:
            sql += " AND country = %s"
            params.append(country)

        if year:
            sql += " AND year = %s"
            params.append(year)

        sql += " ORDER BY year DESC LIMIT 1"

        cursor.execute(sql, params)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result
    
    def upsert_stat(self, metric_key, country, year, value, unit, source_name, source_url):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        INSERT INTO Trusted_Statistics
            (metric_key, country, year, value, unit, source_name, source_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            value        = VALUES(value),
            unit         = VALUES(unit),
            source_name  = VALUES(source_name),
            source_url   = VALUES(source_url),
            last_updated = CURRENT_TIMESTAMP
        """
        cursor.execute(sql, (metric_key, country, year, value, unit, source_name, source_url))
        conn.commit()
        print(f"  OK  {metric_key} ({country}, {year}) = {value} {unit}")
        cursor.close()
        conn.close()
