import tarjan # requires installation
import functools
import random
import pulp # requires installation
import sys

def read_in(file_name):
	matrix = []
	with open(file_name, "r") as fil:
		i = 0
		for line in fil.read().splitlines():
			if i == 0:
				total = int(line)
			elif i == 1:
				children = line.split(" ")
				while "" in children or " " in children:
					if " " in children:
						children.remove(" ")
					if "" in children:
						children.remove("")
				children = list(map(int, children))
			else:
				edges = list(map(int, list(line.replace(" ", "").replace("\t", ""))))
				matrix += [edges]
			i += 1
	return (children, matrix, total) 

def get_scc(edges):
	edges = edges_to_dict(edges)
	# Remove all the ones of size 1
	temp = tarjan.tarjan(edges)
	final = []
	for item in temp:
		if len(item) != 1:
			final += [item]
	return final

def edges_to_dict(edges):
	edges_dict = {}
	fromm = 0
	for line in edges:
		edges_dict[fromm] = []
		too = 0
		for item in line:
			if item == 1:
				edges_dict[fromm] += [too]
			too += 1
		fromm += 1
	return edges_dict

def has_path5(scc, edges):
	edges = edges_to_dict(edges)
	has = set()
	construct = []
	finished = []
	for first in scc:
		hyper_break = False
		if first not in has:
			for second in edges[first]:
				if second not in scc:
					continue
				if first in edges[second]:
					has.add(second)
					has.add(first)
					hyper_break = True
					break
				for third in edges[second]:
					if third not in scc:
						continue
					if first in edges[third]:
						has.add(first)
						has.add(second)
						has.add(third)
						hyper_break = True
						break
					for fourth in edges[third]:
						if fourth not in scc:
							continue
						if first in edges[fourth]:
							has.add(first)
							has.add(second)
							has.add(third)
							has.add(fourth)
							hyper_break = True
							break
						for fifth in edges[fourth]:
							if fifth not in scc:
								continue
							if first in edges[fifth]:
								has.add(first)
								has.add(second)
								has.add(third)
								has.add(fourth)
								has.add(fifth)
								hyper_break = True
								break
						if hyper_break:
							break
					if hyper_break:
						break
				if hyper_break:
					break
	return has

def convert(scc, edges):
	converted = [[] for x in range(0, len(scc))]
	i = 0
	for v in scc:
		for too in edges[v]:
			converted[i] += [too]
		i += 1
	return converted

def get_cycles(scc, edges, children, broken = False):
	size = len(scc)
	added = set()

	# run time issue
	scc = list(has_path5(scc, edges))

	edges = edges_to_dict(edges)

	for i in children:
		if i in scc:
			scc += [i]
	cycles = set()

	i = 0
	while i < search_count or len(added) != size:
		start = random.choice(scc)

		# This can be used for better approximation on hard instances.
		# while i > 2000 and start in added:
		# 	not_added = [item for item in set(scc) if item not in added]
		# 	if not_added:
		#  		start = random.choice(not_added)
		#	else:
		#		continue

		now = start
		cyc = [start]
		while len(cyc) < 2 or cyc[-1] != start:
			a = random.choice(edges[now])
			while a not in scc:
			 	a = random.choice(edges[now])
			next = a
			cyc += [next]
			now = next
			if len(cyc) == 6 and next != start:
				cyc = [start]
				now = start
			elif start in edges[now] and random.random() > 0.5 or next == start:
				if next == start:
					cyc.pop()
				for item in cyc:
					added.add(item)
				already = False
				for item in cycles:
					if set(list(map(int, item.split(" ")))) == set(cyc):
						already = True
				if len(cyc) != len(set(cyc)):
					already = True
				if not already:
					cycles.add(" ".join(str(x) for x in cyc))
				cyc += [start]
		i += 1
	return cycles

def do_all(file_name, estim):
	ch_ma_to = read_in(file_name)
	children = ch_ma_to[0]
	edges = ch_ma_to[1]
	size = ch_ma_to[2]

	sccs = get_scc(edges)

	# Only for instances with run time issues
	# breaker = [[],[],[],[],[]]
	# for scc in sccs:
	# 	scc5 = has_path5(scc, edges)
	# 	for item in scc5:
	# 		breaker[random.randint(0, 4)] += [item]
	# sccs = breaker

	real_sol = ""
	not_used = []
	for scc in sccs:

		# for instance with run time issue
		# new_scc = scc

		# for other instances
		new_scc = has_path5(scc, edges)

		new_scc = list(new_scc)

		if new_scc == []:
			continue
		else:
			if estim:
				cycles = get_cycles(new_scc, edges, children)
			else:
				temp = make_stp(new_scc, edges)
				cycles = []
				obj = next(temp)
				while obj != 0:
					cycles += [obj]
					obj = next(temp)

			if cycles:
				solution = lpsolver(cycles, children, new_scc)
				real_sol += solution[0] + "; "
				not_used += solution[1]
	return (real_sol[0:-2], not_used)

def lpsolver(cycles, children, scc):
	# for each cycle, make a variable
	# for each vertice, make a variable
	# sum of cycle and all of it's conflicting cycles <= 1
	# everything >= 0
	# cycle <= vertices in cycle average (hence if cycle is 1 all vertices in it are 1)
	# minimize sum of (1 - a) + 2(1 - c)

	scc = list(set(scc))
	prob = pulp.LpProblem("Foo", pulp.LpMinimize)

	cycl_vars = []
	for cyc in cycles:
		cycl_vars += [pulp.LpVariable(cyc, lowBound=0, upBound = 1, cat = 'Integer')]
	childs = []
	adults = []
	all_pat = []
	i = 0
	for v in scc:
		all_pat += [pulp.LpVariable(str(v), lowBound=0, upBound=1, cat = 'Integer')]
		if v in children:
			childs += [i]
		else:
			adults += [i]
		i += 1
	dum = pulp.LpVariable("dumb", lowBound=0, upBound=1, cat = 'Integer')
	cost = 0 * dum
	for index in childs:
		cost = cost + 2*(1 - all_pat[index])
	for index in adults:
		cost = cost + (1 - all_pat[index])
	prob += cost

	for v in scc:
		cycle_const = 0 * dum
		i = 0
		for cyc in cycles:
			if v in list(map(int, cyc.split(" "))):
				cycle_const = cycle_const + cycl_vars[i]
			i += 1
		prob += (cycle_const <= 1)

	i = 0
	for person in all_pat:
		const = 0
		j = 0
		for cyc in cycles:
			if scc[i] in list(map(int, cyc.split(" "))):
				const = const + cycl_vars[j]
			j += 1
		i += 1
		prob += (const >= person)

	optimization_result = prob.solve()
	sol = []
	for var in cycl_vars:
		if var.value() > 0.1:
			print(var.name + " " + str(var.value()))
			sol += [var.name.split("_")]
	not_used = []
	for var in all_pat:
		if var.value() == 0:
			not_used += [var.name]

	sol_string = ""
	for item in sol:
		sol_string += " ".join(list(map(str, item))) + "; "
	return (sol_string[0:-2], not_used)


def not_used_sol(vertices, edges, children):
	scc = list(map(int, vertices))
	if len(scc) < 2:
		return "give"
	cycles = get_cycles(list(scc), edges, children)
	if cycles:
		print("These are cycles")
		print(cycles)
	sol = lpsolver(cycles, children, scc)
	not_used = sol[1]
	return (sol[0], not_used)


if __name__ == "__main__":
	cmdargs = sys.argv
	input_file = cmdargs[1]
	if len(cmdargs) > 2:
		search_count = cmdargs[2]
	else:
		search_count = 5000

	with open("solutions.out", "a") as f, open("notused.out", "a") as f2:
		a = do_all(input_file, True)
		f.write(a[0] + "\n")
		f2.write(" ".join(a[1]) + "\n")

# For catching missed cycles
# with open("notused.out", "r") as notused:
# 	with open("addedsols.out", "a") as f, open("stillnotused.out", "a") as f2:
# 		i = 1
# 		for line in notused.read().splitlines():
# 			if line != "" and len(line.split(" ")) > 1:
# 				print("We are on " + str(i))
# 				print(line)
# 				verts = line.split(" ")
# 				print(verts)
# 				ma = read_in("phase1-processed/" + str(i) + ".in")
# 				edges = ma[1]
# 				children = ma[0]
# 				gets = not_used_sol(verts, edges, children)
# 				if gets == "give":
# 					i += 1
# 					continue
# 				f.write(gets[0] + "\n")
# 				f2.write(" ".join(gets[1]) + "\n")
# 			else:
# 				f.write("\n")
# 				f2.write("\n")
# 			i += 1
