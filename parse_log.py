import json
from collections import Counter

log_file = r"c:\Games\Python\Rotations\WarcraftLogs\Druid\Restoration\Algethar Academy\Putiputi_f4_log_cR93BVhPKaHwY8C2.json"

try:
    with open(log_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    casts = Counter()
    
    # Assuming the first combatantinfo gives the sourceID for the player
    source_id = None
    for event in data:
        if event.get("type") == "combatantinfo":
            source_id = event.get("sourceID")
            break
            
    if not source_id:
        print("No sourceID found")
    else:
        for event in data:
            if event.get("type") == "cast" and event.get("sourceID") == source_id:
                name = event.get("abilityName", "Unknown")
                casts[name] += 1
                
        print(f"Total Casts for SourceID {source_id}:")
        for name, count in casts.most_common(30):
            print(f"{count}: {name}")
            
except Exception as e:
    print(f"Error: {e}")
