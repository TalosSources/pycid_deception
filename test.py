import pycid
import games

game = games.wimp_surly_macid()

game.impute_fully_mixed_policy_profile()

u = game.expected_utility(context={}, agent=1)
print(u)


f = lambda X : "d" if X == "s" else "r"
honest_S_policy = pycid.StochasticFunctionCPD("D1", f, game)


g = lambda D1 : "a" if D1 == "r" else "n"
honest_T_policy = pycid.StochasticFunctionCPD("D2", g, game)

game.add_cpds(honest_S_policy, honest_T_policy)

u = game.expected_utility(context={"X" : "s", "D1" : "d"}, agent=1)
print(u)


