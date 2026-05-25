import duckdb


class DatabaseManager:
    def __init__(self, database_name, schema_name):
        self.con = duckdb.connect(
            "md:"
        )  # picks motherduck_token from env automatically
        self.database_name = database_name
        self.schema_name = schema_name

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.con.close()

    def init_schema(self):
        self.con.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.database_name}.{self.schema_name}.raw_listings (
                id VARCHAR,
                price VARCHAR,
                title VARCHAR,
                detail VARCHAR[],
                tags VARCHAR,
                freguesia VARCHAR,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.con.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.database_name}.{self.schema_name}.scrape_jobs (
                parent_url VARCHAR,
                url VARCHAR,
                status VARCHAR,
                page_count INTEGER,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def write_listings(self, listings):
        self.con.executemany(
            f"""
            INSERT INTO {self.database_name}.{self.schema_name}.raw_listings
                (id, price, title, detail, tags, freguesia)
            VALUES 
                (?,?,?,?,?,?)
            """,
            [
                [
                    d["id"],
                    d["price"],
                    d["title"],
                    d["detail"],
                    d["tags"],
                    d["freguesia"],
                ]
                for d in listings
            ],
        )

    def write_job_state(self, parent_url, url, status, page_count=None):
        self.con.execute(
            f"""
            INSERT INTO {self.database_name}.{self.schema_name}.scrape_jobs
                (parent_url, url, status, page_count)
            VALUES
                (? ,? ,?, ?)
            """,
            [parent_url, url, status, page_count],
        )

    def already_loaded_urls(self):
        self.con.execute(
            f"""
            WITH success_this_month AS (
            SELECT
                *
            FROM "lisbon_rental"."test"."scrape_jobs"
            WHERE 
                status = 'success'
            AND
                DATE_TRUNC('month', scraped_at) = DATE_TRUNC('month', CURRENT_DATE)
            ),

            done_child_urls AS (
            SELECT
                url
            FROM success_this_month
            WHERE 
                page_count IS NULL
            ),

            parent_url_count AS (
            SELECT
                parent_url,
                COUNT(url) AS parent_count
            FROM success_this_month
            GROUP BY parent_url
            ),

            done_parent_urls AS (
            SELECT 
            parent_url_count.parent_url
            FROM parent_url_count
            JOIN success_this_month 
            ON 
                parent_url_count.parent_url=success_this_month.parent_url 
            AND 
                success_this_month.page_count IS NOT NULL
            WHERE parent_count = page_count
            )

            SELECT * FROM done_child_urls UNION ALL SELECT * FROM done_parent_urls
            """
        )
