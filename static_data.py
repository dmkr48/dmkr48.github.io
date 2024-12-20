import os
import json
import hashlib
from urllib.parse import urlparse
from datetime import datetime, timezone

# Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
json_folder_path = os.path.join(current_dir, "json")
media_folder_path = "https://raw.githubusercontent.com/dmkr48/images/refs/heads/main/media"
output_file_path = os.path.join(current_dir, "static_messages.json")

def get_media_path(channel_id):
    return f"{media_folder_path}/{channel_id}"

def load_json_files_with_channel():
    messages = []
    for filename in os.listdir(json_folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(json_folder_path, filename), 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    for item in data:
                        content = item.get('content')
                        timestamp = item.get('timestamp')
                        channel_id = item.get('channel_id')
                        dt = datetime.fromisoformat(timestamp) if timestamp else None
                        date_str = dt.strftime("%Y-%m-%d") if dt else None

                        if item.get('attachments'):
                            for attachment in item['attachments']:
                                url = attachment.get('url')
                                messages.append({
                                    "content": content,
                                    "url": url,
                                    "date_str": date_str,
                                    "timestamp": dt.isoformat() if dt else None,
                                    "channel_id": channel_id
                                })
                        else:
                            messages.append({
                                "content": content,
                                "url": None,
                                "date_str": date_str,
                                "timestamp": dt.isoformat() if dt else None,
                                "channel_id": channel_id
                            })
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from {filename}: {e}")
    return messages

def classify_media_type(url, channel_id):
    if not url:
        return "text", None

    parsed_url = urlparse(url)
    path = parsed_url.path
    url_extension = os.path.splitext(path)[1]
    url_hash = hashlib.md5(url.encode()).hexdigest()
    media_path = get_media_path(channel_id)

    if url_extension.lower() in ['.mp3', '.m4a']:
        file_url = f"{media_folder_path}/{channel_id}/{url_hash}.mp3"
        return "audio", file_url
    elif url_extension.lower() in ['.jpg', '.png', '.gif']:
        file_url = f"{media_folder_path}/{channel_id}/{url_hash}.png"
        return "image", file_url

    return "unknown", url

def generate_static_data():
    messages = load_json_files_with_channel()
    processed_messages = []

    for message in messages:
        media_type, static_url = classify_media_type(message["url"], message["channel_id"])
        processed_messages.append({
            "content": message["content"],
            "url": static_url,
            "date_str": message["date_str"],
            "timestamp": message["timestamp"],
            "channel_id": message["channel_id"],
            "media_type": media_type
        })

    # Save to static JSON file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(processed_messages, output_file, indent=4, ensure_ascii=False)

    print(f"Static data generated at {output_file_path}")

# Run the script
if __name__ == "__main__":
    generate_static_data()
