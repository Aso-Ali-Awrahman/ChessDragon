from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .models import VideoPost, UserData
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from random import shuffle, choice
import pandas as pd



def file_handler(action, user, obj):
    try:
        user = UserData.objects.get(user=user)
        if action == 'r':
            return user.swiss_data
        else:
            user.swiss_data = obj
            user.save()
    except ObjectDoesNotExist:
        return redirect('error-page', 'guess you want to mess my website structure!')


def score_handler(obj):
    if obj != {}:
        unique_scores = []
        for name in obj:
            player_score = obj[name]['score']
            if player_score not in unique_scores:
                unique_scores.append(player_score)
                
        unique_scores.sort(reverse=True)
        return unique_scores
    return [0]


# decorators
def is_logged_in(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('error-page', 'you need to log in to sacrifice your roooook!!')
        return func(request, *args, **kwargs)
    return wrapper



# Create your views here.

# these three views mostly static
def home_page(request):
    return render(request, 'home-page.html')


def community_page(request):
    links = VideoPost.objects.all()
    return render(request, 'community-page.html', {'links':links})


def error_page(request, message):
    return render(request, 'error-page.html', {'message':message})

####

def login_page(request):
    
    if request.user.is_authenticated:
        return redirect('profile')
    
    message = '' 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user_authorize = authenticate(request, username=username, password=password)
        
        if user_authorize is not None:
            login(request, user_authorize)
            return redirect('profile')
        
        message = 'incorrect username/password!'    
        
    
    return render(request, 'login-page.html', {'message':message})


@login_required(login_url='login')
def profile_page(request):  
    if request.user.is_superuser:
            return redirect('super-profile')
    
    if request.method == 'POST':
        if 'logout-button' in request.POST:
            logout(request)
            return redirect('home')
        
    return render(request, 'profile-page.html')


@login_required(login_url='login')
def super_profile_page(request):
    
    if not request.user.is_superuser:  # if it is a regular user it will redirect to the profile_page
        return redirect('profile')
    
    if request.method == 'POST':
        if 'create-user-button' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if not username or not password:
                return redirect('profile')
            
            try:
                User.objects.get(username=username)
                return redirect('error-page', 'this username is already exist !!')
            except User.DoesNotExist:
                new_user = User.objects.create_user(username=username, password=password)
                UserData(user=new_user, swiss_data={}, knockout_data={}).save()
                
        elif 'delete-user-button' in request.POST:
            username = request.POST.get('delete-user-button')
            try:
                user_to_delete = User.objects.get(username=username)
                user_to_delete.delete()
            except User.DoesNotExist:
                return redirect('error-page', "don't mess my website structure or i will sacrifice youu!!")
        
        elif 'post-button' in request.POST:
            link = request.POST.get('link')
            if not link:
                return redirect('error-page', 'you need to paste a link to post it!!')
            
            VideoPost(link=f'embed/{link}').save()
       
        elif 'delete-link-button' in request.POST:
            link = request.POST.get('delete-link-button')
            try:
                VideoPost.objects.get(link=link).delete()
            except ObjectDoesNotExist:
                return redirect('error-page', "don't mess my website structure or i will sacrifice youu!!")    

        elif 'logout-button' in request.POST:
            logout(request)
            return redirect('home')
        
    users = User.objects.filter(is_superuser=False)
    link_videos = VideoPost.objects.all()
    
    return render(request, 'super-profile-page.html', {'users':users, 'link_videos':link_videos})


# website logic of chess pairing 

# swiss-system
@is_logged_in
def standing_page(request):
    data = file_handler(action='r', user=request.user, obj=None)

    if data == {} or len(data) % 2 == 1:
        return redirect('error-page', 'in order to have a score you need to play, in order to play you need to create a tournament')
         
    context = {
        'ranking': None,
        'is_print': False,
        'round_count': None
    } 
    
    scores = score_handler(obj=data)
    
    ranking = {}  # it contain all the data but sorted base of score!
    
    for score in scores:
        for name in data:
            if ranking.get(name) is None:
                if data[name]['score'] == score:
                    ranking[name] = data[name]

    if scores[0] != 0 and len(scores) != 1:
        for name in data:
            context['round_count'] = range(len(data[name]['rounds']))
            if len(context['round_count']) != 0:
                context['is_print'] = True   
            break  # we just need one player, because all of them are same in count    

    context['ranking'] = ranking

    return render(request, 'standing-page.html', context)
    
    
@is_logged_in
def tournament_page(request):
    data = file_handler(action='r', user=request.user, obj=None)
    message = ''
    
    if request.method == 'POST':
        if 'reset-button' in request.POST:
            if data == {} or len(data) % 2 == 1:  # just for safety ;)
                return redirect('error-page', 'how many players do you have? 0 hhhh')

            for name in data:
                try:
                    data[name]['score'] = 0.0
                    data[name]['points'] = []
                    data[name]['rounds'] = []
                    data[name]['color_list'] = []
                    data[name]['vs_players'] = []
                    data[name]['color'] = {
                        'last_played_color': '',
                        'White': 0,
                        'Black': 0
                    }
                except KeyError:
                    return redirect('tournament')
            message = 'Data has been Reset'
            
        elif 'create-button' in request.POST:
            names = request.POST.getlist('names')
            data = {} 
            player_count = len(names)
            
            if player_count == 0 or player_count % 2 == 1:
                return redirect('error-page', 'chess is a game that need even number of player')
            
            for i in range(player_count):
                name = names[i].strip().title()
                while True:
                    if name == '':
                        return redirect('error-page', 'Are you trying to play against ghost, idiot ??')
                    elif data.get(name) is None:  # if same name is already inserted it will add '_2'
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
                        break
                    else:
                        name += '_2'           
            message = 'Tournament Created'
        
        elif 'upload-button' in request.POST:
            try:
                excel_file = request.FILES['excel_file']
            except:
                return redirect('error-page', 'guess you want to mess my website structure!')

            df = pd.read_excel(excel_file)
        
            if 'Names' not in df.columns:
                return redirect('error-page', "The uploaded Excel file does not contain the (Names) header. Please upload a valid file.")
            
            df_length = len(df.Names)
            
            if df_length == 0 or df_length % 2 == 1 or df_length <= 4:
                return redirect('error-page', 'invalid number of players!!')
            
            data = {}
            
            for name in df.Names:
                while True:
                    if name == '':
                        return redirect('error-page', 'Are you trying to play against ghost, idiot ??')
                    elif data.get(name) is None:  # if same name is already inserted it will add '_2'
                        data[name.title()] = {
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
                        break
                    else:
                        name += '_2'
                        
            message = 'Tournament Created'            
                
        file_handler(action='w', user=request.user, obj=data)  # used for both reset and create/upload tournament
        # # # # # #
        
    context = {
        'data': data,
        'is_there_data': False,
        'message': message
    }
    
    scores = score_handler(obj=data)
    
    if scores[0] != 0 and len(scores) != 1:
        context['is_there_data'] = True
    
    return render(request, 'tournament-page.html', context)


@is_logged_in
def round_page(request):
    data = file_handler(action='r', user=request.user, obj=None)
    
    if data == {} or len(data) % 2 == 1:
        return redirect('error-page', 'create tournament to use round play for pairing the players!')
    
    context ={
        'players_pair': None,
        'is_pairing': False,
        'is_incomplete':False
    }
    
    if request.method == 'POST':

        if 'pair-button' in request.POST:
            unique_scores = score_handler(obj=data)

            # shuffling the data, but first convert to list
            list_data = list(data.items())
            shuffle(list_data)
            shuffle(list_data)
            data = dict(list_data)
            
            naming_list_list = []  # before final, lists the names inside a list from high to low based on score

            for this_score in unique_scores:
                ls = []
                for name in data:
                    if data[name]['score'] == this_score:
                        ls.append(name)
                naming_list_list.append(ls)
                
            # in this list the players will be pair lists inside the list, that has the most accurate pairing based on color
            final_pair_list = []  
            pair = []
            color_order = 'White'
            # using this algorithm the lsit has the highest accurate pairirng based on the color
            for name_list in naming_list_list:
                while len(name_list) != 0:
                    for name in name_list:
                        if data[name]['color']['last_played_color'] == color_order:
                            pair.append(name)
                            name_list.remove(name)
                            break
                        elif data[name]['color']['last_played_color'] == '':
                            pair.append(name)
                            name_list.remove(name)
                            break
                    
                    if color_order == 'White':
                        color_order = 'Black'
                    else:
                        color_order = 'White'
                    
                    if len(pair) == 2:
                        final_pair_list.append(pair)
                        pair = []
 
            ##########################################
            # this is for user limitation if they clicked the pair-button multiple time, it will delete the incomplete data 
            for name in data:
                if len(data[name]['points']) != len(data[name]['vs_players']):
                    data[name]['vs_players'].pop()
                    data[name]['color_list'].pop()
                    if data[name]['color']['last_played_color'] == 'White':
                        data[name]['color']['last_played_color'] = 'Black'
                        data[name]['color']['White'] -= 1
                    else:
                        data[name]['color']['last_played_color'] = 'White'
                        data[name]['color']['Black'] -= 1
                else:
                    break  # if one player is ok then all of it are same
            ##########################################
            white_players = []
            black_players = []

            for pair_list in final_pair_list:  # each pair_list consists of two player, that play each other
                first_player = data[pair_list[0]]['color']
                second_player = data[pair_list[1]]['color']

                any_change = False  # just for efficiency
                
                while first_player['last_played_color'] == second_player['last_played_color']:
                    any_change = True
                    if first_player['White'] < second_player['White']:
                        first_player['last_played_color'] = 'Black'  # it should be in reverse, to be white in this round
                        second_player['last_played_color'] = 'White'

                    elif second_player['White'] < first_player['White']:
                        second_player['last_played_color'] = 'Black'
                        first_player['last_played_color'] = 'White'
                    else:
                        first_player['last_played_color'] = choice(['White', 'Black'])
                        second_player['last_played_color'] = choice(['White', 'Black'])

                # setting the color dict if there was any change in the while loop
                if any_change:
                    data[pair_list[0]]['color'] = first_player
                    data[pair_list[1]]['color'] = second_player

                for name in pair_list:
                    if data[name]['color']['last_played_color'] == 'White':
                        black_players.append(name)
                        data[name]['color']['Black'] += 1
                        data[name]['color_list'].append('B')
                    else:
                        white_players.append(name)
                        data[name]['color']['White'] += 1
                        data[name]['color_list'].append('W')

                # end of for loop of final_pair_list
    
            players_pair = {
                # white_player: black_player,
            }

            for i in range(len(white_players)):
                players_pair[white_players[i]] = black_players[i]  # for the front end, dict is easy to use
                
                # setting the data (last_color and vs_players)
                data[white_players[i]]['color']['last_played_color'] = 'White'
                data[white_players[i]]['vs_players'].append(black_players[i])

                data[black_players[i]]['color']['last_played_color'] = 'Black'
                data[black_players[i]]['vs_players'].append(white_players[i])
        
            file_handler(action='w', user=request.user, obj=data)
            
            context['players_pair'] = players_pair
            context['is_pairing'] = True
            
            return render(request, 'round-page.html', context)

        elif 'upload-score-button' in request.POST:
            for name in data:
                try:
                    score = float(request.POST.get(name))
                    if score not in [1, 0.5, 0]:  # to ensure that the user wont to play with the database or server
                        return redirect('error-page', 'insert valid score (1, 0.5, 0) !!')
                except ValueError:
                    return redirect('error-page', 'insert valid score (1, 0.5, 0) !!')
                except (TypeError, KeyError):
                    return redirect('error-page', 'Guess you want to mess my website structure!!')
                
                data[name]['score'] += score
                data[name]['points'].append(score)
                data[name]['rounds'].append(f"{score}/{data[name]['color_list'][-1]}/{data[name]['vs_players'][-1]}")
                
            file_handler(action='w', user=request.user, obj=data)
            return redirect('standing')
    
        elif 'retrieve-button' in request.POST:
            white_players = []
            black_players = []
            
            for name in data:
                if data[name]['color_list'][-1] == 'W':
                    white_players.append(name)
                    black_players.append(data[name]['vs_players'][-1])
                    
            players_pair = {}
            for i in range(len(white_players)):
                players_pair[white_players[i]] = black_players[i]
            
            context['players_pair'] = players_pair
            context['is_pairing'] = True    
            
            return render(request, 'round-page.html', context)        

    elif request.method == 'GET': 
        # check if the user did not upload the points for the players, where the lists will not match each other in term of length
        for check_one_name in data:
            if len(data[check_one_name]['points']) != len(data[check_one_name]['vs_players']):
                context['is_incomplete'] = True
                return render(request, 'round-page.html', context)
            else:
                return render(request, 'round-page.html', context)
                

# knock-out system
@is_logged_in
def knockout_page(request):
    try:
        user = UserData.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return redirect('error-page', 'guess you want to mess my website structure!')
    
    context = {
        'data': user.knockout_data,
        'players': None,
        'is_pairing': False,
        'is_there_data': len(user.knockout_data)  
    }
    
    if request.method == 'POST':
        
        if 'upload-button' in request.POST:
            try:
                excel_file = request.FILES['excel_file']  # get the excel file
            except:
                return redirect('error-page', 'guess you want to mess my website structure!')

            df = pd.read_excel(excel_file)  # use pandas module for ease of use
        
            if 'Names' not in df.columns:  # check if Names column is in the excel data sheet
                return redirect('error-page', "The uploaded Excel file does not contain the (Names) header. Please upload a valid file.")
            
            df_length = len(df.Names)
            # checking the length of the Names column
            if df_length == 0 or df_length % 2 == 1 or df_length <= 4:
                return redirect('error-page', 'you need to insert a valid excel file!')
            # to ensure that the number of player is like that [8, 16, 32, 64, 128, 256, 512, 1024]
            while df_length > 1:
                df_length /= 2
            if df_length != 1:
                return redirect('error-page', 'the number of players must be (8, 16, 32, 64, 128, 256, 512)')
            
            data = {
                'white_players': [],
                'black_players': []
            }
            
            shuffle(df.Names)
            shuffle(df.Names)
            
            for i in range(len(df.Names)):
                name = df.Names[i].title()
                while True:
                    if name not in data['white_players'] or name not in data['black_players']:  # check duplicate names
                        if i % 2 == 0:
                            data['white_players'].append(name)
                        else:
                            data['black_players'].append(name)
                        break
                    else:
                        name = f'{name}_2'

            shuffle(data['white_players'])
            shuffle(data['black_players'])
            
            user.knockout_data = data
            user.save()
            
            return redirect('knock-out')  # to refresh the database
        
        elif 'pair-button' in request.POST:
            data = user.knockout_data
            
            if (len(data['white_players']) + len(data['black_players'])) == 2:
                return redirect('knock-out')
            
            players = {}
            
            for i in range(len(data['white_players'])):
                players[data['white_players'][i]] = data['black_players'][i]
            
            context['players'] = players
            context['is_pairing'] = True
           
        elif 'upload-score-button' in request.POST:
            
            white_players = []
            black_players = []
            
            for color, name_list in user.knockout_data.items():
                for player_name in name_list:
                    try:
                        score = int(request.POST.get(player_name))
                        
                        if score not in [1, 0]:
                            return redirect('error-page', 'insert valid score (1, 0) !!')
                        elif score == 1:
                            if color == 'white_players':
                                black_players.append(player_name)
                            else:
                                white_players.append(player_name)
                        
                    except (ValueError, KeyError, TypeError):
                        return redirect('error-page', 'guess you want to mess my website structure!')
            
            shuffle(white_players)
            shuffle(black_players)
            
            length = len(white_players) + len(black_players)
            
            if length % 2 == 1:
                return redirect('knock-out')
            
            naming_list_list = []  # it not list inside list ! leave as it is
            
            for _ in range(length):
                
                if len(white_players) != 0:
                    naming_list_list.append(white_players[0])
                    white_players.pop(0)  # removes the value of the first index
                    
                    if len(black_players) != 0:
                        naming_list_list.append(black_players[0])
                        black_players.pop(0)
                    else:
                        naming_list_list.append(white_players[0])
                        white_players.pop(0)
                
                elif len(black_players) != 0:
                    naming_list_list.append(black_players[0])
                    naming_list_list.append(black_players[1])
                    black_players.pop(0)
                    black_players.pop(0)
                
                else:
                    break
             
            for i in range(len(naming_list_list)):
                if i % 2 == 0:
                    white_players.append(naming_list_list[i])
                else:
                    black_players.append(naming_list_list[i])
            
            shuffle(white_players)
            shuffle(black_players)
            
            data = {
                'white_players': white_players,
                'black_players': black_players
            }
            
            user.knockout_data = data
            user.save()
            
            return redirect('knock-out')  # to refresh the database 
                    
    
    return render(request, 'knockout-page.html', context)
        
