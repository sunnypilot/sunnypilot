filenames = ['/data/params/d/HyundaiCars', '/data/params/d/HondaCars', '/data/params/d/SubaruCars']

with open('/data/params/d/Cars', 'w') as outfile:
    for names in filenames:
        with open(names) as infile:
            outfile.write(infile.read())
        outfile.write("\n")