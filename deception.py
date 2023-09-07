import pycid

from intention import intends_to_cause
from belief import belief

from learning import test_learning_procedure as learn
from utils import get_unique_outcome, evaluate_prop


def deceives(macid : pycid.MACID, deceiver, deceivee, 
             policy, ref_policy, ctx, prop, var,
             dr_cf_policy=None, de_cf_policy=None, learning_procedure=None):
    #NOTE : in the paper, outcome is D^T. Does it mean only 1 decision variable, or the set of decisions??

    S_intends = intends_to_cause(macid, deceiver, policy, ref_policy, var, ctx)

    T_believes = belief(macid, deceivee, policy, prop, ctx=ctx, learning_procdure=learn, cf_policy=de_cf_policy)

    S_believes = belief(macid, deceiver, policy, prop, ctx=ctx, learning_procedure=learn, cf_policy=dr_cf_policy)

    prop_value = evaluate_prop(macid, prop, ctx)
    
    return S_intends and T_believes and not S_believes and not prop_value 

def is_deceptive(macid: pycid.MACID, deceiver, policy, ref_policy):
    # This method could have way more work.
    # it could, as before, check every or a good subset of settings
    # it could test for all or many deceivee
    # it could try to find or build a proposition about which there might be deception, with an outcome to go with
    ... # TODO