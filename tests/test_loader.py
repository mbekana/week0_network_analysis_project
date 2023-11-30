import unittest
import os
import json
import pandas as pd
from src.loader import SlackDataLoader

class TestSlackDataLoader(unittest.TestCase):

    def setUp(self):
        self.data_path = os.path.abspath('../../week0_network_analysis_project/data/anonymized')
        self.data_loader = SlackDataLoader(self.data_path)

    def test_slack_parser_expected_columns(self):
        test_data = os.path.join(self.data_path, "all-week8/2022-10-10.json")

        temp_json_path = os.path.join(self.data_path, "channels.json")
        with open(temp_json_path, 'w', encoding="utf8") as temp_json_file:
            json.dump(test_data, temp_json_file)

        df = self.data_loader.slack_parser(self.data_path)
        print(df)

        expected_columns = ['msg_type', 'msg_content', 'sender_name', 'msg_sent_time', 'msg_dist_type',
                             'time_thread_start', 'reply_count', 'reply_users_count', 'reply_users', 'tm_thread_end', 'channel']
        self.assertCountEqual(df.columns.tolist(), expected_columns)

        # if os.path.exists(temp_json_path):
        #     os.remove(temp_json_path)

if __name__ == '__main__':
    unittest.main()
