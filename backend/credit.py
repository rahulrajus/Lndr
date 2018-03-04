def withdraw(user1, user2, amount):
    a[user1] -= amount
    a[user2] += amount
a = {}
with open("out.txt", "r") as f:
    for line in f:
        lolz = line.split(",")
        a.update({lolz[0]: int(lolz[1])})
print(a)
