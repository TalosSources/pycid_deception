import pycid

import numpy as np
from copy import copy, deepcopy
import inspect

import belief
import learning
import games

import intention
from deception import evaluate_prop, deceives


#==========================STUFF==========================


#=========================================================




ws = games.wimp_surly_macid()

f = lambda X : "d" if X == "s" else "r"

honest_S_policy = pycid.StochasticFunctionCPD("D1", f, ws)
#honest_S_policy = 

f_d = lambda X : "d"
deceptive_S_policy = pycid.StochasticFunctionCPD("D1", f_d, ws)
#deceptive_S_policy = f_d

g = lambda D1 : "a" if D1 == "r" else "n"
honest_T_policy = pycid.StochasticFunctionCPD("D2", g, ws)
#honest_T_policy = g

cf_g = lambda D1, PROP : "a" if PROP==True else "r"
cf_T_policy = cf_g

#ws.add_cpds(D1=deceptive_S_policy, D2=honest_T_policy)
ws.add_cpds(D1=lambda X : "d", D2=lambda D1 : "a" if D1 == "r" else "n")
#print(f"cpd D1 : {ws.get_cpds('D1')}")

type_prop = lambda X : X=="w"
#ws.draw()

#let prop = (X == "s")
#cf_ws = deepcopy(ws)
#cf_ws.update([("prop", "D2"), ("X", "prop")]) # now T knows about the proposition when making their decision
#cf_ws.add_cpds(propJSON's and =lambda X : X=="s")
#cf_ws.draw()

#cf_g = lambda D1, prop : "n" if prop == True else "a" #using the knowledge
#cf_honest_T_policy = pycid.StochasticFunctionCPD("D2", cf_g, cf_ws)



def belief_test():
    #==========================BELIEF=TEST==========================#
    type_prop = lambda X : X == "s"
    #T_belief_over_type = belief.belief(ws, 1, honest_T_policy, type_prop, {"X" : "w"})
    S_belief_over_type = belief.belief(ws, 1, honest_T_policy, type_prop, learning_procedure=learning.test_learning_procedure, ctx={"X" : "w"})
    #print(f"T does {'' if T_belief_over_type else 'not'} believe that X == strong")
    print(f"S does {'' if S_belief_over_type else 'not'} believe that X == strong")

def intention_test():
    result = intention.intends_to_cause(ws, 1, deceptive_S_policy, honest_S_policy, "D2", {"X" : "w"})
    print(f"intends to cause when type=weak : {result} (should be true here)")
    result = intention.intends_to_cause(ws, 1, deceptive_S_policy, honest_S_policy, "D2", {"X" : "s"})
    print(f"intends to cause when type=strong : {result}")

    """
    What should happen here ?
    When X is weak : causing T to retreat is sufficient reason to signal strongness. 
        If T was to retreat anyway, S would've been fine signalling weakness (even preferred it)
    When X is strong : The deceptive and honest policy are identical, so S doesn't mind switching, idk.
    But what's sure is that there should be intention when S is weak. If not, there can't be deception.
    """

def deception_test():
    result = deceives(ws, 1, 2, deceptive_S_policy, honest_S_policy, {"X" : "w"}, 
                      type_prop, "D2", dr_cf_policy=deceptive_S_policy, de_cf_policy=cf_T_policy)
    print(f"Deceives ? {deceives}")


def evaluation_test():
    result_w = evaluate_prop(ws, type_prop, ctx={"X": "w"})
    result_s = evaluate_prop(ws, type_prop, ctx={"X": "s"})
    print(f"w (should be true) : {result_w}")
    print(f"s (should be false) : {result_s}")


def intervention_test():

    #ws.update([("X", "D2")])
    test_lambda = lambda D1 : "n" if D1=="d" else "a"
    function = pycid.StochasticFunctionCPD("D2", test_lambda, ws)
    ws.intervene({"D2" : function})
    #ws.intervene({"D2" : lambda D1, X : g(f(X))})

    print(ws.query(["D1", "D2"], context={}))


def potential_setting_space_unit_test():
    import intention
    setting_space = intention.compute_setting_space(games.test_ws_variant())
    print(setting_space)
    print(f"There should be 16 settings, and there is : {len(setting_space)}")

    total_probability = 0
    for s,p in setting_space:
        total_probability += p
    print(f"total_prob = {total_probability}")

def nan_test():
    print(f"macid={ws}")
    print(f"U1 cpd = {ws.get_cpds('U1')}")
    ctx = {'X': 'w', 'D2': 'n'}
    u = ws.expected_utility(context=ctx, agent=1)
    print(u)


#belief_test()

intention_test()

#evaluation_test() # seems to work fine 

#potential_setting_space_unit_test()

nan_test()




