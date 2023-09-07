import pycid
import numpy as np
from copy import deepcopy

import random

def learn_policy(macid : pycid.MACID, d):
	#learns a Q matrix for the given decision variable, ideally shouldn't modify the given game
	#actually maybe we should learn the whole policy for every decision. may lead to computational explosion
	#TODO discuss with Rhys

	inc_dim = ... # the size of all the possible tuples that could be inputed to the decision node
	dom_dim = ... # the size of the decision domain
	sample_ctx = ...
	Q = np.array[(inc_dim, dom_dim)]
	for i in range(10):
		ctx = sample_ctx()
		... # update Q by playing a macid game with ctx and recording the utility obtained 
	return ... # make some policy object with the Q matrix obtained


def test_learning_procedure(macid: pycid.MACID, d):
	Q = np.zeros((2,2)) # 2 possible values for X, and 2 possible decisions
	macid = deepcopy(macid) # TODO maybe change that, inefficient

	f = lambda X, PROP : "d" if X == "s" else "r"
	cf_S_policy = pycid.StochasticFunctionCPD("D1", f, macid)
	macid.add_cpds(cf_S_policy)
	#print(macid.get_cpds())
	#macid.draw()

	for _ in range(20):
		type_idx = 1 if random.random() < 0.9 else 0 # sample the wimp-surly S type
		type = "s" if type_idx==1 else "w"
		decision_idx = 1 if random.random() > 0.5 else 0 # random decision during training
		decision = "d" if decision_idx==1 else "r" 
		utility = macid.expected_utility(context={}, agent=1)
		Q[type_idx, decision_idx] = utility

	policy = lambda X, PROP : "d" if np.argmax(Q[1 if X=="s" else 0]) == 1 else "r"
	return pycid.StochasticFunctionCPD("D1", policy, macid)