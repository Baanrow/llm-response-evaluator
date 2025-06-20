from openai import OpenAI
from CODE_LIBRARY import clr_scr
import time
from collections import Counter
import csv
from datetime import datetime
import pandas as pd
import os

clr_scr()

# Create necessary directories if they don't exist
os.makedirs('tool_21_prompts', exist_ok=True)
os.makedirs('tool_21_runs', exist_ok=True)

# Set the prompt version you want to use
prompt_version = 'V13'
prompt_filename = f'tool_21_prompt_{prompt_version}'

# Read the system message from the prompt file
with open(f'tool_21_prompts/{prompt_filename}.txt', 'r') as file:
    system_message = file.read().strip()

# Define the test cases
current_date_times = [
    "2025-01-13 14:01 Mon",
    "2025-01-14 14:01 Tue",
    "2025-01-15 14:01 Wed",
    "2025-01-16 14:01 Thu",
    "2025-01-17 14:01 Fri",
    "2025-01-18 14:01 Sat",
    "2025-01-19 14:01 Sun"
]

caller_texts = [
    "I want to book an appointment for a haircut for Monday",
    "I want to book an appointment for a haircut for Tuesday",
    "I want to book an appointment for a haircut for Wednesday",
    "I want to book an appointment for a haircut for Thursday",
    "I want to book an appointment for a haircut for Friday",
    "I want to book an appointment for a haircut for Saturday",
    "I want to book an appointment for a haircut for Sunday"
]

# Create CSV file with timestamp in name to avoid overwriting
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f'tool_21_runs/results_{timestamp}_{prompt_filename}.csv'

# Initialize CSV file with headers
with open(output_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['CurrentDateTime', 'CallerText', 'Response', 'Count', 'Result', 'Total_Time_ms', 'Avg_Time_ms'])

# Rate limiting variables
requests_per_minute = 200  # Adjust based on your API tier
request_interval = 60 / requests_per_minute  # Time between requests in seconds
max_requests_before_pause = 180  # Safety margin below the 200 RPM limit

# Keep track of requests for rate limiting
request_count = 0
minute_start = time.time()
total_requests = 0

# Load validation data
validation_df = pd.read_csv('validation_data.csv')

# Create a mapping dictionary that considers both CurrentDateTime and CallerText
validation_map = validation_df.set_index(['CurrentDateTime', 'CallerText'])['Expected Response'].to_dict()

def standardize_date_format(date_str):
    """Convert various date formats to YYYY-MM-DD"""
    try:
        # Handle DD/M/YYYY format
        if '/' in date_str:
            day, month, year = date_str.split('/')
            return f"{year}-{month:0>2}-{day:0>2}"
        # Handle YYYY-MM-DD format
        elif '-' in date_str:
            return date_str
        return date_str
    except:
        return date_str

# Initialize counters for correct/incorrect responses
total_correct = 0
total_incorrect = 0

for current_date_time in current_date_times:
    for caller_text in caller_texts:
        # Check if we're approaching the rate limit and need a longer pause
        if total_requests >= max_requests_before_pause:
            sleep_time = 60  # Full minute pause
            print(f"\nApproaching rate limit. Taking a {sleep_time} second break...")
            time.sleep(sleep_time)
            total_requests = 0
            minute_start = time.time()
            request_count = 0

        print(f"Testing: {current_date_time} with request: {caller_text}")
        
        prompt_text = f"""**currentDateTime**: {current_date_time}

**CallerText**: {caller_text}"""

        responses = []
        start_time = time.time()
        batch_start_time = time.time()

        # Run 10 times for each combination
        for i in range(10):
            # Check if we should pause between batches
            if i == 0 and total_requests > 0:
                elapsed_since_batch = time.time() - batch_start_time
                if elapsed_since_batch < 10:  # If less than 10 seconds since last batch
                    sleep_time = 10 - elapsed_since_batch
                    print(f"Pausing {sleep_time:.1f} seconds between batches...", end='', flush=True)
                    time.sleep(sleep_time)
                batch_start_time = time.time()

            # Rate limiting checks
            current_time = time.time()
            if current_time - minute_start >= 60:
                request_count = 0
                minute_start = current_time
            
            if request_count >= requests_per_minute:
                sleep_time = 60 - (current_time - minute_start)
                print(f"Rate limit approached, sleeping for {sleep_time:.1f} seconds...", end='', flush=True)
                time.sleep(sleep_time)
                minute_start = time.time()
                request_count = 0

            print(f"\rMaking API call {i+1}/10... (Total requests: {total_requests})", end='', flush=True)
            try:
                assistant = OpenAI().chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt_text}
                    ]
                )
                responses.append(assistant.choices[0].message.content)
                request_count += 1
                total_requests += 1

                # Add a minimum delay between individual calls
                time.sleep(max(request_interval, 0.5))  # At least 0.5 second between calls

            except Exception as e:
                print(f"Error making API call: {e}")
                print("Taking a longer break due to error...")
                time.sleep(120)  # Wait two minutes if there's an error
                continue

        # After completing a batch of 10, print status
        print(f"\nCompleted batch. Total requests so far: {total_requests}")
        if total_requests % 50 == 0:  # Every 50 requests
            print("Taking a longer break every 50 requests...")
            time.sleep(30)

        # Calculate timing
        end_time = time.time()
        response_time = (end_time - start_time) * 1000

        # Count responses
        response_counts = Counter(responses)

        # Write results to CSV
        with open(output_filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for response, count in response_counts.items():
                # Get expected response and validate
                current_key = (current_date_time, caller_text)
                expected_response = validation_map.get(current_key, 'No expected value found')
                expected_response = standardize_date_format(expected_response)
                result = 'correct' if standardize_date_format(response) == expected_response else 'incorrect'
                
                # Update counters based on result and count
                if result == 'correct':
                    total_correct += count
                else:
                    total_incorrect += count
                
                writer.writerow([
                    current_date_time,
                    caller_text,
                    response,
                    count,
                    result,
                    f"{response_time:.0f}",
                    f"{(response_time/10):.0f}"
                ])

        # Validation results
        for response, count in response_counts.items():
            current_key = (current_date_time, caller_text)
            expected_response = validation_map.get(current_key, 'No expected value found')
            expected_response = standardize_date_format(expected_response)
            result = 'correct' if standardize_date_format(response) == expected_response else 'incorrect'
            print(f"{response} ({count}) {result} (Expected: {expected_response})")

        print()  # Single empty line after each batch

# After all tests are complete, append the accuracy statistics
with open(output_filename, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([])  # Empty row for spacing
    writer.writerow(['Total Correct:', total_correct])
    writer.writerow(['Total Incorrect:', total_incorrect])
    accuracy = (total_correct / (total_correct + total_incorrect)) * 100
    writer.writerow(['Accuracy:', f"{accuracy:.4f}%"])

print(f"\nResults have been saved to {output_filename}")
