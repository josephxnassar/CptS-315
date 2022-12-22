# Reads file and returns list of all lines
def read_file(input):
    with open(input, "r") as infile:
        inputList = infile.read().splitlines()
    return inputList

# Writes single dict to file
def write_file(output, frequencies):
    with open(output, "w") as outfile:
        for entry in frequencies:
            outfile.write(str(entry) + " " + str(frequencies[entry]) + '\n')

# Writes confidence scores to file in desired format
def write_output(output, c1, c2):
    count = 0
    with open(output, "w") as outfile:
        outfile.write("OUTPUT A" + '\n')
        for entry in c1:
            outfile.write(str(entry) + " " + str(c1[entry]) + '\n')
            count += 1
            if count == 5:
                break
        outfile.write("OUTPUT B" + '\n')
        for entry in c2:
            outfile.write(str(entry) + " " + str(c2[entry]) + '\n')
            count += 1
            if count == 10:
                break

# Finds items and their frequencies
def itemFrequencies(inputList):
    itemCounts = dict()
    for row in inputList:
        items = row.split(sep = " ")
        for i in range(len(items) - 1):
            if items[i] in itemCounts:
                itemCounts[items[i]] += 1
            else:
                itemCounts[items[i]] = 1
    sort = dict(reversed(sorted(itemCounts.items(), key = lambda item : item[1])))
    subCent = dict(filter(lambda item: item[1] >= 100, sort.items()))
    return subCent

# Finds pairs and their frequencies
def pairFrequencies(inputList):
    itemCounts = dict() 
    for row in inputList:
        items = row.split(sep = " ")
        for i in range(len(items) - 1):
            for j in range(i+1,len(items) - 1):
                new = items[i] + " " + items[j]
                if new in itemCounts:
                    itemCounts[new] += 1
                else:
                    itemCounts[new] = 1
    sort = dict(reversed(sorted(itemCounts.items(), key = lambda item : item[1])))
    subCent = dict(filter(lambda item: item[1] >= 100, sort.items()))
    return subCent

# Finds triples and their frequencies
def tripleFrequencies(inputList):
    itemCounts = dict()
    for row in inputList:
        items = row.split(sep = " ")
        for i in range(len(items) - 1):
            for j in range(i+1,len(items) - 1):
                for k in range(j+1,len(items) -1):
                    new = items[i] + " " + items[j] + " " + items[k]
                    if new in itemCounts:
                        itemCounts[new] += 1
                    else:
                        itemCounts[new] = 1
    sort = dict(reversed(sorted(itemCounts.items(), key = lambda item : item[1])))
    subCent = dict(filter(lambda item: item[1] >= 100, sort.items()))
    return subCent

# Finds most frequent subsets
def a_priori(inputList):
    return itemFrequencies(inputList), pairFrequencies(inputList), tripleFrequencies(inputList)

# Finds confidence scores for pairs
def confidencePairs(single, pairs):
    confidenceScores = dict()
    for entry in pairs:
        items = entry.split(sep = " ")
        c1, c2 = pairs[entry] / single[items[0]], pairs[entry] / single[items[1]]
        confidenceScores[items[0]+"=>"+items[1]] = c1
        confidenceScores[items[1]+"=>"+items[0]] = c2
    sort = dict(reversed(sorted(confidenceScores.items(), key = lambda item : item[1])))
    return sort

# Finds confidence scores for triples
def confidenceTriple(pairs, triple):
    confidenceScores = dict()
    for entry in triple:
        items = entry.split(sep = " ")
        c1, c2, c3 = triple[entry] / pairs[items[0]+" "+items[1]], triple[entry] / pairs[items[0]+" "+items[2]], triple[entry] / pairs[items[1]+" "+items[2]]
        confidenceScores["("+items[0]+","+items[1]+")=>"+items[2]] = c1
        confidenceScores["("+items[0]+","+items[2]+")=>"+items[1]] = c2
        confidenceScores["("+items[1]+","+items[2]+")=>"+items[0]] = c3
    sort = dict(reversed(sorted(confidenceScores.items(), key = lambda item : item[1])))
    return sort

def main():
    itemList = read_file("browsing-data.txt")
    (single, double, triple) = a_priori(itemList)

    '''
    write_file("outputsingles.txt", single)
    write_file("outputpairs.txt", double)
    write_file("outputtriples.txt", triple)
    '''

    c1 = confidencePairs(single, double)
    c2 = confidenceTriple(double, triple)

    write_output("output.txt", c1, c2)

# Driver
if __name__ == "__main__":
    main()

'''
pairs["DAI62779 ELE17451"] / single["DAI62779"]
pairs["DAI62779 ELE17451"] / single["ELE17451"]
A => B means (A,B) / A
(X,Y) => Z means (X,Y,Z) / (X,Y)
(X,Z) => Y means (X,Y,Z) / (X,Z)
(Y,Z) => X means (X,Y,Z) / (Y,Z)

'''