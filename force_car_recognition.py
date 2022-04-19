filenames = ['/data/params/d/HyundaiCars']

with open('/data/params/d/Cars', 'w') as outfile:
    for names in filenames:
        with open(names) as infile:
            outfile.write(infile.read())
        outfile.write("\n")