import requests
import webbrowser
import time

# Define the base headers (with placeholders for dynamic parts)
base_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://d2kpeuq6fthlg5.cloudfront.net",
    "priority": "u=1, i",
    "referer": "https://d2kpeuq6fthlg5.cloudfront.net/",
    "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129", "Microsoft Edge WebView2";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
}

def read_init_data(file_path):
    """Reads multiple init-data (queries) from the specified file."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def update_headers(headers, token=None):
    """Updates headers with authorization token if provided."""
    updated_headers = headers.copy()
    if token:
        updated_headers["authorization"] = f"Bearer {token}"
    return updated_headers

def verify_login(init_data):
    """Verifies the login using the provided init-data."""
    url = "https://api.gumart.click/api/verify"
    payload = {
        "telegram_data": init_data,
        "ref_id": None
    }

    response = requests.post(url, headers=base_headers, json=payload)
    if response.status_code == 200:
        print("Verification successful.")
        return response.json()
    else:
        print(f"Verification failed. Status code: {response.status_code}")
        return None

def login(init_data):
    """Logs in using the verified init-data and returns the login response."""
    url = "https://api.gumart.click/api/login"
    payload = {
        "telegram_data": init_data,
        "ref_id": None
    }

    response = requests.post(url, headers=base_headers, json=payload)
    if response.status_code == 200:
        print("Login successful!")
        return response.json().get("data", {})
    else:
        print(f"Login failed. Status code: {response.status_code}")
        return None

def fetch_tasks(access_token):
    """Fetches tasks using the provided access token."""
    url = "https://api.gumart.click/api/missions"
    headers = update_headers(base_headers, access_token)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Tasks fetched successfully!")
        return response.json()
    else:
        print(f"Failed to fetch tasks. Status code: {response.status_code}")
        return None

def complete_task(access_token, task_id):
    """Completes the task with the given task ID."""
    url = f"https://api.gumart.click/api/missions/{task_id}/start"
    headers = update_headers(base_headers, access_token)

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        task_data = response.json().get("data", {})
        if task_data:
            print(f"Task {task_id} started successfully.")
            link = task_data.get("function_data", {}).get("link")
            if link:
                print(f"Opening task link: {link}")
                webbrowser.open(link)  # Open the link in a browser
            return task_data
        else:
            print(f"Task {task_id} started, but no task data returned. Full response: {response.json()}")
            return None
    else:
        print(f"Failed to start task {task_id}. Status code: {response.status_code}")
        return None

def claim_task(access_token, task_id):
    """Claims the reward for the task with the given task ID."""
    url = f"https://api.gumart.click/api/missions/{task_id}/claim"
    headers = update_headers(base_headers, access_token)

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        claim_data = response.json().get("data", {})
        if claim_data:
            print(f"Task {task_id} claimed successfully! Points earned: {claim_data.get('point')}")
            return claim_data
        else:
            print(f"Task {task_id} claimed, but no data returned. Response: {response.json()}")
            return None
    else:
        print(f"Failed to claim task {task_id}. Status code: {response.status_code}")
        return None

def auto_click_claim(access_token):
    """Automatically clicks claim and prints the claim value and updated balance."""
    url = "https://api.gumart.click/api/claim"
    headers = update_headers(base_headers, access_token)

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        claim_data = response.json().get("data", {})
        if claim_data:
            claim_value = claim_data.get("claim_value")
            balance = claim_data.get("balance")
            print(f"Claim successful! Claim value: {claim_value}, Updated balance: {balance}")
        else:
            print(f"Claim successful, but no claim data returned. Response: {response.json()}")
    else:
        print(f"Failed to claim. Status code: {response.status_code}")

def process_tasks(access_token, task_list):
    """Process the tasks by completing and claiming them, with a 30-second delay between each task."""
    for task in task_list:
        task_id = task.get("id")
        print(f"Processing task {task_id}: {task.get('title')}")
        
        # Complete the task
        task_data = complete_task(access_token, task_id)
        if task_data and task_data.get("status") == "in_progress":
            # After completing the task, claim it
            claim_data = claim_task(access_token, task_id)
            if claim_data:
                print(f"Task {task_id} claimed successfully.")
        
        # Wait for 30 seconds before processing the next task
        print("Waiting for 30 seconds before processing the next task...")
        time.sleep(30)

if __name__ == "__main__":
    init_data_list = read_init_data("query.txt")  # Read multiple queries from file

    # Process each query one by one
    for index, init_data in enumerate(init_data_list):
        print(f"\n--- Executing query {index + 1}/{len(init_data_list)} ---")
        
        # Step 1: Verify login
        verify_result = verify_login(init_data)
        if verify_result and verify_result.get("data", {}).get("is_verify") == 1:
            login_data = login(init_data)
            if login_data:
                access_token = login_data.get("access_token")
                print(f"Access token for query {index + 1}: {access_token}")
                
                # Step 2: Fetch tasks and process them
                tasks_response = fetch_tasks(access_token)
                if tasks_response:
                    # Extract tasks from different categories and process them
                    missions = tasks_response.get("data", {}).get("missions", {})
                    tasks = tasks_response.get("data", {}).get("tasks", {})
                    
                    # Process missions (e.g., daily, fixed)
                    for task_group in missions.values():
                        process_tasks(access_token, task_group)
                    
                    # Process other tasks (e.g., dog, cowtopia, etc.)
                    for task_group in tasks.values():
                        process_tasks(access_token, task_group)
                
                # Step 3: Automatically click claim
                auto_click_claim(access_token)
        else:
            print(f"Verification failed for query {index + 1}.")
