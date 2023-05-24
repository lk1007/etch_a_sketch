import path

p = path.PathMaker("test/null", "images/pepe.jpeg", precision_factor=100000000000)
p.brightness_maker([200])
p.start()
