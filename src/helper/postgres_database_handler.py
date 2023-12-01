import psycopg2
from psycopg2 import sql

import psycopg2

class PostgreSQLHandler:
    def __init__(self, dbname, user, password, host="127.0.0.1", port=5432):
        self.conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port
        )
        self.cur = self.conn.cursor()

    def create_users_table(self):
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
                team_id VARCHAR(255),
                name VARCHAR(255),
                deleted BOOLEAN,
                color VARCHAR(10),
                real_name VARCHAR(255),
                tz VARCHAR(255),
                tz_label VARCHAR(255),
                tz_offset INT,
                profile JSONB,
                is_admin BOOLEAN,
                is_owner BOOLEAN,
                is_primary_owner BOOLEAN,
                is_restricted BOOLEAN,
                is_ultra_restricted BOOLEAN,
                is_bot BOOLEAN,
                is_app_user BOOLEAN,
                updated BIGINT,
                is_email_confirmed BOOLEAN,
                who_can_share_contact_card VARCHAR(50)
            );
        '''
        self.cur.execute(create_table_query)
        self.conn.commit()

    def create_feature_store_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS feature_store (
            feature_id SERIAL PRIMARY KEY,
            feature_name VARCHAR(255)
        );
        """
        self.cur.execute(query)
        self.conn.commit()

    def create_model_versioning_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS model_versioning (
            version_id SERIAL PRIMARY KEY,
            model_name VARCHAR(255)
        );
        """
        self.cur.execute(query)
        self.conn.commit()

    def create_slack_messages_table(self):
        # Create users table first
        self.create_users_table()

        query = """
        CREATE TABLE IF NOT EXISTS slack_messages (
            message_id SERIAL PRIMARY KEY,
            
            message_text TEXT
        );
        """
        self.cur.execute(query)
        self.conn.commit()
# user_id SERIAL REFERENCES users(id),
    def create_message_tags_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS message_tags (
            tag_id SERIAL PRIMARY KEY,
            message_id INT REFERENCES slack_messages(message_id),
            tag_name VARCHAR(50)
        );
        """
        self.cur.execute(query)
        self.conn.commit()

    def close_connection(self):
        self.cur.close()
        self.conn.close()
