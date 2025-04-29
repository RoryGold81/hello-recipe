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
            print(f"Attempting to fetch oEmbed data from: {oembed_endpoint}")
            response = requests.get(oembed_endpoint)
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Response text: {response.text[:500]}...")  # Print first 500 chars of response

            # Check if the response is JSON by looking at the Content-Type header
            content_type = response.headers.get('Content-Type', '')
            is_json = 'application/json' in content_type.lower()
            
            if response.status_code == 200:
                if is_json:
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
                        return f"""
                            <h2>Error: Failed to decode JSON response</h2>
                            <p>The Instagram oEmbed endpoint returned a response with status code 200, but the content could not be parsed as JSON.</p>
                            <p><b>Attempted URL:</b> {recipe_url}</p>
                            <p><b>Endpoint:</b> {oembed_endpoint}</p>
                            <p>This could be because:</p>
                            <ul>
                                <li>Instagram's oEmbed API might have changed and now requires authentication</li>
                                <li>The URL format might be incorrect</li>
                                <li>Instagram might be returning HTML instead of JSON</li>
                            </ul>
                            <hr>
                            <p><a href="/">Try another URL</a></p>
                            <hr>
                            <h3>Response Headers:</h3>
                            <pre>{response.headers}</pre>
                            <h3>Response Content (first 1000 characters):</h3>
                            <pre>{response.text[:1000]}...</pre>
                            """
                else:
                    # Response is not JSON (likely HTML)
                    return f"""
                        <h2>Error: Instagram returned HTML instead of JSON</h2>
                        <p>The Instagram oEmbed endpoint returned HTML content instead of JSON data.</p>
                        <p><b>Attempted URL:</b> {recipe_url}</p>
                        <p><b>Endpoint:</b> {oembed_endpoint}</p>
                        <p><b>Content-Type:</b> {content_type}</p>
                        <p>This likely means that:</p>
                        <ul>
                            <li>Instagram's oEmbed API now requires authentication</li>
                            <li>The simple endpoint is no longer supported</li>
                            <li>Instagram is redirecting to their website instead of providing oEmbed data</li>
                        </ul>
                        <hr>
                        <p><a href="/">Try another URL</a></p>
                        <hr>
                        <h3>Response Headers:</h3>
                        <pre>{response.headers}</pre>
                        <h3>Response Content (first 1000 characters):</h3>
                        <pre>{response.text[:1000]}...</pre>
                        """
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
