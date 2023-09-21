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
* **file_handler**: used for handling the swiss_data in terms of read and write, has three parameters, action which represent either reading 'r' or writing 'w' the data, user to retrieve or update the swiss_data of the requested user, and obj which is used when the user wants to update the data of the players which is a dictionary. 
* **score_handler**: returns a list that consists of unique scores based on the player's scores from high to low, if there is data of the players.
* **is_logged_in**: a decorator used for 4 pages, simply checks if the user is authenticated, if it is then it can access the page, if not it will be redirected to the error page.
* **(home_page, community_page, error_page)**: those pages are mostly static apart from community pages which get all the links of the VideoPost model.
* **login_page**: used for logging the user to use the website features, when the user submits the form, checks if the user is authenticated, if it is it will redirect to the profile page. 
* **profile_page**: used for normal users that are not admin, if it is admin automatically redirects to the super_profile_page, if not it will render the profile page, the normal user in the profile page, can use the logout button to log out from the website.
* **super_profile_page**: only for admin users where they can (create users, delete users, view users, post links, delete links, view links, and log out) the admin can create normal users, and only view and delete normal users aswell.
* siwss system: three pages used for handling the swiss system (standing_page, tournament_page, and round_page).
* **standing_page**: displays the standing of the players from high to low, using file_handler and score_handler we get the data of the players and unique_scores, then rank them based on their score and the scores list, store all the info in the ranking dict, then we check the scores list for the print functionality.
* **tournament_page**: in the page consists of creating tournament by writing the names of the players, or by importing from excel file, also has reset standing for the players to reset the data of each player, then it can show the players as a dropdown button indivitualy to view more info, in the back end if the request is post, when the reset standing button is submited it will reset the dict of all of the players to default value, and a js pop up message apear after ward, if the submited button is create then we collect the name of the inputs as a list since all the inputs has same name, checks for any invalid length, then itterate over every name, and save it inside the data dict, also checks for the duplicate if there is then it will ad '_2', apart from writing the names manualy we can upload an excel file to the back end using upload-button, get the data of the sheet using pandas module we read the file, and then checks if 'Names' column is in the sheet, also checks the length of the Names it must be (2, 4, 8, 16, 32, 64, 128, ...) after that save each name in the data dict, all three post request after finishing their task use the file_handler to update the data, also when the scores list is at zero, it wont display the reset button since it all the players has default value

