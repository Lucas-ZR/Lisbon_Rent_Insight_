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
                extra VARCHAR[],
                freguesia VARCHAR,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.con.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.database_name}.{self.schema_name}.scrape_jobs (
                parent_url VARCHAR,
                url VARCHAR,
                status VARCHAR,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def write_listings(self, listings):
        self.con.executemany(
            f"""
            INSERT INTO {self.database_name}.{self.schema_name}.raw_listings
                (id, price, title, extra, freguesia)
            VALUES 
                (?,?,?,?,?)
            """,
            [
                [d["id"], d["price"], d["title"], d["extra"], d["freguesia"]]
                for d in listings
            ],
        )

    def write_job_state(self, parent_url, url, status):
        self.con.execute(
            f"""
            INSERT INTO {self.database_name}.{self.schema_name}.scrape_jobs
                (parent_url, url, status)
            VALUES
                (? ,? ,?)
            """,
            [parent_url, url, status],
        )
