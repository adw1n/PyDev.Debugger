from opcode import HAVE_ARGUMENT, EXTENDED_ARG, hasconst, opname, hasname, hasjrel, haslocal, \
    hascompare, hasfree, cmp_op
import dis
import sys

try:
    xrange
except NameError:
        xrange = range


def collect_try_except_info_py2(co, lasti=-1):
    dis.dis(co)
    code = co.co_code
    labels = dis.findlabels(code)
    linestarts = dict(dis.findlinestarts(co))
    print(sorted(linestarts.items()))
    n = len(code)
    i = 0
    extended_arg = 0
    free = None
    while i < n:
        c = code[i]
        op = ord(c)

        if (opname[op]) == 'SETUP_EXCEPT':
            print('try: at line: %s' % (linestarts[i]))
        i = i + 1
        if op >= HAVE_ARGUMENT:
            oparg = ord(code[i]) + ord(code[i + 1]) * 256 + extended_arg
            extended_arg = 0
            i = i + 2
            if op == EXTENDED_ARG:
                extended_arg = oparg * 65536
            print(repr(oparg).rjust(5))
            if op in hasconst:
                print('(' + repr(co.co_consts[oparg]) + ')1')
            elif op in hasname:
                print('(' + co.co_names[oparg] + ')2')
            elif op in hasjrel:
                try:
                    print('(to line' + repr(linestarts[i + oparg]) + ')3a')
                except:
                    print('(to bytecode offset: ' + repr(i + oparg) + ')3b')
            elif op in haslocal:
                print('(' + co.co_varnames[oparg] + ')4')
            elif op in hascompare:
                print('(' + cmp_op[oparg] + ')5')
            elif op in hasfree:
                if free is None:
                    free = co.co_cellvars + co.co_freevars
                print('(' + free[oparg] + ')6')


if sys.version_info[0] <= 2:
    collect_try_except_info = collect_try_except_info_py2
else:
    collect_try_except_info = collect_try_except_info_py3


def _method_simple_raise_local_load():
    x = AssertionError
    try:  # SETUP_EXCEPT (to except line)
        raise AssertionError()
    except x as exc:
        # DUP_TOP, LOAD_GLOBAL (NameError), LOAD_GLOBAL(AssertionError), BUILD_TUPLE,
        # COMPARE_OP (exception match), POP_JUMP_IF_FALSE
        pass


def _method_simple_raise_multi_except():
    try:  # SETUP_EXCEPT (to except line)
        raise AssertionError()
    except (NameError, AssertionError) as exc:
        # DUP_TOP, LOAD_FAST (x), COMPARE_OP (exception match), POP_JUMP_IF_FALSE
        pass


def _method_simple_raise_unmatched_except():
    try:  # SETUP_EXCEPT (to except line)
        raise AssertionError()
    except NameError:  # DUP_TOP, LOAD_GLOBAL (NameError), COMPARE_OP (exception match), POP_JUMP_IF_FALSE
        pass


def _method_simple_raise_any_except():
    try:  # SETUP_EXCEPT (to except line)
        raise AssertionError()
    except:  # POP_TOP
        pass


def _method_try_except():
    try:  # SETUP_EXCEPT (to except line)
        try:  # SETUP_EXCEPT (to except line)
            pass
        except:  # POP_TOP
            raise
    except:  # POP_TOP
        pass


def test_findlinestarts():
    code = _method_simple_raise_local_load.__code__
    collect_try_except_info(code)
