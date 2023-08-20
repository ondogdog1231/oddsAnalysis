import utils.handicap as h
from config import connector
print(h.handicapDict)

c = connector.config()

result = c.findOdds()
print(result)
for match in result:
    if match[1] not in h.handicapDict:
        print("Not exist")
        continue
    # if h.handicapDict[match[1]]
    print(f"ID:{match[0]}")
    c.updateDecimalHandicap(match[0], h.handicapDict[match[1]])
