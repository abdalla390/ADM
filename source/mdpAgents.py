# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print("Starting up MDPAgent!")
        name = "Pacman"
        self.actions = ['North', 'West', 'South', 'East']
        self.states = [] # The call to populate in getAction(...)

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print("Running registerInitialState for MDPAgent!")
        self.states = MDPAgent.possible_states(state)

        print("I'm at:")
        print(api.whereAmI(state))
        
    # This is what gets run in between multiple games
    def final(self, state):
        print("Looks like the game just ended!")\
        
    @staticmethod
    def possible_states(state):
        corners = api.corners(state)
        walls = set(api.walls(state))
        
        height = corners[3][1]
        width = corners[3][0]
        
        possible = []

        for i in range(1, width):
            for j in range(1, height):
                if (i, j) not in  walls:
                    possible.append((i,j))

        return possible 

    def transition_fn(self, query_state, pacman_pos, action) -> float:
        p = api.directionProb
        side = (1 - p) / 2
        dx, dy = MDPAgent._action_conversion_value(action)

        direction = [((dx, dy), p), ((dy, dx), side), ((-dy, -dx), side)]

        prob = 0.0
        for (mx, my), pr in direction:
            target = (pacman_pos[0] + mx, pacman_pos[1] + my)

            if target not in self.states:
                target = pacman_pos
            if target == query_state:
                prob += pr
        return prob
    
    @staticmethod
    def _action_conversion_value(action) -> tuple:
        if action == 'East':
            return (1,0)
        elif action == 'West':
            return (-1, 0)
        elif action == 'South':
            return (0, -1)
        elif action == 'North':
            return (0, 1)
        else:
            raise ValueError('Action not present in MDP action set')

    @staticmethod
    def _neighbour_check(curr, next) -> bool:
         return abs(curr[0] - next[0]) + abs(curr[1] - next[1]) == 1


    def move_In_squares(self, state) -> str:
        position = api.whereAmI(state)

        if random.random() < 0.0001:
            print(f'I am in {position}, probability to get to state is: ' + str(self.transition_fn((5,4), position, 'North')))

        if position[0] > 6 and position[0] <= 13 and position[1] == 1:
            return 'West'
        elif position[1] >= 1 and position[1] < 9 and position[0] == 6:
            return 'North'
        elif position[1] == 9 and position[0] >= 6 and position[0] < 13:
            return 'East'
        elif position[0] == 13 and position[1] <= 9 and position[1] > 1:
            return 'South'

        return 'Stop'

    @staticmethod
    def _dist_reward(square, ghost) -> float:
        dist = abs(square[0] - ghost[0]) + abs(square[1] - ghost[1])
        if dist == 0:
            return -10 ** 4
        return -10 / (dist)

    def reward_fn(self, square, food, ghosts, capsule) -> float:
        reward = 0
        
        if square in food:
            reward += 5
        if square in capsule:
            reward += 10

        for pellet in food:
            reward -= 0.5 * MDPAgent._dist_reward(square, pellet) 

        for ghost in ghosts:
            if ghost[1] == 0:
                reward += MDPAgent._dist_reward(square, ghost[0])
            else:
                reward -= MDPAgent._dist_reward(square, ghost[0])
        return reward

    def value_iteration(self, rewards, gamma, iterations) -> dict:
        V = {state: 0.0 for state in self.states}
        for _ in range(iterations):
            new_V = {}
            for state in self.states:
                best = max(
                    sum(self.transition_fn(sprime, state, a) * V[sprime] for sprime in self.states)
                    for a in self.actions
                )
                new_V[state] = rewards[state] + gamma * best
            V = new_V
        return V

    def best_action(self, pacman_pos, V):
        near = self._near_states(pacman_pos)
        return max(self.actions,
               key=lambda a: sum(self.transition_fn(s2, pacman_pos, a) * V[s2]
                                 for s2 in near))


    def _near_states(self, pacman_pos):
        near = []
        for state in self.states:
            if self._neighbour_check(state, pacman_pos):
                near.append(state)
        return near
    
    def getAction(self, state): # type: ignore
        # Runs every move: rebuild rewards from the current world, re-solve, act
        food = set(api.food(state))
        capsules = set(api.capsules(state))
        ghosts = api.ghostStates(state)
        rewards = {s: self.reward_fn(s, food, ghosts, capsules) for s in self.states}

        V = self.value_iteration(rewards, gamma=0.9, iterations=30)
        action = self.best_action(api.whereAmI(state), V)

        legal = api.legalActions(state)
        return api.makeMove(action, legal)


