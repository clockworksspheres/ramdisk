
import re

stringOne   = r"c:\one\andAThird\andAHalf" 
stringTwo   = r"c:\\one\\two\\three"
stringThree = r'c:\\\one\\\and\\\ahalf'
stringFour  = r"c:\\\one\\two\three"
stringFive  = r"c:\one\\two\\\three"
stringSix   = r'c:\\\one\\\and\\\\\ahalf'

mystrings = [stringOne, stringTwo, stringThree, stringFour, stringFive]

for string in mystrings:
   print(f"{string}")

match = re.search("(\\+)?", stringOne)

#print(match.group(1))

print("\n----------\n")

if re.search(r"\\{3}", stringThree):
    print(stringThree)

print("\n----------\n")

if re.search(r"\\{3,}", stringThree):
    print(stringThree)

print("\n----------\n")

if re.search(r"\\{3,}", stringSix):
    print(stringThree)

print("\n----------\n")

mysub = re.sub(r"\\{1,}", r"\\\\", stringOne)
print(mysub)

print("\n----------\n")

mysub = re.sub(r"\\{1,}", r"\\\\", stringFive)
print(mysub)

print("\n----------\n")



print("\n----------\nDone...")
# print(match.group(1))

