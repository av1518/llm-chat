import requests
import json


def stream_content(url, data):
    """
    Make a streaming POST request and yield the 'content' part of each JSON response as they arrive.

    :param url: The URL to which the POST request is made.
    :param data: A dictionary or JSON string to be sent in the body of the POST request.
    """
    headers = {"Content-Type": "application/json"}

    # If data is a dictionary, convert it to a JSON string
    if isinstance(data, dict):
        data = json.dumps(data)

    # Make a streaming POST request
    with requests.post(url, data=data, headers=headers, stream=True) as response:
        # Raise an error for bad responses
        response.raise_for_status()

        # Process the stream
        for chunk in response.iter_lines():
            if chunk:
                # Decode chunk from bytes to string
                decoded_chunk = chunk.decode("utf-8")
                try:
                    # Convert string to JSON
                    json_chunk = json.loads(decoded_chunk)

                    # if the model is done generating, return
                    if json_chunk.get("done") == True:
                        return

                    # Yield the 'content' part
                    yield json_chunk["message"]["content"]
                except json.JSONDecodeError:
                    continue
