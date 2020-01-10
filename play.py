import pickle
import random
import requests
import re
from datetime import datetime
from cpu import CPU
from hashlib import sha256

URL = 'https://lambda-treasure-hunt.herokuapp.com/api/'
# ex:  #curl -X POST -H 'Authorization: Token 7a375b52bdc410eebbc878ed3e58b2e94a8cb607' -H "Content-Type: application/json" -d '{"direction":"n"}' https://lambda-treasure-hunt.herokuapp.com/api/adv/move/
TOKEN = '619a8e22a6a39aff3a792debc98d89b4f135abb0'
AUTH = {"Authorization": f"Token {TOKEN}"}
JSON = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}
#commands
INIT = 'adv/init/'	#GET
					
header = {"Content-Type": "application/json"}
response = requests.get(URL + INIT, headers = AUTH)
print(response)
response = response.json()
starting_exits = response['exits']
print(response)



with open('map.pickle', 'rb') as map:
    full_map = pickle.load(map)



class Player:
	"""Creates a new player and allows him to move around"""
	def __init__(self):
		self.map = {}
		
		self.current_room = 1  # might need to change. Room 1 is the shop
		self.current_exits = starting_exits
		self.coordinates = None
		#self.cooldown = 0
		self.now = datetime.now()
		self.encumbrance = 0
		self.encumbered = False
		self.balance = 0
		self.gold = 0
		# need some decisions on this:
		self.name_changed = False
		#self.items = deque()
		# shop to well path : 'e,e, n, e, e'
		self.vital_rooms = {
						'shop': {'room_id': 1, 'coordinates': '59, 60'},  
						'mine': {'room_id': 272, 'coordinates': '53, 58'},
                        'name': {'room_id': 467, 'coordinates': '68, 47'},  # pirate's room to change name
                        'well': {'room_id': 55, 'coordinates': '63, 61'},   # final stop to get the hint

		}				# ['name to Excalibur.', "'Ere's a tip from Pirate Ry: If you find a shrine, try prayin'. Ye' never know who may be listenin'."

	def cooldown(self, cooldown_time: int):
		start_time = datetime.now()
		while (datetime.now() - start_time).seconds < cooldown_time:	# wait for the cooldown period to pass
			pass

	def pick_up(self):
		response = requests.post(URL + 'adv/take/', headers = JSON, json = {"name":"treasure"})
		print(response)
		print(response.json())
		self.cooldown(response.json()['cooldown'])
#'{"name":"[NAME OF ITEM OR PLAYER]"}' https://lambda-treasure-hunt.herokuapp.com/api/adv/examine/
	def examine(self):
		response = requests.post(URL + 'adv/examine/', headers = JSON, json = {"name":"well"})
		print(response, response.json())
		self.cooldown(response.json()['cooldown'])
#curl -X GET -H 'Authorization: Token 7a375b52bdc410eebbc878ed3e58b2e94a8cb607' https://lambda-treasure-hunt.herokuapp.com/api/bc/last_proof/
	def last_proof(self):
		response = requests.get(URL + 'bc/last_proof/', headers = AUTH)
		print(response, response.json())
		self.cooldown(response.json()['cooldown'])
		return response.json()

	def submit_proof(self):
		res = self.last_proof()
		last_proof = res['proof']
		difficulty = res['difficulty']
		print( last_proof, difficulty)

		x = 0
		print(f'Finding proof...\nlast_proof: {last_proof}, difficulty: {difficulty}')
		while True:
			string = (str(last_proof) + str(x)).encode()
			hash_ = sha256(string).hexdigest()
			if hash_[:difficulty] == '0' * difficulty:
				print('Submitting proof: ', x, hash_[:difficulty], type(hash_))
				break
			x += 1


		response = requests.post(URL + 'bc/mine/', headers = AUTH, json = {"proof": x})
		print(response, response.json())
		self.cooldown(response.json()['cooldown'])

	def inventory(self):
		response = requests.post(URL + 'adv/status/', headers = JSON, json = {"name":"treasure"})
		print(response, response.json())
		self.cooldown(response.json()['cooldown'])

	def sell(self):
		# response = requests.post(URL + 'adv/sell/', headers = JSON, json = {"name":"treasure"})
		# print(response, response.json())
		# #'{"name":"treasure", "confirm":"yes"}' https://lambda-treasure-hunt.herokuapp.com/api/adv/sell/
		response = requests.post(URL + 'adv/sell/', headers = JSON, json = {"name":"treasure", "confirm":"yes"})
		print(response, response.json())
		self.cooldown(response.json()['cooldown'])

	def change_name(self):
		# response = requests.post(URL + 'adv/sell/', headers = JSON, json = {"name":"treasure"})
		# print(response, response.json())
		# #'{"name":"treasure", "confirm":"yes"}' https://lambda-treasure-hunt.herokuapp.com/api/adv/sell/
		response = requests.post(URL + 'adv/change_name/', headers = JSON, json = {"name":"Excalibur", 'confirm':'aye'} )
		print(response, response.json())
		self.cooldown(response.json()['cooldown'])

	def move(self, dir: str) -> dict:
		# 'Authorization: Token 7a375b52bdc410eebbc878ed3e58b2e94a8cb607' -H "Content-Type: application/json" -d '{"direction":"n"}' https://lambda-treasure-hunt.herokuapp.com/api/adv/move/
		convert_dir = {'n': 'to_n', 'w': 'to_w', 'e': 'to_e', 's': 'to_s'}
		print(convert_dir[dir])
		print(full_map[self.current_room][convert_dir[dir]])
		next_room = full_map[self.current_room][convert_dir[dir]]
		new_room = requests.post(URL + 'adv/move/', headers = JSON, json = {"direction": f'{dir}', "next_room_id": str(next_room)})
		print(new_room)
		print(new_room.json())
		self.current_room = new_room.json()['room_id']
		self.coordinates = new_room.json()['coordinates']
		self.current_exits = new_room.json()['exits']
		print(int(new_room.json()['cooldown']))
		#print(self.cooldown())
		self.cooldown(new_room.json()['cooldown'])


		if new_room.json()['items']:
			if 'tiny treasure' in new_room.json()['items'] or 'great treasure' in new_room.json()['items']:
				print('found gold', new_room.json()['items'])
				# start_time = datetime.now()
				# print(new_room.json()['cooldown'], datetime.now() - start_time )
				# while (datetime.now() - start_time).seconds < new_room.json()['cooldown']:	# wait for the cooldown period to pass
				# 	pass
				if self.encumbrance < 10:
					self.pick_up()
					self.encumbrance += 2



	

player = Player()


# use this to get back to shop
path_from_shop = [] 
reverse_direction = {'n': 's', 's': 'n', 'w': 'e', 'e': 'w'}

# with open('clue.ls8', 'w') as f:
#             for line in code[2:]:
#                 f.write(line)
#                 f.write('\n')
cpu = CPU()
cpu.load()
cpu.run()
mine_room = cpu.next_room
print('mining room is ', mine_room)

# self.places['mine']['room_id'] = next_room

while True:
	
	current_direction = None
	key = 'x'
	while key not in ['n', 's', 'e', 'w', 'ex', 'exam', 'submit', 'lastproof','q', 'i', 'sell', 'shop', 'name']:
		key = input('Please enter an instruction: ex for explore, exam for examining, m for manual, i for inventory, name to change name or q to quit:  ')
	
	if key is 'q':
		break
	elif key == 'sell':
		print('did you say sell??')
		player.sell()
	elif key == 'name':
		print('Changing name')
		player.change_name()
	elif key == 'exam':
		print('Examining')
		player.examine()
	elif key == 'lastproof':
		print('Requesting last proof')
		player.last_proof()
	elif key == 'submit':
		print('Submitting new proof')
		player.submit_proof()
	elif key is 'i':
		#player.cooldown()
		player.inventory()
	elif key is 'shop':
		print('You want to go to the shop? I do not know how to do that yet')
	elif key in ['n','s','w','e']:
		path_from_shop.append(current_direction)
		player.move(key)
		path_from_shop.append(key)
		print('path from shop so far', path_from_shop)
	else:
		while player.encumbrance < 6:
			current_direction = random.choice(player.current_exits)
			path_from_shop.append(current_direction)

			player.move('s')
			print('path from shop so far', path_from_shop)

