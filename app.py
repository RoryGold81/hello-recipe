# Make sure 'requests' is imported at the top of app.py
import requests
from flask import Flask, render_template, request

# Flask app initialization (should already be there)
app = Flask(__name__)

# index route (should already be there)
@app.route('/')
def index():
    return render_template('index.html')

# Replace the OLD process_recipe function with THIS one:
@app.route('/process_recipe', methods=['POST'])
def process_recipe():
    """Handles the recipe URL submission and attempts to fetch caption via oEmbed."""
    if request.method == 'POST':
        recipe_url = request.form.get('recipe_url')
        if not recipe_url:
            return "Error: No URL provided."

        # --- oEmbed Logic Starts ---
        oembed_endpoint = f"https://api.instagram.com/oembed/?url={recipe_url}" # Using the simple endpoint

        try:
            response = requests.get(oembed_endpoint)

            if response.status_code == 200:
                try:
                    data = response.json()
                    caption = data.get('title', 'Caption not found in oEmbed response.')
                    # Display results including the raw JSON for debugging
                    return f"""
                        <h2>oEmbed Result:</h2>
                        <p><b>Attempted URL:</b> {recipe_url}</p>
                        <p><b>Extracted Caption (from title):</b> {caption}</p>
                        <hr>
                        <p><i>Note: Full caption might be truncated. Check raw JSON below.</i></p>
                        <a href="/">Try another URL</a>
                        <hr>
                        <pre>Raw JSON Response:\n{data}</pre>
                        """
                except requests.exceptions.JSONDecodeError:
                    return f"Error: Failed to decode JSON response from {oembed_endpoint}. Status: {response.status_code}. Response text: <pre>{response.text}</pre>"
            elif response.status_code == 404:
                 return f"Error: Could not find oEmbed data for the URL (404 Not Found). Is the post public and URL correct? Endpoint: {oembed_endpoint}"
            elif response.status_code == 401 or response.status_code == 400:
                 return f"Error: Request failed with status {response.status_code}. Simple oEmbed might require authentication now. Endpoint: {oembed_endpoint}. Response: <pre>{response.text}</pre>"
            else:
                 return f"Error: Received status code {response.status_code} from {oembed_endpoint}. Response: <pre>{response.text}</pre>"

        except requests.exceptions.RequestException as e:
            return f"Error: Failed to connect to the oEmbed endpoint. Details: {e}"
        # --- oEmbed Logic Ends ---

    return "Please submit a URL via the form."

# Main execution block (should already be there)
if __name__ == '__main__':
    app.run(debug=True)
