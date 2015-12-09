import sys, re

class Juggler:
	regex = r'^J (J[0-9]+) (H:[0-9]+) (E:[0-9]+) (P:[0-9]+) ((C[0-9]+,?)+)$'
	def __init__(self, string, circuits):
		match = re.match(Juggler.regex, string)
		if not match:
			raise ValueError('Invalid string ' + string)
		self.name = match.group(1)
		hand_eye = int(match.group(2).split(':')[1])
		endurance = int(match.group(3).split(':')[1])
		pizzazz = int(match.group(4).split(':')[1])
		self.stats = (hand_eye, endurance, pizzazz)
		self.preferred_circuits = [circuits[int(c[1:])] for c in match.group(5).split(',')]


	def dot_product(self, other):
		return sum(a*b for a, b in zip(self.stats, other.stats))


class Circuit:
	regex = r'^C (C[0-9]+) (H:[0-9]+) (E:[0-9]+) (P:[0-9]+)$'
	def __init__(self, string):
		match = re.match(Circuit.regex, string)
		if not match:
			raise ValueError('Invalid string ' + string)
		self.name = match.group(1)
		hand_eye = int(match.group(2).split(':')[1])
		endurance = int(match.group(3).split(':')[1])
		pizzazz = int(match.group(4).split(':')[1])
		self.stats = (hand_eye, endurance, pizzazz)
		self.jugglers = list()

	def __str__(self):
		string = self.name + " "
		for juggler in self.jugglers:
			string = string + juggler.name + " " + " ".join("%s:%d" % \
				(circuit.name, juggler.dot_product(circuit)) for circuit in juggler.preferred_circuits) + ", "
		string = string[:-2]
		return string


def main():
	if len(sys.argv) != 2:
		print "Usage: python jugglers.py <filename>"
		sys.exit()
	jugglers = list()
	circuits = list()
	try:
		with open(sys.argv[1], 'r') as inputfile:
			for line in inputfile:
				try:
					if line[0] == 'C':
						circuits.append(Circuit(line))
					elif line[0] == 'J':
						jugglers.append(Juggler(line, circuits))
				except Exception, e:
					print "Something went wrong while reading the file:", e
					sys.exit()
	except IOError:
		print "Couldn't read file", sys.argv[1]
		sys.exit()
	assign_jugglers(circuits, jugglers)
	write_file(circuits)

	# answer = 0
	# for juggler in circuits[1970].jugglers:
		# answer = answer + int(juggler.name[1:])
	# print "Answer:", answer

def write_file(circuits):
	try:
		with open('output.txt', 'w') as output_file:
			for circuit in circuits:
				output_file.write(str(circuit) + "\n")
	except IOError, e:
		print "Couldn't save file", e
		sys.exit()

def assign_jugglers(circuits, jugglers):
	
	def assign_juggler(juggler):
		jugglers_per_circuit = len(jugglers) / len(circuits)
		# give them the most preferred one that they aren't a worse fit for than everyone in it
		assigned = False
		for preferred in juggler.preferred_circuits:
			# if it has room, just put them in it
			if len(preferred.jugglers) < jugglers_per_circuit:
				print "Assigning " + juggler.name + " to " + preferred.name
				preferred.jugglers.append(juggler)
				assigned = True
				break
			# if it's full, see if anyone there is a worse fit and re-assign them
			else:
				score = juggler.dot_product(preferred)
				for other_juggler in preferred.jugglers:
					other_score = other_juggler.dot_product(preferred)
					if other_score < score:
						preferred.jugglers.remove(other_juggler)
						print "Assigning " + juggler.name + " to " + preferred.name + " " + str(score) + \
							" and removing "+other_juggler.name + " " + str(other_score)
						preferred.jugglers.append(juggler)
						assign_juggler(other_juggler)
						assigned = True
						break
				# once this one's assigned, no need to check the other circuits
				if assigned:
					break
		# if none of the preferred circuits worked, just put them in the first empty one
		if not assigned:
			for circuit in circuits:
				if len(circuit.jugglers) < jugglers_per_circuit:
					print "Assigning " + juggler.name + " to " + circuit.name
					circuit.jugglers.append(juggler)
					break

	for juggler in jugglers:
		assign_juggler(juggler)

if __name__ == '__main__':
	main()