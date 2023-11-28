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
        '''
        write a function to get all the channels from the json file
        '''
        with open(os.path.join(self.path, 'channels.json'), 'r') as f:
            channels = json.load(f)

        return channels

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
        for json_file in glob.glob(f"{path_channel}*.json"):
            with open(json_file, 'r', encoding="utf8") as slack_data:
                combined.append(json.load(slack_data))

        dflist = []
        for slack_data in combined:
            msg_type, msg_content, sender_id, time_msg, msg_dist, time_thread_st, reply_users, reply_count, reply_users_count, tm_thread_end = [],[],[],[],[],[],[],[],[],[]

            for row in slack_data:
                print(f"Type of 'row': {type(row)}")
                print(f"Row data: {row}")

                if isinstance(row, dict):
                    if 'bot_id' in row:
                        print(f"Skipped row: {row}")
                        continue

                    msg_type.append(row.get('type', 'Not provided'))
                    msg_content.append(row.get('text', 'Not provided'))

                    if 'user_profile' in row.keys():
                        sender_id.append(row['user_profile']['real_name'])
                    else:
                        sender_id.append('Not provided')
                        time_msg.append(row.get('ts', 'Not provided'))

                    if 'blocks' in row.keys() and row['blocks']:
                        block = row['blocks'][0]
                        if 'elements' in block.keys() and block['elements']:
                            element = block['elements'][0]
                            if 'elements' in element.keys() and element['elements']:
                                msg_dist.append(element['elements'][0]['type'])
                            else:
                                msg_dist.append('unknown')
                        else:
                            msg_dist.append('unknown')
                    else:
                        msg_dist.append('unknown')

                    if 'thread_ts' in row.keys():
                        time_thread_st.append(row['thread_ts'])
                    else:
                        time_thread_st.append(None)

                    if 'reply_users' in row.keys():
                        reply_users.append(",".join(row['reply_users']))
                    else:
                        reply_users.append('Not provided')

                    if 'reply_count' in row.keys():
                        reply_count.append(row['reply_count'])
                        reply_users_count.append(row['reply_users_count'])
                        tm_thread_end.append(row['latest_reply'])
                    else:
                        reply_count.append(0)
                        reply_users_count.append(0)
                        tm_thread_end.append(None)
                else:
                    print(f"Skipping row: {row}")
                    pass

            data = zip(msg_type, msg_content, sender_id, time_msg, msg_dist, time_thread_st,
                        reply_count, reply_users_count, reply_users, tm_thread_end)
            columns = ['msg_type', 'msg_content', 'sender_name', 'msg_sent_time', 'msg_dist_type',
                        'time_thread_start', 'reply_count', 'reply_users_count', 'reply_users', 'tm_thread_end']

            df = pd.DataFrame(data=data, columns=columns)
            df = df[df['sender_name'] != 'Not provided']
            dflist.append(df)

        dfall = pd.concat(dflist, ignore_index=True)
        dfall['channel'] = path_channel.split('/')[-1].split('.')[0]
        dfall = dfall.reset_index(drop=True)
        print("Row data: {}".format(row))
        return dfall
    
    
    def parse_slack_reaction(self, path, channel):
        """get reactions"""
        dfall_reaction = pd.DataFrame()
        combined = []
        for json_file in glob.glob(f"{path}*.json"):
            with open(json_file, 'r') as slack_data:
                combined.append(json.load(slack_data))  # Load the JSON data from each file

        reaction_name, reaction_count, reaction_users, msg, user_id = [], [], [], [], []

        for k in combined:
            for i_count, i in enumerate(k):  # Iterate over the loaded JSON object
                if isinstance(i, dict) and 'reactions' in i.keys():  # Check if i is a dictionary with 'reactions' key
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
