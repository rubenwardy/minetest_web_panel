class Conf:
	settings = {}
	def set(self, setting, val):
		self.settings[setting] = val

	def get(self, setting):
		return self.settings[setting]

	def read(self, filename):
		with open(filename, "r") as f:
			for i, line in enumerate(f.readlines()):
				arr = line.split("=")
				if len(arr) == 2:
					self.set(arr[0].strip(), arr[1].strip())
				else:
					print("Invalid number of parts on line " + str(i) +\
						". Only one '=' should be present.")

	def write(self, filename):
		with open(filename, "w") as f:
			for key, value in self.settings.iteritems():
				f.write(key + " = " + value + "\n")
