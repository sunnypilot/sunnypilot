filenames = ['/data/params/d/HondaCars', '/data/params/d/HyundaiCars', '/data/params/d/SubaruCars',
             '/data/params/d/ToyotaCars', '/data/params/d/VolkswagenCars']

with open('/data/params/d/Cars', 'w') as outfile:
  for names in filenames:
    with open(names) as infile:
      outfile.write(infile.read())
    outfile.write("\n")