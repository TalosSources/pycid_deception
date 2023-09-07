import pycid

import numpy as np
from copy import copy, deepcopy
import inspect


def build_cf_game(macid: pycid.MACID, agent, prop) -> pycid.MACID :
	"""	
		BUILD COUNTERFACTUAL GAME HERE : 
		WE (AFTER DEEP-COPYING THE GAME) INTRODUCE A NEW NODE PROP.
		IT IS CONDITIONALLY DEPENDENT (HAS EDGE FROM) EVERY VARIABLE MENTIONED IN THE PROPOSITION
		THE CPDS ARE DEFINED BY THE PROPOSITION -> I NEED A PROPOSITION REPRESENTATION WHERE THE INCOMING VARIABLES ARE EXPLICITELY ACCESSIBLE. 
		MAYBE THE LAMBDAS ARE READABLE THAT WAY -> YES :)
		IT IS ALSO VISIBLE (HAS EDGE TO) EVERY DECISION NODE (OR MAYBE ONLY SOME, THE ONE THAT HAPPEN AFTER THE PROPOSITION'S TRUTH VALUE IS DETERMINED)	
	"""
	cf_macid = deepcopy(macid)

	l_params = inspect.signature(prop).parameters

	# for every node that prop depends on, we add an edge from it to the proposition
	cf_macid.update([(name, "PROP") for name, _ in l_params.items()])

	cf_macid.add_cpds(PROP=prop) # we use the given lambda as a CPD for the proposition node

	#now we make the proposition visible to every decision node? (clarify with rhys, maybe only one or some given subset) for the counterfactual property
	cf_macid.update([("PROP", name) for name in macid.agent_decisions[agent]])
	
	return cf_macid


def belief(macid : pycid.MACID, agent, policy, prop, cf_policy=None, learning_procedure=None, ctx={}) -> bool: # TODO offer possibility to use given cf_policy
	# I need a representation for what a proposition is in this context
	# it seems pycid supports some form of intervention. investigate this for countrafactuals

	#decisions arrays
	#policy_sf = pycid.StochasticFunctionCPD("D1", policy, macid)

	# TODO : check that the prop inputs aren't already contained in the decision inputs
	
	macid.add_cpds(policy)
	D = macid.query(macid.agent_decisions[agent], context=ctx)

	cf_macid = build_cf_game(macid, agent, prop)

	cf_policy = learning_procedure(cf_macid, agent) if cf_policy is None else cf_policy
	cf_policy = pycid.StochasticFunctionCPD(variable=f"D{agent}", stochastic_function=cf_policy, cbn=macid) # TODO very ugly find nice and general and consistent solution
	# TODO : this above ^ breaks everything, I need to find another way to do it (or figure out why it breaks evrtg)

	cf_macid.add_cpds(cf_policy)


	#cf_macid.add_cpds(D2=["a","n"])
	print(f"model={macid.get_cpds('D2')}")
	print(f"before : {cf_macid.get_cpds('D2')}")
	#cf_macid.add_cpds(macid.get_cpds("D2"))
	cf_macid.add_cpds(D2= lambda D1: 'a' if D1=="r" else 'n') # TODO : problem here, the cardinality seem to cause problem, see with James 
	print(f"after : {cf_macid.get_cpds('D2')}")

	#for node in cf_macid.nodes():
	#		cpd = cf_macid.get_cpds(node=node)
	#		print(f"cpd={cpd}")
	#		print(f"all cards = {cpd.cardinality}")
	#		for index, node in enumerate(cpd.variables[1:]):
	#			parent_cpd = cf_macid.get_cpds(node)
	#			print(f"parent={parent_cpd}")
	#			print(f"parent card = {parent_cpd.cardinality[0]}")
	#			print(f"card = {cpd.cardinality[1 + index]}")
		

	cf_macid.draw()
	ctx_true = copy(ctx)
	ctx_true["PROP"] = True # I guess here we assume cfpolicy has an additional input for all decisions node as a boolean prop node
	cf_D_true = cf_macid.query(macid.agent_decisions[agent], context=ctx_true)

	ctx_false = copy(ctx)
	ctx_false["PROP"] = False
	cf_D_false = cf_macid.query(macid.agent_decisions[agent], context=ctx_false)

	acts_as_true = D == cf_D_true

	responds = cf_D_true != cf_D_false

	return acts_as_true and responds
