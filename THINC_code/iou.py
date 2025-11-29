import numpy as np

# Example array
arr = np.array([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]])

# Deleting along axis=0 (row-wise deletion)
deleted_row = np.delete(arr, 1, axis=0)

print("Array after deleting along axis=0:")
print(deleted_row)

# Deleting along axis=1 (column-wise deletion)
deleted_column = np.delete(arr, 1, axis=1)

print("\nArray after deleting along axis=1:")
print(deleted_column)

X = arr.copy()

X[1] = [50, 60, 70]

print()
print(arr)
print()
print(X)