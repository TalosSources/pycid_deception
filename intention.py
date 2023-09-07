import pycid
from copy import deepcopy

from utils import get_unique_outcome

def rec_find_settings(tables):
    #tables is a kv where {k = variable name, v = a kv where {k = outcome, v = prob}}
    #we need to return a list of pairs (a kv where {k = var_name, v = outcome}, prob for setting k)
    if len(tables) == 0:
        return [({}, 1.0)]
    else:
        var = next(iter(tables)) # var is any variable in tables.keys()
        table = tables[var] # table is a kv {outcome, prob}
        settings = []
        c_tables = deepcopy(tables)
        del c_tables[var]
        for o in table.keys():
            p = table[o] # the prob of having outcome o for variable var
            rec_settings = rec_find_settings(c_tables) # settings for all other variables
            for sub_s, sub_prob in rec_settings:
                s = deepcopy(sub_s)
                s[var] = o
                settings.append((s, sub_prob * p)) # the new prob is the prob of the considered sub-setting * the prob of the added outcome

        return settings



def compute_setting_space(macid : pycid.MACID):
    #find every variable that is part of the setting (not decision nor utility etc.)
    #using their domain, compute every possible combination of them. 
    # the prob of a combination is just the product of the probs of the outcome of each variable

    variables = [n for n in macid.nodes if n not in macid.decisions and n not in macid.utilities]
    tables = {n : macid.get_cpds(n).func() for n in variables} # all the outcome-probabilities maps for exog. variables

    all_settings = rec_find_settings(tables)

    return all_settings

def fix_outcome(macid: pycid.MACID, outcome, policy, agent) -> pycid.MACID :
    # perform intervention : we fix the outcome variable to what it would have been if the agent choose the given policy
    # pretty hard : seems to require either keeping track of the original game, or massively duplicating nodes.
    # 
    # or maybe there's a pycid feature that's handy here
    c_macid = deepcopy(macid)

    # TODO_ : idea: cache values of the outcome variable, and assign it with context or hard intervention to the variable in the interventioned game
    
    parents = macid.get_parents(outcome)

    ... # TODO_ : too hard for now, need to ask questions

    return macid

def compute_intervention(macid: pycid.MACID, var, policy, every_setting) -> pycid.MACID :
    # s is a ctx, so dict(variable_name, outcome)

    cache = {}
    macid.add_cpds(policy)
    for s, _ in every_setting:
        outcome = get_unique_outcome(macid, var, s)
        cache[s] = outcome

    def intervene(ctx):
        ctx = deepcopy(ctx)
        ctx[var] = cache[ctx]
        return ctx

    return intervene
    

def check_inequality(W, e_a_u : float, r_u_n_i, r_u_i):
    # r_u_n_i and r_u_i would be dicts of setting : (utility, prob) ... 
    # NOTE best we can have until I find a better way to compute expected utilities 
    # conditioned on context subsets rather than single contexts 
    # W would be a set of settings, or no : a dict of setting -> boolean, 
    # indicating which one are in the checked set (so using r_u_i ctx)
    r_u_n_i = deepcopy(r_u_n_i)
    for i, (_, b) in enumerate(W) :
        if b:
            r_u_n_i[i] = r_u_i[i]

    w_expected_utility = 0 # this should sometimes be 3. 
    for _, (u, p) in r_u_n_i:
        w_expected_utility += u * p
    #print(f"w_expected_utility={w_expected_utility}")
    print(f"comparing eau={e_a_u} and w_e_u={w_expected_utility} (runi={r_u_n_i})")
    return e_a_u <= w_expected_utility


def minimal_set_exists(W, e_a_u, r_u_n_i, r_u_i):
    #maybe W could be a dict of setting -> is_in_set

    if check_inequality(W, e_a_u, r_u_n_i, r_u_i):
        return True
    else:
        for (s, b) in W:
            if not b: # an element that could be added to form a potential minimal set
                W_c = deepcopy(W)
                W_c.remove((s, False))
                W_c.append((s, True))
                if minimal_set_exists(W_c, e_a_u, r_u_n_i, r_u_i):
                    return True
    
    print(f"testing for W={W}, eau={e_a_u}, runi={r_u_n_i}, rui={r_u_i} returned false")
    return False

def intends_to_cause(macid : pycid.MACID, agent, policy, ref_policy, var, e) -> bool :
    """
    outcome represents a set of variable names?
    let's first suppose it represents just one variable
    """

    """
    new way to represent itv_games : 
    when querying an itv_game, we take the context, and pass it through a intervene_context function, taking the context, 
    and some data structure indexed by the setting (here the given context), giving a fixed value for a set of variables.
    that function returns a new context, where the outcome are fixed to what they would have been in the other game given that setting.
    in that case, the intervene_context function is in fact the intervention itself.
    """

    outcome = get_unique_outcome(macid, var, e)

    def intervene(ctx_):
        ctx = deepcopy(ctx_)
        #outcome = get_unique_outcome(macid, var, ctx)
        ctx[var] = outcome
        print(f"intervention on {ctx_} yields {ctx}")
        return ctx

    every_setting = compute_setting_space(macid)


    # build game with intervention (things agent would do done for them)
    
    #itv_macid = fix_outcome(macid, outcome, policy, agent)
    #intervention = compute_intervention(macid, outcome, policy, agent, every_setting)
    #intervention = compute_intervention(macid, var, policy, every_setting)
    
    macid = deepcopy(macid)

    # retrieve all utilities needed (3 categories)
        # 1. actual utilities
    macid.add_cpds(policy)
    expected_actual_utility = macid.expected_utility(agent=agent, context={})

    # dicts of setting : (utility, prob)
    r_u_n_i = []    # reference utility no intervention
    r_u_i = []      # reference utility intervention

    W = []

    macid.add_cpds(ref_policy)
    print(f"macid={macid}")
    print(f"U1 cpd = {macid.get_cpds('U1')}")
    #itv_macid.add_cpds(ref_policy)
    for s, p in every_setting :
        no_u = macid.expected_utility(context=s, agent=agent)
        r_u_n_i.append((s, (no_u, p)))

        #u = itv_macid.expected_utility(context=s, agent=agent)
        itv_s = intervene(s)
        u = macid.expected_utility(context=itv_s, agent=agent)
        print(f"for itv_s = {itv_s}, we get u = {u}")
        r_u_i.append((s, (u, p))) # NOTE maybe we don't need to have the p stored twice
        # good thing : r_u_n_i and r_u_i have the same setting order, handy

        #print(f"hello! s={s}")
        W.append((s, False)) # every setting -> False for empty set

    print(f"rui={r_u_i} \n\n")
    print(f"runi={r_u_n_i} \n\n")

    # if empty checks satisfies the inequality, no set containing e can be minimal
    if check_inequality(W, expected_actual_utility, r_u_n_i, r_u_i): 
        print(f"finished at empty set check")
        #print(f"testing for W={W}, eau={expected_actual_utility}, runi={r_u_n_i}, rui={r_u_i} returned false")
        return False
    
    W.remove((e, False))
    W.append((e, True))
    #print(f"W={W}")

    #find minimal set satisfying condition
    return minimal_set_exists(W, expected_actual_utility, r_u_n_i, r_u_i)
