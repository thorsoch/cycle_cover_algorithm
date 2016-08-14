with open("solutions.out", "r") as fil:
	i = 1
	for line in fil.read().splitlines():
		cycles = line.split(";")
		alls = []
		for cycle in cycles:
			vs = cycle.split(" ")
			for item in vs:
				alls += [item]
			if (len(set(vs)) != len(vs)):
				print(str(i) + " is broken because of " + cycle)
		if len(set(alls)) != len(alls):
			print(str(i) + " is broken because of overlap")
			while alls != []:
				thing = alls.pop()
				if thing in alls:
					print(thing)
		i += 1