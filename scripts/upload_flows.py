import os
import re
import requests

def parse_yaml_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    id_match = re.search(r'^id:\s*["\']?([\w-]+)["\']?', content, re.MULTILINE)
    ns_match = re.search(r'^namespace:\s*["\']?([\w.-]+)["\']?', content, re.MULTILINE)
    
    flow_id = id_match.group(1) if id_match else None
    namespace = ns_match.group(1) if ns_match else None
    
    return namespace, flow_id

def upload_flow(filepath):
    namespace, flow_id = parse_yaml_metadata(filepath)
    if not namespace or not flow_id:
        print(f"[ERROR] Could not parse namespace/id for {filepath}")
        return
        
    auth = ("admin@kestra.io", "Admin1234!")
    headers = {"Content-Type": "application/x-yaml"}
    
    with open(filepath, 'rb') as f:
        yaml_content = f.read()
        
    # Try PUT first to update existing flow
    put_url = f"http://localhost:8080/api/v1/flows/{namespace}/{flow_id}"
    response = requests.put(put_url, auth=auth, headers=headers, data=yaml_content)
    
    if response.status_code in [200, 201]:
        print(f"[SUCCESS] Updated existing flow {namespace}.{flow_id}")
    elif response.status_code == 404:
        # Fallback to POST if PUT returns 404 Not Found
        post_url = "http://localhost:8080/api/v1/flows"
        response = requests.post(post_url, auth=auth, headers=headers, data=yaml_content)
        if response.status_code in [200, 201]:
            print(f"[SUCCESS] Created new flow {namespace}.{flow_id}")
        else:
            print(f"[ERROR] Failed to create flow {namespace}.{flow_id}: Status {response.status_code}")
            print(response.text)
    else:
        print(f"[ERROR] Failed to update flow {namespace}.{flow_id}: Status {response.status_code}")
        print(response.text)

def main():
    flow_dir = "flows"
    for filename in os.listdir(flow_dir):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            filepath = os.path.join(flow_dir, filename)
            upload_flow(filepath)

if __name__ == "__main__":
    main()
