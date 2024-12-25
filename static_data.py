import os
import json
import hashlib
from urllib.parse import urlparse
from datetime import datetime, timezone

# Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
json_folder_path = os.path.join(current_dir, "json")
media_folder_path_1 = "https://raw.githubusercontent.com/dmkr48/images/main/media"
media_folder_path_2 = "https://raw.githubusercontent.com/dmkr48/images2/main/media"
output_file_path = os.path.join(current_dir, "static_messages.json")

# Channel mapping to media folder paths
channel_media_mapping = {
    #gen 3, 6, 7, 8, 9, 10
    "media_folder_path_1": [1177001515857227857, 1177001494889893909, #gen3
                            1177001972012949534, #gen6
                            1177007541973172254, 1177007658419617872, 1177007704468902059, 1177005953447645194, 1177007628568764508, 1177007682947928075, #gen7
                            1177015897873977474, 1177015924767858728, 1177015971756646601, 1177016028794990602, #gen8
                            1177016672918442054, 1177021173280808990, 1177034551550283787, #gen9
                            1177035130968227840, 1177022205306089512, 1177021537912639508, 1177035013162815598, 1177034734954618912, 1177021510871953559, 1177022335795073165], #gen10
    "media_folder_path_2": [1177117244686336100, 1177022335795073165, 1177117264487657513, 1177129851526848633, 1177117307466690611, 1177129890605191188, 1177129969701363712, 1177164766872092752, 1177164785788403753, 1177035322547249223, 1177035367942201494, 1177129826532999199, #gen11
                            1208078091814043698, 1208078154695180358, 1208078327886258217, 1208079396183875594, 1208082554259906581, 1208078296231968850, 1208081737683570688, 1208081548965060608, 1208081645425401897, 1208082171806613585, 1208082406486183976, 1208081780964331623, 1208082212084252792, 1208082254715166751, 1208082314714947614], #gen12
}

def get_media_path(channel_id):
    if channel_id in channel_media_mapping["media_folder_path_1"]:
        return media_folder_path_1
    elif channel_id in channel_media_mapping["media_folder_path_2"]:
        return media_folder_path_2
    else:
        raise ValueError(f"Channel ID {channel_id} is not mapped to a media folder.")

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
        file_url = f"{media_path}/{channel_id}/{url_hash}.mp3"
        return "audio", file_url
    elif url_extension.lower() in ['.jpg', '.png', '.gif']:
        file_url = f"{media_path}/{channel_id}/{url_hash}.png"
        return "image", file_url

    return "unknown", url

def generate_static_data():
    messages = load_json_files_with_channel()
    processed_messages = []

    for message in messages:
        try:
            media_type, static_url = classify_media_type(message["url"], message["channel_id"])
            processed_messages.append({
                "content": message["content"],
                "url": static_url,
                "date_str": message["date_str"],
                "timestamp": message["timestamp"],
                "channel_id": message["channel_id"],
                "media_type": media_type
            })
        except ValueError as e:
            print(f"Error processing message: {e}")

    # Save to static JSON file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(processed_messages, output_file, indent=4, ensure_ascii=False)

    print(f"Static data generated at {output_file_path}")

# Run the script
if __name__ == "__main__":
    generate_static_data()
