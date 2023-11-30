import json
import argparse
import os
import io
import shutil
import copy
import glob 
from datetime import datetime
from pick import pick
from time import sleep
import pandas as pd
from collections import Counter

# Create wrapper classes for using slack_sdk in place of slacker
class SlackDataLoader:
    '''
    Slack exported data IO class.

    When you open slack exported ZIP file, each channel or direct message 
    will have its own folder. Each folder will contain messages from the 
    conversation, organised by date in separate JSON files.

    You'll see reference files for different kinds of conversations: 
    users.json files for all types of users that exist in the slack workspace
    channels.json files for public channels, 
    
    These files contain metadata about the conversations, including their names and IDs.

    For security reasons, we have anonymized names - the names you will see are generated using the faker library.
    
    '''
    def __init__(self, path):
        '''
        path: path to the slack exported data folder
        '''
        self.path = path
        self.channels = self.get_channels()
        self.users = self.get_users()

    def get_users(self):
        '''
        write a function to get all the users from the json file
        '''
        with open(os.path.join(self.path, 'users.json'), 'r') as f:
            users = json.load(f)

        return users
    
    def get_channels(self):
        try:
            with open(os.path.join(self.path, 'channels.json'), 'r') as f:
                channels = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading channels: {e}")
            channels = []
        return channels

    def get_users(self):
        try:
            with open(os.path.join(self.path, 'users.json'), 'r') as f:
                users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading users: {e}")
            users = []
        return users


    def get_channel_messages(self, channel_name):
        '''
        write a function to get all the messages from a channel
        '''

    def get_user_map(self):
        '''
        write a function to get a map between user id and user name
        '''
        userNamesById = {}
        userIdsByName = {}
        for user in self.users:
            userNamesById[user['id']] = user['name']
            userIdsByName[user['name']] = user['id']
        return userNamesById, userIdsByName        


    def slack_parser(self, path_channel):
        combined = []
        for json_file in glob.glob(f"{path_channel}/*.json"):
            with open(json_file, 'r', encoding="utf8") as slack_data:
                data = json.load(slack_data)
                if isinstance(data, list):
                    combined.extend(data)

        if not combined:
            print(f"No valid data found in {path_channel}")
            return pd.DataFrame()

        msg_type_list, msg_content_list, sender_name_list, time_msg_list, msg_dist_list, time_thread_start_list, reply_count_list, reply_users_count_list, reply_users_list, tm_thread_end_list = [], [], [], [], [], [], [], [], [], []

        for row in combined:
            if 'bot_id' not in row.keys():
                msg_type_list.append(row.get('type', ''))
                msg_content_list.append(row.get('text', ''))
                sender_name_list.append(row['user_profile']['real_name'] if 'user_profile' in row else 'Not provided')
                time_msg_list.append(row.get('ts', ''))

                # Check for the existence of 'blocks' and nested elements
                if 'blocks' in row and row['blocks'] and 'elements' in row['blocks'][0] and row['blocks'][0]['elements']:
                    # Check if there are elements in the 'elements' list
                    if 'elements' in row['blocks'][0]['elements'][0] and row['blocks'][0]['elements'][0]['elements']:
                        msg_dist_list.append(row['blocks'][0]['elements'][0]['elements'][0]['type'])
                    else:
                        msg_dist_list.append('reshared')
                else:
                    msg_dist_list.append('reshared')

                time_thread_start_list.append(row.get('thread_ts', 0))
                reply_users_list.append(",".join(row.get('reply_users', [])))
                reply_count_list.append(row.get('reply_count', 0))
                reply_users_count_list.append(row.get('reply_users_count', 0))
                tm_thread_end_list.append(row.get('latest_reply', 0))


        data = zip(msg_type_list, msg_content_list, sender_name_list, time_msg_list, msg_dist_list, time_thread_start_list,
                   reply_count_list, reply_users_count_list, reply_users_list, tm_thread_end_list)
        columns = ['msg_type', 'msg_content', 'sender_name', 'msg_sent_time', 'msg_dist_type',
                   'time_thread_start', 'reply_count', 'reply_users_count', 'reply_users', 'tm_thread_end']

        df = pd.DataFrame(data=data, columns=columns)
        df = df[df['sender_name'] != 'Not provided']
        df['channel'] = path_channel.split('/')[-1].split('.')[0]
        df = df.reset_index(drop=True)

        return df
    
    
    def parse_slack_reaction(self, path, channel):
        """get reactions"""
        dfall_reaction = pd.DataFrame()
        combined = []
        for json_file in glob.glob(f"{path}*.json"):
            with open(json_file, 'r') as slack_data:
                combined.append(slack_data)

        reaction_name, reaction_count, reaction_users, msg, user_id = [], [], [], [], []

        for k in combined:
            slack_data = json.load(open(k.name, 'r', encoding="utf-8"))
            
            for i_count, i in enumerate(slack_data):
                if 'reactions' in i.keys():
                    for j in range(len(i['reactions'])):
                        msg.append(i['text'])
                        user_id.append(i['user'])
                        reaction_name.append(i['reactions'][j]['name'])
                        reaction_count.append(i['reactions'][j]['count'])
                        reaction_users.append(",".join(i['reactions'][j]['users']))
                    
        data_reaction = zip(reaction_name, reaction_count, reaction_users, msg, user_id)
        columns_reaction = ['reaction_name', 'reaction_count', 'reaction_users_count', 'message', 'user_id']
        df_reaction = pd.DataFrame(data=data_reaction, columns=columns_reaction)
        df_reaction['channel'] = channel
        return df_reaction
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export Slack history')

    parser.add_argument('--zip', help="Name of a zip file to import")
    args = parser.parse_args()

