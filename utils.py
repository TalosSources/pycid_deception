import pycid
import inspect

def get_unique_outcome(macid : pycid.MACID, var, setting, policy=None):
    return macid.query([var], setting).sample(1)._values[0][0]


def evaluate_prop(macid : pycid.MACID, prop, ctx):
    params = inspect.signature(prop).parameters
    print(f"params={params}")
    names = [name for name, _ in params.items()]

    params_outcomes = [ctx[var] if var in ctx.keys() else get_unique_outcome(macid , var, ctx) for var in names]

    return prop(*params_outcomes)


def some_test():
    from games import wimp_surly_macid

    ws = wimp_surly_macid()
    ws.impute_fully_mixed_policy_profile()

    outcome = get_unique_outcome(ws, "D1", {"X" : "s"})
    print(outcome)

#some_test()