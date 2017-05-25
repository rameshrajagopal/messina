import json
import unicodecsv as csv

def converter(json_file, csv_file):
    brands = []
    with open(json_file, "rb") as f:
        d = json.load(f)
        for e in d:
            brands.append(e["name"])
    with open(csv_file, "wb") as f:
        writer = csv.writer(f, delimiter=",")
        try:
            writer.writerow(brands)
        except UnicodeEncodeError as e:
            print e
    return None

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print "Wrong usage", sys.argv[0], " <input.json> <output.csv>"
        sys.exit(-1)
    converter(sys.argv[1], sys.argv[2])
