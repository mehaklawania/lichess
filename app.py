from flask import Flask, request, render_template
import requests

app = Flask(__name__)

BASE_URL = "https://lichess.org/api"

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{BASE_URL}/user/{username}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            profile_data = {
                'username': data.get('username'),
                'profile_url': f"https://lichess.org/image/150/{username}",
                'bio': data.get('profile', {}).get('bio', 'No bio available'),
                'total_games': sum(perf.get('games', 0) for perf in data.get('perfs', {}).values()),
                'ratings': {
                    'blitz': data.get('perfs', {}).get('blitz', {}).get('rating', 'N/A'),
                    'bullet': data.get('perfs', {}).get('bullet', {}).get('rating', 'N/A'),
                    'rapid': data.get('perfs', {}).get('rapid', {}).get('rating', 'N/A')
                }
            }
            return render_template('profile.html', data=profile_data)
        else:
            return "User not found or error in fetching data.", 404
    return render_template('profile.html')

@app.route('/leaderboards')
def leaderboards():
    # Get top 10 players for different time controls
    variants = ['bullet', 'blitz', 'rapid']
    leaderboards_data = {}
    
    for variant in variants:
        response = requests.get(f"{BASE_URL}/player/top/10/{variant}")
        if response.status_code == 200:
            data = response.json()
            leaderboards_data[variant] = data.get('users', [])
    
    return render_template('leaderboards.html', leaderboards=leaderboards_data)

@app.route('/tournaments')
def tournaments():
    headers = {
        'Accept': 'application/json'
    }
    try:
        response = requests.get(f"{BASE_URL}/tournament", headers=headers)
        response.raise_for_status()
        
        all_tournaments = response.json()
        tournaments_data = []
        
        if isinstance(all_tournaments, list):
            for tournament in all_tournaments:
                if isinstance(tournament, dict):
                    # Process variant information
                    variant_info = tournament.get('variant', {})
                    variant_name = variant_info.get('name', 'Standard') if isinstance(variant_info, dict) else 'Standard'
                    
                    processed_tournament = {
                        'name': tournament.get('fullName', 'Unnamed Tournament'),
                        'variant': variant_name,  # Use clean variant name
                        'players': tournament.get('nbPlayers', 0),
                        'status': tournament.get('status', 'Unknown'),
                        'duration': tournament.get('minutes', 0),
                        'id': tournament.get('id', ''),
                        'timeControl': f"{tournament.get('clock', {}).get('limit', 0) // 60}+{tournament.get('clock', {}).get('increment', 0)}"
                    }
                    tournaments_data.append(processed_tournament)
        else:
            created = all_tournaments.get('created', [])
            started = all_tournaments.get('started', [])
            
            for tournament in created + started:
                if isinstance(tournament, dict):
                    # Process variant information
                    variant_info = tournament.get('variant', {})
                    variant_name = variant_info.get('name', 'Standard') if isinstance(variant_info, dict) else 'Standard'
                    
                    processed_tournament = {
                        'name': tournament.get('fullName', 'Unnamed Tournament'),
                        'variant': variant_name,  # Use clean variant name
                        'players': tournament.get('nbPlayers', 0),
                        'status': tournament.get('status', 'Unknown'),
                        'duration': tournament.get('minutes', 0),
                        'id': tournament.get('id', ''),
                        'timeControl': f"{tournament.get('clock', {}).get('limit', 0) // 60}+{tournament.get('clock', {}).get('increment', 0)}"
                    }
                    tournaments_data.append(processed_tournament)
        
        return render_template('tournaments.html', tournaments=tournaments_data)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tournaments: {str(e)}")
        return f"Error fetching tournaments data: {str(e)}", 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return f"An unexpected error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
