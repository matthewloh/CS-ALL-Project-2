# when the reply is less than or equal to 4, 8
# replies 1, 2, 3, 4, 5 offset should be 0 
# for every 5 replies, subtract the len(repliesList) with floor operator * -1
repliesList = [i for i in range(1, 21)]
print(len(repliesList)) 
decrement = (len(repliesList) // 5 * -1) - 1 
print(decrement)
offset = (len(repliesList) + decrement) * -1 