import os
import yaml
import glob
from collections import defaultdict, Counter

dump_dir = 'simia_data_dump'
yaml_files = glob.glob(os.path.join(dump_dir, '*.yaml'))

root_keys = set()
config_types = set()
step_modifiers = set()
action_names = set()

def parse_step(step):
    if isinstance(step, str):
        parts = step.split(',')
        action = parts[0].split('.')[0]
        action_names.add(action)
        for part in parts[1:]:
            if '=' in part:
                mod_name = part.split('=', 1)[0]
                step_modifiers.add(mod_name)
    elif isinstance(step, dict):
        pass

for file in yaml_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                continue
            root_keys.update(data.keys())
            
            if 'config' in data and isinstance(data['config'], dict):
                for cfg_k, cfg_v in data['config'].items():
                    if isinstance(cfg_v, dict) and 'type' in cfg_v:
                        config_types.add(cfg_v['type'])
            
            if 'lists' in data and isinstance(data['lists'], dict):
                for lst_name, lst_steps in data['lists'].items():
                    if isinstance(lst_steps, list):
                        for step in lst_steps:
                            parse_step(step)
    except Exception as e:
        pass

print("=== ANALYSIS RESULTS ===")
print("Root Keys:", sorted(list(root_keys)))
print("Config Types:", sorted(list(config_types)))
print("Step Modifiers:", sorted(list(step_modifiers)))
print("Number of unique actions/spells:", len(action_names))
