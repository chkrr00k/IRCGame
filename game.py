import ircbot30_

class Game:
	def __init__(self, rows: int):
		self.rows = [["|" for j in range(1, i + 1)] for i in range(1, rows + 1)]
	
	def __str__(self):
		result = ""
		spaces = len(self.rows) - 1
		for row in self.rows:
			result += (" " * spaces) + " ".join(row) + "\n"
			spaces -= 1
		return result

	def change(self, row: int, fromWhere: int, toWhere: int):
		row -= 1
		fromWhere -= 1

		if row < 0 or row > len(self.rows) + 1:
			raise IOError("wrong row")
		currentRow = self.rows[row]
#		print(fromWhere < 0 , fromWhere > len(currentRow) , toWhere < 0 , toWhere > len(currentRow))
		if fromWhere < 0 or fromWhere > len(currentRow) or toWhere < 0 or toWhere > len(currentRow):
			raise IOError("Your interval is out of the scheme")
		
		if "+" in currentRow[fromWhere:toWhere]:
			raise IOError("You can't erase existing +")
		else:
			currentRow[fromWhere:toWhere] = ["+" for j in range(fromWhere, toWhere)]

	def isOver(self):
		for row in self.rows:
			if "|" in row:
				return False
		return True

	def print(self):
		result = list()
		spaces = len(self.rows) - 1
		for row in self.rows:
			result.append((" " * spaces) + " ".join(row))
			spaces -= 1
		return result

class Player:
	def __init__(self, name: str, game: Game, turn = False):
		self.game = game
		self.turn = turn
		self.name = name

	def getName(self):
		return self.name

	def play(self, row: int, fromWhere: int, toWhere: int):
		if self.turn:
			self.game.change(row, fromWhere, toWhere)
			self.turn = False
			print(self.game)

	def setTurn(self, turn = True):
		self.turn = turn

	def canPlay(self):
		return self.turn

	def hasWin(self):
		return self.game.isOver()

class Play:
	def __init__(self, *players: Player):
		self.players = {pl.getName() : pl for pl in players}
		self.order = [pl.getName() for pl in players]
		self.current = 0
		self.winner = None
	
	def addPlayer(self, player: Player):
		self.players[player.getName()] = player
		self.order.append(player.getName())
		self.current %= len(self.order)

	def removePlayer(self, player: Player):
		self.player.remove(player)
		self.order.remove(player.getName())
		self.current %= len(self.order)

	def isTurn(self, player: str):
		return self.order[self.current] == player

	def play(self, player: str, row: int, fromWhere: int, toWhere: int):
		if player in self.players:
			if self.order[self.current] == player and self.players[player].canPlay():
				self.players[player].play(row, fromWhere, toWhere)
				if self.players[player].hasWin():
					self.winner = player
				self.current += 1
				self.current %= len(self.order)
				self.players[self.order[self.current]].setTurn()
			else:
				raise IOError("It's not your turn")

	def checkForWin(self):
		return self.winner

	def getCurrentPlayer(self):
		return self.players[self.order[self.current]]




