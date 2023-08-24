import numpy as np
import itertools
import math
import sys


def diff_perms(v):
    assert 1 <= v <= 8
    perms = set()
    for i in range(1, 10 - v):
        l, r = i, i + v
        perms.add((l, r))
        perms.add((r, l))
    return list(np.array(p) for p in sorted(perms))


def div_perms(v):
    assert 2 <= v <= 9
    perms = set()
    for i in range(1, math.ceil(10 / v)):
        l, r = i*v, i
        perms.add((l, r))
        perms.add((r, l))
    return list(np.array(p) for p in sorted(perms))


def mul_perms(v, N):
    perms = set()
    for i in range(10**(N-1), 10**N):
        digits = [(i // 10**j) % 10 for j in range(N)]
        if np.prod(digits) == v:
            for perm in itertools.permutations(digits):
                perms.add(perm)
    return list(np.array(p) for p in sorted(perms))


def sum_perms(v, N):
    perms = set()
    for i in range(10**(N-1), 10**N):
        digits = [(i // 10**j) % 10 for j in range(N)]
        if 0 in digits:
            continue
        if np.sum(digits) == v:
            for perm in itertools.permutations(digits):
                perms.add(perm)
    return list(perms)


class Constraint:
    def __init__(self, indices, perms):
        N = len(indices)
        for p in perms:
            assert len(p) == N

        self.y, self.x = np.transpose(np.array(indices))
        self.perms     = perms
        self.indices   = indices


class Board:
    def __init__(self, H=9, W=9):
        self.slots         = np.zeros((H, W), dtype=np.int32)
        self.row_bitmap    = [0] * H
        self.column_bitmap = [0] * W
        self.constraints   = []
        self.iter          = 0

    def __repr__(self):
        return repr(self.slots)

    def add_perm(self, p, indices):
        row_bitmap    = self.row_bitmap[:]
        column_bitmap = self.column_bitmap[:]
        for v, (r, c) in zip(p, indices):
            assert not self.slots[r, c]

            mask = (1 << v)
            if row_bitmap[r] & mask:
                return False
            if column_bitmap[c] & mask:
                return False

            row_bitmap[r]    |= mask
            column_bitmap[c] |= mask

        self.row_bitmap    = row_bitmap
        self.column_bitmap = column_bitmap
        for v, (r, c) in zip(p, indices):
            self.slots[r, c] = v

        return True

    def del_perm(self, indices):
        for r, c in indices:
            v = self.slots[r, c]
            assert v != 0

            mask                   = (1 << v)
            self.slots[r, c]       = 0
            self.row_bitmap[r]    &= ~mask
            self.column_bitmap[c] &= ~mask

    def add_constant(self, v, index):
        assert self.add_perm((v,), [index])

    def add_constraint(self, indices, perms):
        self.constraints.append(Constraint(indices, perms))

    def add_sum_constraint(self, v, indices):
        self.add_constraint(indices, sum_perms(v, len(indices)))

    def add_mul_constraint(self, v, indices):
        self.add_constraint(indices, mul_perms(v, len(indices)))

    def add_dif_constraint(self, v, indices):
        assert len(indices) == 2
        self.add_constraint(indices, diff_perms(v))

    def add_div_constraint(self, v, indices):
        assert len(indices) == 2
        self.add_constraint(indices, div_perms(v))

    def _solve(self, ci):
        if ci == len(self.constraints):
            return True

        self.iter += 1

        c = self.constraints[ci]
        for p in c.perms:
            if self.add_perm(p, c.indices):
                print(self)
                # print(' '.join('0x%02X' % b for b in self.row_bitmap))
                # print(' '.join('0x%02X' % b for b in self.column_bitmap))
                if self._solve(ci + 1):
                    return True
                self.del_perm(c.indices)

        return False

    def solve(self):
        return self._solve(0)


if __name__ == '__main__':
    b = Board(9, 9)
    b.add_constant(1, (0, 0))
    b.add_constant(4, (5, 4))
    b.add_constant(6, (6, 8))
    b.add_mul_constraint(40,  [(0, 1), (0, 2)])
    b.add_mul_constraint(360, [(0, 3), (0, 4), (1, 4), (2, 4)])
    b.add_sum_constraint(20,  [(0, 5), (0, 6), (1, 5), (1, 6)])
    b.add_sum_constraint(18,  [(0, 7), (0, 8), (1, 7), (1, 8)])
    b.add_dif_constraint(3,   [(1, 0), (1, 1)])
    b.add_dif_constraint(6,   [(1, 2), (2, 2)])
    b.add_div_constraint(4,   [(1, 3), (2, 3)])
    b.add_dif_constraint(3,   [(2, 0), (2, 1)])
    b.add_sum_constraint(15,  [(2, 5), (3, 3), (3, 4), (3, 5)])
    b.add_div_constraint(2,   [(2, 6), (2, 7)])
    b.add_sum_constraint(20,  [(2, 8), (3, 8), (4, 8), (5, 8)])
    b.add_sum_constraint(10,  [(3, 0), (3, 1), (4, 0)])
    b.add_mul_constraint(30,  [(3, 2), (4, 2), (5, 2), (5, 3)])
    b.add_sum_constraint(20,  [(3, 6), (3, 7), (4, 7)])
    b.add_mul_constraint(784, [(4, 1), (5, 1), (6, 1), (6, 2), (7, 1)])
    b.add_dif_constraint(2,   [(4, 3), (4, 4)])
    b.add_sum_constraint(16,  [(4, 5), (5, 5)])
    b.add_mul_constraint(90,  [(4, 6), (5, 6), (5, 7)])
    b.add_sum_constraint(16,  [(5, 0), (6, 0), (7, 0)])
    b.add_sum_constraint(18,  [(6, 3), (7, 2), (7, 3)])
    b.add_mul_constraint(18,  [(6, 4), (7, 4), (8, 4)])
    b.add_sum_constraint(13,  [(6, 5), (7, 5)])
    b.add_mul_constraint(36,  [(6, 6), (7, 6)])
    b.add_mul_constraint(9,   [(6, 7), (7, 7), (7, 8)])
    b.add_dif_constraint(4,   [(8, 0), (8, 1)])
    b.add_sum_constraint(13,  [(8, 2), (8, 3)])
    b.add_div_constraint(2,   [(8, 5), (8, 6)])
    b.add_dif_constraint(4,   [(8, 7), (8, 8)])
    if b.solve():
        print('Found solution:')
        print(b)
    else:
        print('No solution.')
