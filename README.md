# Chess-Dragon

### **Chess-Dragon**: a user base web application for pairing players in a tournament using (swiss) and (knockout) systems, from writing down the names of the players, pairing them according to the rule of the system, writing the score for each player after the round, and displaying the ranking from first to last.

### Database Functionality
* uses SQLite3 db for storing the user data.
* consists of two models apart from the built-in User model.
* VideoPost: stores the link of the YouTube video, only superusers can add a link, and the links will display on the community page.
* UserData: consists of three fields, user where each user can access the other data, swiss_data stores the data of the players in JSON format, and knockout_data also stores the data of the players in JSON format, but inside the JSON consists of two lists (white_players, black_players).
* JSON field example for the swiss_data:
data[name] = {
    "score": 0.0,
    "points": [],
    "color_list": [],
    "vs_players": [],
    "rounds": [],
    "color": {
        'last_played_color': '',
        'White': 0,
        'Black': 0
    }
} 
* JSON field example for the knockout_data: 
data = {
    'white_players': [],
    'black_players': []
}

<br>

### Back-End Functionality
* all functions are in views.py file.
* 


