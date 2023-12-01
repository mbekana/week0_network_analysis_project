from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from src.helper.mongodb_database_handler import SlackMessageWithSchema
from textblob import TextBlob

slack_db = SlackMessageWithSchema(database_name="week0_network_analysis")
app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

@app.route('/api/sentiment_analysis', methods=['GET'])
def sentiment_analysis_api():
    sentiment_data = {}
    messages = slack_db.find_all('slack_messages')

    for message in messages:
        timestamp = float(message['msg_sent_time'])
        msg_sent_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
        month_key = msg_sent_time[:7]  # Extract the month part

        if month_key not in sentiment_data:
            sentiment_data[month_key] = {'positive_scores': [], 'negative_scores': []}

        blob = TextBlob(message['msg_content'])
        sentiment_score = blob.sentiment.polarity

        if sentiment_score > 0:
            sentiment_data[month_key]['positive_scores'].append(sentiment_score)
        elif sentiment_score < 0:
            sentiment_data[month_key]['negative_scores'].append(sentiment_score)

    # Calculate average sentiment score for each month
    result = [{'month': month_key,
               'average_positive_sentiment': sum(data['positive_scores']) / len(data['positive_scores']) if data['positive_scores'] else 0,
               'average_negative_sentiment': sum(data['negative_scores']) / len(data['negative_scores']) if data['negative_scores'] else 0}
              for month_key, data in sentiment_data.items()]

    return jsonify(result)

# Top Messages API Endpoint

# Top Messages API Endpoint
@app.route('/api/user_stats', methods=['GET'])
def top_messages():
    # Query MongoDB for users with the most messages, replies, and reactions
    most_messages_user = slack_db.db.slack_messages.aggregate([
        {"$group": {"_id": "$sender_name", "message_count": {"$sum": 1}}},
        {"$sort": {"message_count": -1}},
        {"$limit": 1},
        {"$project": {"user": "$_id", "message_count": 1, "_id": 0}}
    ])

    most_replies_user = slack_db.db.replies.aggregate([
        {"$group": {"_id": "$sender_name", "reply_count": {"$sum": "$Reply count"}}},
        {"$sort": {"reply_count": -1}},
        {"$limit": 1},
        {"$project": {"user": "$_id", "reply_count": 1, "_id": 0}}
    ])

    most_reactions_user = slack_db.db.reactions.aggregate([
        {"$group": {"_id": "$user_id", "reaction_count": {"$sum": 1}}},
        {"$sort": {"reaction_count": -1}},
        {"$limit": 1},
        {"$project": {"user": "$_id", "reaction_count": 1, "_id": 0}}
    ])

    # Convert MongoDB cursor results to a list
    most_messages_user = list(most_messages_user)
    most_replies_user = list(most_replies_user)
    most_reactions_user = list(most_reactions_user)

    # Create a dictionary to hold the JSON responses
    response = {
        "most_messages_user": most_messages_user,
        "most_replies_user": most_replies_user,
        "most_reactions_user": most_reactions_user
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
