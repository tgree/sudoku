import numpy as np
import itertools
import math


class DiffConstraint:
    def __init__(self, v):
        assert 1 <= v <= 8
        self.perms = []
        for i in range(1, 10 - v):
            self.perms.append((i, i + v))
            self.perms.append((i + v, i))


class DivideConstraint:
    def __init__(self, v):
        assert 2 <= v <= 9
        self.perms = []
        for i in range(1, math.ceil(10 / v)):
            l, r = i*v, i
            self.perms.append((l, r))
            if l != r:
                self.perms.append((r, l))


class MultiplyConstraint:
    def __init__(self, v, N):
        perms = set()
        for i in range(10**(N-1), 10**N):
            digits = [(i // 10**j) % 10 for j in range(N)]
            if np.prod(digits) == v:
                for perm in itertools.permutations(digits):
                    perms.add(perm)
        self.perms = list(perms)


class AddConstraint:
    def __init__(self, v, N):
        perms = set()
        for i in range(10**(N-1), 10**N):
            digits = [(i // 10**j) % 10 for j in range(N)]
            if 0 in digits:
                continue
            if np.sum(digits) == v:
                for perm in itertools.permutations(digits):
                    perms.add(perm)
        self.perms = list(perms)


def check_equals_ok(board, indice, v):
    return board[indice] == 0 or board[indice] == v


def check_sum_ok(board, indices, v):
    y, x = np.transpose(np.array(indices))
    a    = board[y, x]
    s    = np.sum(a)
    return (not np.all(a) and s < v) or s == v


def check_product_ok(board, indices, v):
    y, x = np.transpose(np.array(indices))
    a    = board[y, x]
    p    = np.prod(a)
    return (not np.all(a) and p <= v) or p == v


def check_diff_ok(board, indices, v):
    y, x = np.transpose(np.array(indices))
    a    = board[y, x]
    return not np.all(a) or np.abs(np.diff(a)) == v


def check_divide_ok(board, indices, v):
    y, x = np.transpose(np.array(indices))
    a    = board[y, x]
    return not np.all(a) or a[0] / a[1] == v or a[1] / a[0] == v


def are_constraints_satisfied(board, r, c):
    return (# check_equals_ok(board, (0, 0), 1) and
            check_product_ok(board, [(0, 1), (0, 2)], 40) and
            check_product_ok(board, [(0, 3), (0, 4), (1, 4), (2, 4)], 360) and
            check_sum_ok(board, [(0, 5), (0, 6), (1, 5), (1, 6)], 20) and
            check_sum_ok(board, [(0, 7), (0, 8), (1, 7), (1, 8)], 18) and
            check_diff_ok(board, [(1, 0), (1, 1)], 3) and
            check_diff_ok(board, [(1, 2), (2, 2)], 6) and
            check_divide_ok(board, [(1, 3), (2, 3)], 4) and
            check_diff_ok(board, [(2, 0), (2, 1)], 3) and
            check_sum_ok(board, [(2, 5), (3, 3), (3, 4), (3, 5)], 15) and
            check_divide_ok(board, [(2, 6), (2, 7)], 2) and
            check_sum_ok(board, [(2, 8), (3, 8), (4, 8), (5, 8)], 20) and
            check_sum_ok(board, [(3, 0), (3, 1), (4, 0)], 10) and
            check_product_ok(board, [(3, 2), (4, 2), (5, 2), (5, 3)], 30) and
            check_sum_ok(board, [(3, 6), (3, 7), (4, 7)], 20) and
            check_product_ok(board, [(4, 1), (5, 1), (6, 1), (6, 2), (7, 1)], 784) and
            check_diff_ok(board, [(4, 3), (4, 4)], 2) and
            check_sum_ok(board, [(4, 5), (5, 5)], 16) and
            check_product_ok(board, [(4, 6), (5, 6), (5, 7)], 90) and
            check_sum_ok(board, [(5, 0), (6, 0), (7, 0)], 16) and
            # check_equals_ok(board, (5, 4), 4) and
            check_sum_ok(board, [(6, 3), (7, 2), (7, 3)], 18) and
            check_product_ok(board, [(6, 4), (7, 4), (8, 4)], 18) and
            check_sum_ok(board, [(6, 5), (7, 5)], 13) and
            check_product_ok(board, [(6, 6), (7, 6)], 36) and
            check_product_ok(board, [(6, 7), (7, 7), (7, 8)], 9) and
            # check_equals_ok(board, (6, 8), 6) and
            check_diff_ok(board, [(8, 0), (8, 1)], 4) and
            check_sum_ok(board, [(8, 2), (8, 3)], 13) and
            check_divide_ok(board, [(8, 5), (8, 6)], 2) and
            check_diff_ok(board, [(8, 7), (8, 8)], 4) and
            True
            )


def fill_square(board, r, c):
    # If square was pre-filled, hold it constant.
    if board[r, c]:
        if r == 8 and c == 8:
            return True
        if c == 8:
            print()
            print(board)
            if fill_square(board, r + 1, 0):
                return True
        else:
            if fill_square(board, r, c + 1):
                return True
        return False

    # Otherwise, try all values.
    for v in range(1, 10):
        if v in board[r, :]:
            continue
        if v in board[:, c]:
            continue

        board[r, c] = v
        if not are_constraints_satisfied(board, r, c):
            continue

        if r == 8 and c == 8:
            return True
        if c == 8:
            print()
            print(board)
            if fill_square(board, r + 1, 0):
                return True
        else:
            if fill_square(board, r, c + 1):
                return True

    # Reset it back to zero.
    board[r, c] = 0
    return False


if __name__ == '__main__':
    board = np.zeros((9, 9))
    board[0, 0] = 1
    board[5, 4] = 4
    board[6, 8] = 6
    if fill_square(board, 0, 0):
        print('Found solution:')
        print(board)
    else:
        print('No solution.')
