import pycid


def S_utility(X, DS, DT):
		us = 0
		if X == "s":
			if DS == "d":
				us+= 1
		elif X == "w":
			if DS == "r":
				us +=1
		if DT == "n":
			us += 2
		return us

def T_utility(X, DT):
	u = 1 if DT == "a" else 0
	ret = u if X=="w" else 1 - u
	return ret

def wimp_surly_macid():
	
	ws = pycid.MACID(
		[
			("X", "D1"),
			("X", "U1"),
			("X", "U2"),
			("D1", "D2"),
			("D1", "U1"),
			("D2", "U1"),
			("D2", "U2")
		],

		agent_decisions = {1 : ["D1"], 2 : ["D2"]},
		agent_utilities = {1 : ["U1"], 2 : ["U2"]}
	)

	d1_domain = ["d", "r"] # defend or retreat
	d2_domain = ["a", "n"] # attack or not


	ws.add_cpds(
		X={"s": 0.9, "w": 0.1},
		D1=d1_domain,
		D2=d2_domain,
		U1=lambda X, D1, D2 : S_utility(X, D1, D2),
		U2=lambda X, D2 : T_utility(X, D2),
	)

	return ws

def test_ws_variant():
	ws = wimp_surly_macid()
	ws.update(nodes=[
		"A", "B", "C"
	])
	ws.add_cpds(
		A={"a" : 0.5, "b" : 0.5},
		B={"c" : 0.3, "d":0.7},
		C={"e":0.2, "f": 0.8}
	)

	return ws