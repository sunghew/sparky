import requests
import json

with open('developer_tokens.json') as data:
    developer_tokens = json.load(data)

with open('suggested_users.json') as sugg:
    sugg_users = json.load(sugg)

"""
Internal Room Queries
"""
def get_users(token, room_id):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/memberships'
    headers = {
        'Authorization': legit_token
    }
    params = {
        'roomId': room_id
    }
    users_json = requests.get(url, headers=headers, params=params).json()
    users = []
    for user in users_json['items']:
        users.append((user['personDisplayName'], user['personEmail']))
    return users

def get_email_user(token, room_id):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/memberships'
    headers = {
        'Authorization': legit_token
    }
    params = {
        'roomId': room_id
    }
    users_json = requests.get(url, headers=headers, params=params).json()
    email_to_user = {}
    for user in users_json['items']:
        email_to_user[user['personEmail']] = user['personDisplayName']
    return email_to_user

def get_messages(token, room_id, before=None, before_msg=None, max_msgs=float('inf')):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/messages'
    headers = {
        'Accept': 'application/json',
        'Authorization': legit_token
    }
    params = {
        'roomId': room_id
    }
    if (max_msgs < float('inf') and max_msgs > 1):
        params['max'] = max_msgs
    if (before != None and before_msg != None):
        raise Exception('Can\'t have before and before_msg')
    elif (before != None):
        params['before'] = before
    elif (before_msg != None):
        params['beforeMessage'] = before_msg
    return requests.get(url, headers=headers, params=params).json()

def get_rooms(token, max_rooms=float('inf'), room_type=None):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {
        'Accept': 'application/json',
        'Authorization': legit_token
    }
    params = {}
    if room_type != None:
        params['type'] = room_type
    if (max_rooms < float('inf') and max_rooms > 1):
        params['max'] = max_rooms
    return requests.get(url, headers=headers, params=params).json()

def get_room(room_name, token, max_msgs=float('inf'), room_type=None):
    for room in get_rooms(token, max_msgs, room_type)['items']:
        if room['title'].lower() == room_name.lower():
            return room
    return None

def get_roomid(room_name, token, max_msgs=float('inf'), room_type=None):
    room = get_room(room_name, token, max_msgs=float('inf'), room_type=None)
    if not room or 'id' not in room:
        return None
    return room['id']

"""
Internal Room Action Commands
"""
def check_suggested_members(member_name):
    if member_name in sugg_users:
        if (len(sugg_users[member_name])>1):
            print "Did you mean one of these? "
            count =1
            for suggested_member in sugg_users[member_name]:
                print count + ": "+ suggested_member[0]
                print "   " + suggested_member[1]
            num = raw_input("Respond with a number: ")
            return sugg_users[member_name][num-1][1]
        else:
            return sugg_users[member_name][0][1]
    else:
        return 0

# not finished
def find_members(token, member_input):
    final_member_list = []
    legit_token = "Bearer " + token
    search_url = "https://api.ciscospark.com/v1/people"
    for member in member_input:
        headers = {
            'Authorization': legit_token
        }
        params = {
            'displayName': member
        }
        matching_members = requests.get(search_url, headers=headers, params=params).json()
        if len(matching_members['items']) == 0:
            print "No matching members"
        elif len(matching_members['items']) == 1:
            final_member_list.append(matching_members['items'][0]['email'])
        elif len(matching_members['items']) > 5:
            found_member = check_suggested_members((member.split())[0])
            if found_member == 0:
                print "Please specify " + member + " a bit more"
            else:
                final_member_list.append(found_member)
        else:
            print "Did you mean one of these? "
            for matched_member in matching_members['items']:
                print count + ": "+ matched_member
            num = raw_input("Respond with a number: ")
    return final_member_list

def find_lastname(token, member):
    lastnames = []
    headers = {
        'Authorization': legit_token
    }
    params = {
        'displayName': member
    }
    matching_members = requests.get(search_url, headers=headers, params=params).json()
    if len(matching_members['items']) == 0:
        print "No matching members"
        return None
    for m in matching_members['items']:
        lastnames.append(m['items'][0]['personDisplayName'])
    if not lastnames:
        return None
    return lastnames

def create_room(token, room_name):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {
        'Authorization': legit_token
    }
    params = {
        'title': room_name
    }
    users_json = requests.post(url, headers=headers, data=params).json()
    room_id = users_json['id']
    return room_id

def delete_room(token, room_id):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/rooms/'+room_id
    headers = {
        'Authorization': legit_token
    }
    params = {
        'roomId': room_id
    }
    delete_output_code = requests.delete(url, headers=headers, params=params)
    return delete_output_code

def add_members_to_room(token, room_id, member_input):
    legit_token = "Bearer " + token
    join_url = "https://api.ciscospark.com/v1/memberships"
    headers = {
        'Authorization': legit_token
    }
    for member_email in member_input:
        add_params = {
            'roomId': room_id,
            'personEmail':member_email
        }
        membership_create_response = requests.post(join_url, headers=headers, data=add_params).json()

def change_room_name(token, old_name, new_name):
    legit_token = "Bearer " + token
    rooms = get_rooms(token)['items']
    for r in rooms:
        if r['title'].lower() == old_name.lower():
            update_url = 'https://api.ciscospark.com/v1/rooms/%s' % r['id']
            headers = {
                'Accept': 'application/json',
                'Authorization': legit_token
            }
            params = {
                'title': new_name
            }
            return requests.put(update_url, headers=headers, data=params).json()
    print 'Room \'%s\' could not be found' % old_name
    print 'No room updated'
    return None

"""
Use these functions
"""
# returns messages from a room
# The Spark API is buggy--if you don't specify a limit, it's by default 50
def get_messages_for_user(user, room_name, limit):
    if user not in developer_tokens:
        raise Exception("User {} doesn't exist".format(user))
    return get_messages(developer_tokens[user], get_roomid(room_name, developer_tokens[user]), None, None, limit)

# returns users, email tuple in a room
def get_users_for_room(user, room_name):
    if user not in developer_tokens:
        raise Exception("User {} doesn't exist".format(user))
    return get_users(developer_tokens[user], get_roomid(room_name, developer_tokens[user]))

# returns a dictionary with email-username pairs
def get_emails_with_users(user, room_name):
    if user not in developer_tokens:
        raise Exception("User {} doesn't exist".format(user))
    return get_email_user(developer_tokens[user], get_roomid(room_name, developer_tokens[user]))

def get_all_rooms(user, max_rooms=float('inf'), room_type=None):
    rooms = []
    for r in get_rooms(developer_tokens[user], max_rooms, room_type)['items']:
        rooms.append(r['title'].lower())
    return rooms

# creates room and returns id of newly created room
def make_room(user, room_name):
    return create_room(developer_tokens[user], room_name)

# removes room and returns output code for delete
def remove_room(user, room_name):
    return delete_room(developer_tokens[user], get_roomid(room_name, developer_tokens[user]))

# adds room_members to room
def add_members(user, room_name, room_members):
    add_members_to_room(developer_tokens[user], get_roomid(room_name, developer_tokens[user]), room_members)

def add_members_with_room_id(user, room_id, room_members):
    add_members_to_room(developer_tokens[user], room_id, room_members)

# changes an existing room's name and returns the output code (returns None if rooms doesn't exist)
def rename_room(user, room_name, new_room_name):
    return change_room_name(developer_tokens[user], room_name, new_room_name)

def search_members(user, member_input):
    return find_members(developer_tokens[user], member_input)

"""
Test Calls
"""
# users = get_users(developer_tokens['tanay'], 'Y2lzY29zcGFyazovL3VzL1JPT00vYjhhMmFhYjAtMmU5Mi0xMWU2LTg0YWEtNWY1MGViMDZhMjAx')
# print get_messages(developer_tokens['tanay'], 'Y2lzY29zcGFyazovL3VzL1JPT00vYjhhMmFhYjAtMmU5Mi0xMWU2LTg0YWEtNWY1MGViMDZhMjAx')
# print get_roomid('Hacker Squad', developer_tokens['chris'])
# print get_messages_for_user('chris', 'Hacker Squad')

# room_members = ["Christopher Chon", "Anjum Shaik", "Tanay Nathan"]
# rname = "test_room"
# print make_room('charu', rname)
# add_members('charu', rname, room_members)
# print remove_room('charu', rname)

# print update_room_name('chris', 'Hacker Squad', 'Chris Fan Club')
# print update_room_name('chris', 'Chris Fan Club', 'Sparky')



'''import requests
import json

with open('developer_tokens.json') as data:
    developer_tokens = json.load(data)

with open('suggested_users.json') as sugg:
    sugg_users = json.load(sugg)

"""
Internal Room Queries
"""
def get_users(token, room_id):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/memberships'
    headers = {
        'Authorization': legit_token
    }
    params = {
        'roomId': room_id
    }
    users_json = requests.get(url, headers=headers, params=params).json()
    users = []
    for user in users_json['items']:
        users.append((user['personDisplayName'], user['personEmail']))
    return users

def get_email_user(token, room_id):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/memberships'
    headers = {
        'Authorization': legit_token
    }
    params = {
        'roomId': room_id
    }
    users_json = requests.get(url, headers=headers, params=params).json()
    email_to_user = {}
    for user in users_json['items']:
        email_to_user[user['personEmail']] = user['personDisplayName']
    return email_to_user

def get_messages(token, room_id, before=None, before_msg=None, max_msgs=float('inf')):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/messages'
    headers = {
        'Accept': 'application/json',
        'Authorization': legit_token
    }
    params = {
        'roomId': room_id
    }
    if (max_msgs < float('inf') and max_msgs > 1):
        params['max'] = max_msgs
    if (before != None and before_msg != None):
        raise Exception('Can\'t have before and before_msg')
    elif (before != None):
        params['before'] = before
    elif (before_msg != None):
        params['beforeMessage'] = before_msg
    return requests.get(url, headers=headers, params=params).json()

def get_rooms(token, max_rooms=float('inf'), room_type=None):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {
        'Accept': 'application/json',
        'Authorization': legit_token
    }
    params = {}
    if room_type != None:
        params['type'] = room_type
    if (max_rooms < float('inf') and max_rooms > 1):
        params['max'] = max_rooms
    return requests.get(url, headers=headers, params=params).json()

def get_room(room_name, token, max_msgs=float('inf'), room_type=None):
    for room in get_rooms(token, max_msgs, room_type)['items']:
        if room['title'].lower() == room_name.lower():
            return room
    return None

def get_roomid(room_name, token, max_msgs=float('inf'), room_type=None):
    room = get_room(room_name, token, max_msgs=float('inf'), room_type=None)
    if not room or 'id' not in room:
        return None
    return room['id']

"""
Internal Room Action Commands
"""
def check_suggested_members(member_name):
    if member_name in sugg_users:
        if (len(sugg_users[member_name])>1):
            print "Did you mean one of these? "
            count =1
            for suggested_member in sugg_users[member_name]:
                print count + ": "+ suggested_member[0]
                print "   " + suggested_member[1]
            num = raw_input("Respond with a number: ")
            return sugg_users[member_name][num-1][1]
        else:
            return sugg_users[member_name][0][1]
    else:
        return 0

# not finished
def find_members(token, member_input):
    final_member_list = []
    legit_token = "Bearer " + token
    search_url = "https://api.ciscospark.com/v1/people"
    for member in member_input:
        headers = {
            'Authorization': legit_token
        }
        params = {
            'displayName': member
        }
        matching_members = requests.get(search_url, headers=headers, params=params).json()
        if len(matching_members['items']) == 0:
            print "No matching members"
        elif len(matching_members['items']) == 1:
            final_member_list.append(matching_members['items'][0]['email'])
        elif len(matching_members['items']) > 5:
            found_member = check_suggested_members((member.split())[0])
            if found_member == 0:
                print "Please specify " + member + " a bit more"
            else:
                final_member_list.append(found_member)
        else:
            print "Did you mean one of these? "
            for matched_member in matching_members['items']:
                print count + ": "+ matched_member
            num = raw_input("Respond with a number: ")
    return final_member_list

def find_lastname(token, member):
    lastnames = []
    headers = {
        'Authorization': legit_token
    }
    params = {
        'displayName': member
    }
    matching_members = requests.get(search_url, headers=headers, params=params).json()
    if len(matching_members['items']) == 0:
        print "No matching members"
        return None
    for m in matching_members['items']:
        lastnames.append(m['items'][0]['personDisplayName'])
    if not lastnames:
        return None
    return lastnames

def create_room(token, room_name):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {
        'Authorization': legit_token
    }
    params = {
        'title': room_name
    }
    users_json = requests.post(url, headers=headers, data=params).json()
    room_id = users_json['id']
    return room_id

def delete_room(token, room_id):
    legit_token = "Bearer " + token
    url = 'https://api.ciscospark.com/v1/rooms/'+room_id
    headers = {
        'Authorization': legit_token
    }
    params = {
        'roomId': room_id
    }
    delete_output_code = requests.delete(url, headers=headers, params=params)
    return delete_output_code

def add_members_to_room(token, room_id, member_input):
    legit_token = "Bearer " + token
    join_url = "https://api.ciscospark.com/v1/memberships"
    headers = {
        'Authorization': legit_token
    }
    for member_email in member_input:
        add_params = {
            'roomId': room_id,
            'personEmail':member_email
        }
        membership_create_response = requests.post(join_url, headers=headers, data=add_params).json()

def change_room_name(token, old_name, new_name):
    legit_token = "Bearer " + token
    rooms = get_rooms(token)['items']
    for r in rooms:
        if r['title'].lower() == old_name.lower():
            update_url = 'https://api.ciscospark.com/v1/rooms/%s' % r['id']
            headers = {
                'Accept': 'application/json',
                'Authorization': legit_token
            }
            params = {
                'title': new_name
            }
            return requests.put(update_url, headers=headers, data=params).json()
    print 'Room \'%s\' could not be found' % old_name
    print 'No room updated'
    return None

"""
Use these functions
"""
# returns messages from a room
def get_messages_for_user(user, room_name, limit):
    if user not in developer_tokens:
        raise Exception("User {} doesn't exist".format(user))
    return get_messages(developer_tokens[user], get_roomid(room_name, developer_tokens[user]), None, None, limit)

# returns users, email tuple in a room
def get_users_for_room(user, room_name):
    if user not in developer_tokens:
        raise Exception("User {} doesn't exist".format(user))
    return get_users(developer_tokens[user], get_roomid(room_name, developer_tokens[user]))

# returns a dictionary with email-username pairs
def get_emails_with_users(user, room_name):
    if user not in developer_tokens:
        raise Exception("User {} doesn't exist".format(user))
    return get_email_user(developer_tokens[user], get_roomid(room_name, developer_tokens[user]))

def get_all_rooms(user, max_rooms=float('inf'), room_type=None):
    rooms = []
    for r in get_rooms(developer_tokens[user], max_rooms, room_type)['items']:
        rooms.append(r['title'].lower())
    return rooms

# creates room and returns id of newly created room
def make_room(user, room_name):
    return create_room(developer_tokens[user], room_name)

# removes room and returns output code for delete
def remove_room(user, room_name):
    return delete_room(developer_tokens[user], get_roomid(room_name, developer_tokens[user]))

# adds room_members to room
def add_members(user, room_name, room_members):
    add_members_to_room(developer_tokens[user], get_roomid(room_name, developer_tokens[user]), room_members)

def add_members_with_room_id(user, room_id, room_members):
    add_members_to_room(developer_tokens[user], room_id, room_members)

# changes an existing room's name and returns the output code (returns None if rooms doesn't exist)
def rename_room(user, room_name, new_room_name):
    return change_room_name(developer_tokens[user], room_name, new_room_name)

def search_members(user, member_input):
    return find_members(developer_tokens[user], member_input)

##########################################

# users = get_users(developer_tokens['tanay'], 'Y2lzY29zcGFyazovL3VzL1JPT00vYjhhMmFhYjAtMmU5Mi0xMWU2LTg0YWEtNWY1MGViMDZhMjAx')
# print get_messages(developer_tokens['tanay'], 'Y2lzY29zcGFyazovL3VzL1JPT00vYjhhMmFhYjAtMmU5Mi0xMWU2LTg0YWEtNWY1MGViMDZhMjAx')
# print get_roomid('Hacker Squad', developer_tokens['chris'])
# print get_messages_for_user('chris', 'Hacker Squad')

# room_members = ["Christopher Chon", "Anjum Shaik", "Tanay Nathan"]
# rname = "test_room"
# print make_room('charu', rname)
# add_members('charu', rname, room_members)
# print remove_room('charu', rname)

# print update_room_name('chris', 'Hacker Squad', 'Chris Fan Club')
# print update_room_name('chris', 'Chris Fan Club', 'Sparky')
'''