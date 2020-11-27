# coding: utf-8
import copy
import math

class Game:
	player_1 = "x"
	player_2 = "o"
	
	def __init__(self):
		self.board = [["-","-","-"],["-","-","-"],["-","-","-"]]
		self.player_1 = "x"
		self.player_2 = "o"
		self.tie = "-"
		self.score = {self.player_1:-1,self.player_2:1,self.tie:0}
		self.finish = False

	def clear(self):
		self.board = [["-","-","-"],["-","-","-"],["-","-","-"]]
		self.finish = False

	def check_winner(self,temp):
		is_blank = False
		temp = [i for i in temp]

		for row in temp:
			if "-" in row:
				is_blank = True
			sums = sum([self.score[i] for i in row])
			if sums == 3:
				return self.player_2
			elif sums == -3:
				return self.player_1
	
		temp = [i for i in zip(*temp)]
		
		for row in temp:
			sums = sum([self.score[i] for i in row])
			if sums == 3:
				return self.player_2
			elif sums == -3:
				return self.player_1

		sums = self.score[temp[0][0]] + self.score[temp[1][1]] + self.score[temp[2][2]]
		if sums == 3:
			return self.player_2
		elif sums == -3:
			return self.player_1
		
		sums = self.score[temp[2][0]] + self.score[temp[1][1]] + self.score[temp[0][2]]
		if sums == 3:
			return self.player_2
		elif sums == -3:
			return self.player_1
		elif is_blank:
			return None
		else:
			return self.tie

	def play(self,x,y,value):
		if not self.finish and self.board[x][y] == "-":
			self.board[x][y] = value
			return True
		else:
			return False

	def is_finish(self):
		winner = self.check_winner(self.board)
		if winner != None:
			self.finish = True
			return winner
		else:
			return False

class GameAlpha:
	"""
	TicTacToe with minmax tree and alpha-beta pruning
	"""

	def __init__(self):
		self.board = [["-","-","-"],["-","-","-"],["-","-","-"]]
		self.player = "o"
		self.computer = "x"
		self.tie = "-"
		self.score = {self.player:-1,self.computer:1,self.tie:0}
		self.finish = False

	def clear(self):
		self.board = [["-","-","-"],["-","-","-"],["-","-","-"]]
		self.finish = False

	def check_winner(self,temp):
		is_blank = False
		temp = [i for i in temp]

		for row in temp:
			if "-" in row:
				is_blank = True
			sums = sum([self.score[i] for i in row])
			if sums == 3:
				return self.computer
			elif sums == -3:
				return self.player
	
		temp = [i for i in zip(*temp)]
		
		for row in temp:
			sums = sum([self.score[i] for i in row])
			if sums == 3:
				return self.computer
			elif sums == -3:
				return self.player

		sums = self.score[temp[0][0]] + self.score[temp[1][1]] + self.score[temp[2][2]]
		if sums == 3:
			return self.computer
		elif sums == -3:
			return self.player
		
		sums = self.score[temp[2][0]] + self.score[temp[1][1]] + self.score[temp[0][2]]
		if sums == 3:
			return self.computer
		elif sums == -3:
			return self.player
		elif is_blank:
			return None
		else:
			return self.tie

	def play(self,x,y,value):
		if not self.finish and self.board[x][y] == "-":
			self.board[x][y] = value
			return True
		else:
			return False

	def play_computer(self):
		temp = [i for i in self.board]
		min_score = -math.inf
		best_move = []

		for i in range(0,3):
			for k in range(0,3):
				if temp[i][k] == "-":
					temp[i][k] = self.computer
					score = self.minmax(temp,-math.inf,math.inf,False)
					if score >= min_score:
						min_score = score
						best_move = [i,k]
					temp[i][k] = "-"

		self.play(best_move[0],best_move[1],self.computer)
		return best_move

	def minmax(self,board,alpha,beta,ismax):
		temp = [i for i in board]
		winner = self.check_winner(temp)

		if winner != None:
			return self.score[winner]

		if ismax:
			best_score = -math.inf
			for i in range(0,3):
				for k in range(0,3):
					if temp[i][k] == "-":
						temp[i][k] = self.computer
						score = self.minmax(temp,alpha,beta,False)
						best_score = max(score,best_score)
						temp[i][k] = "-"

						if best_score >= beta:
							break

						if best_score > alpha:
							alpha = best_score

			return best_score
		else:
			best_score = math.inf
			for i in range(0,3):
				for k in range(0,3):
					if temp[i][k] == "-":
						temp[i][k] = self.player
						score = self.minmax(temp,alpha,beta,True)
						best_score = min(score,best_score)
						temp[i][k] = "-"

						if best_score <= alpha:
							break

						if best_score < beta:
							beta = best_score

			return best_score

	def is_finish(self):
		winner = self.check_winner(self.board)
		if winner != None:
			self.finish = True
			return winner
		else:
			return False