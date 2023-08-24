import argparse
import itertools
import math
import sys

import numpy as np


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


def set_perms(digits):
    return list(itertools.permutations(digits))


class Constraint:
    def __init__(self, indices, perms):
        N = len(indices)
        for p in perms:
            assert len(p) == N

        self.y, self.x = np.transpose(np.array(indices))
        self.perms     = perms
        self.indices   = indices


class Board:
    def __init__(self, array):
        H = len(array)
        W = len(array[0])

        self.slots         = np.array(array, dtype=np.int32)
        self.init_slots    = np.copy(self.slots)
        self.row_bitmap    = [0] * H
        self.column_bitmap = [0] * W
        self.constraints   = []
        self.iter          = 0

        for r in range(H):
            for c in range(W):
                v = self.slots[r, c]
                if v:
                    self.row_bitmap[r]    |= (1 << v)
                    self.column_bitmap[c] |= (1 << v)

    def __repr__(self):
        return repr(self.slots)

    @staticmethod
    def from_sudoku(array):
        b = Board(array)
        for y in range(3):
            for x in range(3):
                digits  = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
                indices = []
                for Y in range(y*3, y*3 + 3):
                    for X in range(x*3, x*3 + 3):
                        digits.discard(b.slots[Y, X])
                        if b.slots[Y, X] == 0:
                            indices.append((Y, X))
                b.add_set_constraint(digits, indices)
        return b

    @staticmethod
    def from_epoch_doku(lines):
        lines = [l.strip() for l in lines]
        for l in lines:
            l.replace(' ','')

        D = len(lines[0])
        assert lines[D] == ''
        array = np.zeros((D, D))
        idict = {}
        for r, l in enumerate(lines[:D]):
            for c, k in enumerate(l):
                if k in '123456789':
                    array[r, c] = int(k)
                else:
                    if k not in idict:
                        idict[k] = []
                    idict[k].append((r, c))

        b = Board(array)
        for l in lines[D+1:]:
            k  = l[0]
            op = l[1]
            v  = int(l[2:])
            if op == '+':
                b.add_sum_constraint(v, idict[k])
            elif op == '-':
                b.add_dif_constraint(v, idict[k])
            elif op == '*':
                b.add_mul_constraint(v, idict[k])
            elif op == '/':
                b.add_div_constraint(v, idict[k])
            else:
                raise Exception('Unrecognized op: "%s"' % k)
            del idict[k]
        if idict:
            raise Exception('Missing constraints: %s' % idict.keys())

        return b

    def add_perm(self, p, indices):
        row_bitmap    = self.row_bitmap[:]
        column_bitmap = self.column_bitmap[:]
        for v, (r, c) in zip(p, indices):
            iv = self.init_slots[r, c]
            if iv:
                if v != iv:
                    return False
            else:
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

    def add_set_constraint(self, digits, indices):
        self.add_constraint(indices, set_perms(digits))

    def _filter(self):
        for c in self.constraints:
            perms = []
            for p in c.perms:
                if self.add_perm(p, c.indices):
                    perms.append(p)
                    self.del_perm(c.indices)
            c.perms = perms

    def _solve(self, ci):
        if ci == len(self.constraints):
            return True

        c = self.constraints[ci]
        for p in c.perms:
            self.iter += 1
            if self.add_perm(p, c.indices):
                print(self)
                if self._solve(ci + 1):
                    return True
                self.del_perm(c.indices)

        return False

    def solve(self, no_filter=False):
        if not no_filter:
            print('Filtering...')
            self._filter()
        print('Solving...')
        return self._solve(0)


def easy_sudoku_1():
    b = Board.from_sudoku([[8, 0, 6,   0, 2, 7,   0, 0, 0],
                           [0, 9, 3,   0, 6, 0,   2, 0, 0],
                           [1, 4, 2,   0, 0, 0,   0, 8, 7],

                           [0, 0, 1,   6, 0, 9,   0, 0, 0],
                           [6, 8, 0,   0, 0, 2,   0, 1, 0],
                           [0, 2, 0,   0, 0, 1,   3, 4, 0],

                           [0, 0, 0,   0, 7, 3,   0, 0, 0],
                           [4, 3, 0,   2, 9, 0,   5, 0, 0],
                           [0, 6, 0,   0, 0, 0,   0, 0, 2],
                           ])
    return b


def hard_sudoku_1():
    b = Board.from_sudoku([[0, 0, 9,   0, 0, 0,   7, 0, 3],
                           [0, 3, 0,   0, 8, 0,   0, 0, 0],
                           [5, 0, 4,   0, 0, 0,   9, 0, 0],

                           [0, 6, 0,   0, 0, 0,   0, 0, 0],
                           [1, 0, 0,   2, 3, 0,   0, 0, 0],
                           [7, 0, 0,   0, 0, 9,   0, 1, 0],

                           [0, 0, 0,   0, 0, 4,   2, 3, 6],
                           [0, 0, 1,   0, 0, 5,   4, 9, 0],
                           [0, 0, 7,   0, 0, 0,   0, 0, 0],
                           ])
    return b


def main(args):
    print('Building...')
    if args.file:
        if args.file.endswith('.epo'):
            with open(args.file, encoding='utf8') as f:
                b = Board.from_epoch_doku(f.readlines())
        else:
            print('Unknown extension: "%s"' % args.file)
            return
    elif args.board == 1:
        b = easy_sudoku_1()
    elif args.board == 2:
        b = hard_sudoku_1()
    else:
        print('Unknown board %s.' % args.board)
        return

    if b.solve(no_filter=args.no_filter):
        print('Found solution:')
        print(b)
    else:
        print('No solution.')
    print('%u iterations.' % b.iter)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', type=int)
    parser.add_argument('--file', '-f')
    parser.add_argument('--no-filter', action='store_true')
    args = parser.parse_args()
    main(args)


if __name__ == '__main__':
    _main()
