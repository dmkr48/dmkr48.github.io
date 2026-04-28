# compile_static.py
import os
import json
import hashlib
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

# === CONFIGURATION ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FOLDER = os.path.join(CURRENT_DIR, "json")
OUTPUT_FOLDER = os.path.join(CURRENT_DIR, "static_data")  # Output per-channel JSONs here

# Media repo URLs (your satellite repos)
MEDIA_REPOS = {
    "repo1": "https://raw.githubusercontent.com/dmkr48/gen3-6/main/media",
    "repo2": "https://raw.githubusercontent.com/dmkr48/gen7/main/media",
    "repo3": "https://raw.githubusercontent.com/dmkr48/gen8/main/media",
    "repo4": "https://raw.githubusercontent.com/dmkr48/gen9/main/media",
}

# Map channel IDs to repo keys
CHANNEL_TO_REPO = {
    # repo1: gen 3,6
    1484896149713457213: "repo1", #gita gen6

    1484896111696154674: "repo2", #christy gen7
    1484896125243887791: "repo2", #eli gen7
    1484896166289342536: "repo2", #jessi gen7
    1484896202196521111: "repo2", #muthe gen7
    1484896206223048799: "repo2", #olla gen7
    1484896141614121101: "repo2", #freya gen7

    1484896138522918932: "repo3", #fiony gen8
    1484896185662836807: "repo3", #lulu gen8
    1484896211289899130: "repo3", #oniel gen8

    1484896162787102720: "repo4", #indah gen9
    1484896177127424111: "repo4", #kathrina gen9
    1484896193719828651: "repo4", #marsha gen9

}

def get_repo_url(channel_id):
    """Get the base media URL for a channel ID."""
    repo_key = CHANNEL_TO_REPO.get(int(channel_id))
    if not repo_key:
        raise ValueError(f"Channel {channel_id} not mapped to any media repo")
    return MEDIA_REPOS[repo_key]

def hash_url(url):
    """Generate a short, consistent hash from URL (ignores expiring tokens)."""
    parsed = urlparse(url)
    clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return hashlib.md5(clean.encode()).hexdigest()[:12]

def get_media_type_and_url(attachment, channel_id):
    """Classify media type and build GitHub-hosted URL."""
    if not attachment:
        return "text", None
    
    url = attachment.get("url", "")
    content_type = attachment.get("content_type", "").lower()
    filename = attachment.get("filename", "")
    
    # Determine extension
    ext = Path(filename).suffix.lower()
    if not ext and content_type:
        ext_map = {
            "image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif",
            "audio/mp4": ".m4a", "audio/mpeg": ".mp3",
            "video/mp4": ".mp4", "video/webm": ".webm"
        }
        ext = ext_map.get(content_type, ".bin")
    
    # Classify media type
    if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        media_type = "image"
    elif ext in [".mp3", ".m4a", ".ogg", ".wav"]:
        media_type = "audio"
    elif ext in [".mp4", ".webm", ".mov", ".avi"]:
        media_type = "video"
    else:
        media_type = "file"  # fallback
    
    # Build GitHub Pages URL
    url_hash = hash_url(url)
    base_repo = get_repo_url(channel_id)
    github_url = f"{base_repo}/{channel_id}/{url_hash}{ext}"
    
    return media_type, github_url

def load_and_process_json_files():
    """Load all JSON files and group processed messages by channel_id."""
    channel_data = {}  # {channel_id: [messages...]}
    
    json_files = list(Path(JSON_FOLDER).glob("*.json"))
    print(f"🔍 Found {len(json_files)} JSON file(s)")
    
    for json_path in json_files:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                messages = json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️  Skipping invalid JSON: {json_path.name} ({e})")
            continue
        
        for msg in messages:
            channel_id = str(msg.get("channel_id", ""))
            if not channel_id:
                continue
            
            content = msg.get("content", "")
            timestamp = msg.get("timestamp")
            attachments = msg.get("attachments", [])
            
            if attachments:
                # Process each attachment as a separate entry
                for att in attachments:
                    media_type, github_url = get_media_type_and_url(att, channel_id)
                    entry = {
                        "media_type": media_type,
                        "content": content or "",
                        "url": github_url,
                        "timestamp": timestamp,
                        "channel_id": channel_id
                    }
                    channel_data.setdefault(channel_id, []).append(entry)
            else:
                # Text-only message
                entry = {
                    "media_type": "text",
                    "content": content or "",
                    "url": None,
                    "timestamp": timestamp,
                    "channel_id": channel_id
                }
                channel_data.setdefault(channel_id, []).append(entry)
    
    return channel_data

def save_per_channel_json(channel_data):
    """Save each channel's messages to its own JSON file."""
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    
    for channel_id, messages in channel_data.items():
        # Sort by timestamp (oldest first)
        messages.sort(key=lambda x: x.get("timestamp") or "")
        
        output_path = Path(OUTPUT_FOLDER) / f"{channel_id}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(messages)} messages → {output_path.name}")

def main():
    print(f"📁 Input: {JSON_FOLDER}")
    print(f"📁 Output: {OUTPUT_FOLDER}\n")
    
    channel_data = load_and_process_json_files()
    
    if not channel_data:
        print("⚠️  No messages processed. Check your JSON files.")
        return
    
    save_per_channel_json(channel_data)
    
    print(f"\n🎉 Done! Generated {len(channel_data)} channel file(s)")
    print(f"📦 Output location: {OUTPUT_FOLDER}")

if __name__ == "__main__":
    main()