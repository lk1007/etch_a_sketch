import python.path_original as path_original

p = path_original.PathMaker("test/null", "images/pepe.jpeg", precision_factor=10)
p.brightness_maker([200])

p.start()
