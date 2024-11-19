from flask import Flask, request, render_template
import requests
import json

app = Flask(__name__)

BASE_URL = "https://lichess.org/api"

@app.route('/')
def home():
    return """
    <h1>Welcome to the Lichess Web App</h1>
    <p>Use the following routes:</p>
    <ul>
        <li><a href="/profile">/profile</a> - View a user's profile.</li>
        <li><a href="/leaderboards">/leaderboards</a> - View the top 10 players.</li>
        <li><a href="/tournaments">/tournaments</a> - View ongoing tournaments.</li>
    </ul>
    """


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        response = requests.get(f"{BASE_URL}/user/{username}")
        if response.status_code == 200:
            data = response.json()
            print(data)
            return render_template('profile.html', data=data)
        else:
            return "User not found or error in fetching data.", 404
    return render_template('profile.html')

# Route 2: Leaderboards
@app.route('/leaderboards')
def leaderboards():
    response = requests.get(f"{BASE_URL}/player")
    if response.status_code == 200:
        # response_json = response.json() 
                # Convert the string response into a Python dictionary
        data = json.loads(response)

        # Function to get top players from each category
        def get_top_players(data, category):
            players = []
            for player in data.get(category, []):
                player_info = {
                    "username": player["username"],
                    "rating": player["perfs"].get(category, {}).get("rating", 0),
                    "title": player.get("title", "N/A")
                }
                players.append(player_info)

            # Sort players by rating (in descending order)
            sorted_players = sorted(players, key=lambda x: x["rating"], reverse=True)
            
            return sorted_players

        # Get top players for 'bullet' and 'blitz'
        top_bullet_players = get_top_players(data, "bullet")
        top_blitz_players = get_top_players(data, "blitz")  # Top 10 players
        return render_template('leaderboards.html', players=data)
    return "Error fetching leaderboard data.", 500

# Route 3: Tournaments
@app.route('/tournaments')
def tournaments():
    response = requests.get(f"{BASE_URL}/tournament")
    if response.status_code == 200:
        data = response.json()
        return render_template('tournaments.html', tournaments=data)
    return "Error fetching tournaments data.", 500


@app.route('/favicon.ico')
def favicon():
    return '', 204



if __name__ == '__main__':
    app.run(debug=True)