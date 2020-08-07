from lshash import LSHash
import json
#
lsh = LSHash(6, 8)
#
lsh.index([1, 2, 3, 4, 5, 6, 7, 8] , extra_data = "0")
lsh.index([2, 3, 4, 5, 6, 7, 8, 9] , extra_data = "1")
lsh.index([10, 12, 99, 1, 5, 31, 2, 3] , extra_data = "2")
lsh.query([1, 2, 3, 4, 5, 6, 7, 7])
print(lsh.query([1, 2, 3, 4, 5, 6, 7, 7]))
#
# # another method
# lsh.index([[1, 2, 3, 4, 5, 6, 7, 8],
#            [2, 3, 4, 5, 6, 7, 8, 9],
#            [4, 2, 3, 1, 5, 6, 7, 8],
#            [1, 3, 4, 5, 6, 7, 8, 9],
#            [10, 12, 99, 1, 5, 31, 2, 3]])
"""lsh.index([[1, 2, 3, 4, 5, 6, 7, 8],
           [2, 3, 4, 5, 6, 7, 8, 9],
           [4, 2, 3, 1, 5, 6, 7, 8],
           [1, 3, 4, 5, 6, 7, 8, 9],
           [10, 12, 99, 1, 5, 31, 2, 3]])# , extra_data = ["3","4","5","6","7"])
print(lsh.query([1, 2, 3, 4, 5, 6, 7, 7], distance_func='jaccard'))"""