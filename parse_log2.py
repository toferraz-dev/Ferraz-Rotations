import json
from collections import Counter, defaultdict

log_file = r"c:\Games\Python\Rotations\WarcraftLogs\Druid\Restoration\Algethar Academy\Flaymaker_f1_log_bDKAg9HjRW3MrxpF.json"

try:
    with open(log_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    casts_by_source = defaultdict(Counter)
    
    for event in data:
        if event.get("type") == "cast":
            source_id = event.get("sourceID")
            if source_id:
                name = event.get("abilityName", "Unknown")
                casts_by_source[source_id][name] += 1
                
    # Find the source ID with the most casts (likely the main player)
    main_source_id = max(casts_by_source.keys(), key=lambda k: sum(casts_by_source[k].values()))
            
    print(f"Total Casts for Main SourceID {main_source_id}:")
    for name, count in casts_by_source[main_source_id].most_common():
        print(f"{count}: {name}")
        
    print("\nTotal events in file:", len(data))
    
except Exception as e:
    print(f"Error: {e}")
