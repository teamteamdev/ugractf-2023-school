import os
import subprocess
import sys
from collections import deque


class CompilationError(ValueError):
    pass


def sanitize_label(label):
    return "L" + label.encode().hex()


def compile_code(code):
    registers = {
        "a": "%%rax",
        "b": "%%rbx",
        "c": "%%rcx",
        "d": "%%rdx"
    }

    def parse_arg(arg, insn):
        if not arg:
            raise CompilationError(f'invalid arg in {insn}')
        if (arg[0] == '-' and arg[1:].isdigit()) or arg.isdigit():
            return "$" + arg
        if arg in registers:
            return registers[arg]
        raise CompilationError(f'invalid arg in {insn}')

    labels = set()
    lines = deque(line.strip() for line in code.splitlines())
    defines = {}
    defines_count = {}
    used_labels = set()

    while lines:
        line = lines.popleft().lower()
        if not line or line.startswith('//'):
            continue

        if line.endswith('!'):
            name = line[:-1]
            content = defines.get(name)
            if not content:
                raise CompilationError('call of not defined macro')
            label_prefix = f'{name}-{defines_count[name]}#'
            for l in content:
                if l.endswith(':'):
                    l = label_prefix + l
                elif '{}' in l:
                    if l.count('{}') > 1:
                        raise CompilationError('invalid label')
                        return
                    l = l.format(label_prefix)
                lines.appendleft(l)
            defines_count[name] += 1
        elif line.startswith('#define'):
            line = line.split()
            if len(line) != 2:
                raise CompilationError('invalid define syntax')
            _, name = line
            if name in defines:
                raise CompilationError('redefine a macro')
            content = []
            bad_line = f'{name}!'
            while lines:
                n = lines.popleft()
                if n == '#enddefine':
                    break
                elif n == bad_line:
                    raise CompilationError('not able to call macro in thisself')
                content.append(n)
            defines[name] = list(reversed(content))
            defines_count[name] = 0
        elif line == '#enddefine':
            raise CompilationError('enddefine without define')
        elif line.endswith(':'):
            label = line[:-1]
            if len(label.split()) != 1:
                raise CompilationError('invalid label name format')
            if label in labels:
                raise CompilationError('redeclare label')
            labels.add(label)
            yield f"{sanitize_label(label)}:"
        else:
            cmd, *args = line.split()
            if cmd == 'push' and len(args) == 1:
                arg = parse_arg(args[0], "push")
                yield f"pushq {arg}"
            elif cmd == 'pop' and len(args) == 1:
                arg = args[0]
                if arg not in registers:
                    raise CompilationError('invalid arg in pop')
                yield f"popq {registers[arg]}"
            elif cmd in ('add', 'sub', 'mov') and len(args) == 2:
                if args[0] not in registers:
                    raise CompilationError(f'invalid arg in {cmd}')
                a = registers[args[0]]
                b = parse_arg(args[1], cmd)
                yield f"{cmd}q {b}, {a}"
            elif cmd == 'mul' and len(args) == 2:
                if args[0] not in registers:
                    raise CompilationError('invalid arg in mul')
                a = registers[args[0]]
                b = parse_arg(args[1], "mul")
                yield f"imulq {b}, {a}"
            elif cmd in ('div', 'mod') and len(args) == 2:
                if args[0] not in registers:
                    raise CompilationError(f'invalid arg in {cmd}')
                a = registers[args[0]]
                b = parse_arg(args[1], cmd)
                yield "mov %%rax, %%r8"
                yield "mov %%rdx, %%r9"
                yield f"mov {a}, %%rax"
                yield "xor %%rdx, %%rdx"
                yield f"mov {b}, %%r10"
                yield "idiv %%r10"
                if cmd == "div":
                    yield "mov %%rax, %%r11"
                elif cmd == "mod":
                    yield "mov %%rdx, %%r11"
                else:
                    assert False
                yield "mov %%r8, %%rax"
                yield "mov %%r9, %%rdx"
                yield f"mov %%r11, {a}"
            elif cmd == 'jmp' and len(args) == 1:
                label = args[0]
                if not (label[0] == label[-1] == '"'):
                    raise CompilationError('invalid label')
                label = label[1:-1]
                used_labels.add(label)
                yield f"jmp {sanitize_label(label)}"
            elif cmd in ('je', 'jl', 'jg') and len(args) == 2:
                arg, label = args
                if arg not in registers:
                    raise CompilationError(f'invalid arg in {cmd}')
                if not (label[0] == label[-1] == '"'):
                    raise CompilationError('invalid label')
                arg = registers[arg]
                label = label[1:-1]
                used_labels.add(label)
                yield f"testq {arg}, {arg}"
                yield f"{cmd} {sanitize_label(label)}"
            else:
                raise CompilationError(f'undefined command {cmd}')
    for label in used_labels:
        if label not in labels:
            raise CompilationError('undefined label')


def generate_c_code(asm_code):
    insns = list(compile_code(asm_code))
    insn_code = "\n".join(f'        "{insn};"' for insn in insns)

    return f"""
#include <stdio.h>
#include <stdlib.h>

unsigned long long stack[4096];

int main(int argc, char **argv) {{
    int stack_size = argc - 1;
    for(int i = 0; i < stack_size; i++) {{
        stack[stack_size - 1 - i] = atoll(argv[1 + i]);
    }}

    asm volatile(
        "mov %%rsp, %%rdi;"

        // Copy onto real stack
        "copy_from:"
        "test %%rcx, %%rcx;"
        "je copied_from;"
        "decq %%rcx;"
        "pushq (%%rsi,%%rcx,8);"
        "jmp copy_from;"
        "copied_from:"

        "xorq %%rax, %%rax;"
        "xorq %%rbx, %%rbx;"
        "xorq %%rcx, %%rcx;"
        "xorq %%rdx, %%rdx;"

{insn_code}

        // Copy from real stack
        "xor %%rcx, %%rcx;"
        "copy_to:"
        "cmp %%rdi, %%rsp;"
        "jae copied_to;"
        "popq (%%rsi,%%rcx,8);"
        "incq %%rcx;"
        "jmp copy_to;"
        "copied_to:"

        "mov %%rdi, %%rsp;"

        : "+c"(stack_size)
        : "S"(stack)
        : "rax", "rbx", "rdx", "rdi", "memory", "flags"
    );

    for(int i = 0; i < stack_size; i++) {{
        printf("%llu\\n", stack[i]);
    }}
}}
""".lstrip()


def run_code(code, input):
    try:
        c_code = generate_c_code(code)
    except CompilationError as e:
        return "Error while compiling code:\n" + str(e)

    result = subprocess.run([
        "gcc",
        "-x", "c",
        "-g",
        "-o", "/tmp/a.out",
        "-Xlinker", "-rpath=" + os.path.dirname(os.path.abspath(__file__)),
        "-"
    ], input=c_code.encode(), capture_output=True)
    if result.returncode != 0:
        text = "Compilation failed:\n\n"
        text += result.stdout.decode(errors="backslashreplace")
        text += result.stderr.decode(errors="backslashreplace")
        return text

    try:
        result = subprocess.run(["/tmp/a.out"] + [str(n) for n in input], capture_output=True, timeout=1)
    except subprocess.TimeoutExpired:
        return "Time limit exceeded"

    text = result.stdout.decode(errors="backslashreplace")
    if result.stderr:
        text += "\n\nStderr:\n" + result.stderr.decode(errors="backslashreplace")
    if result.returncode != 0:
        text += f"\n\nExit code: {result.returncode}"
    return text


if __name__ == '__main__':
    code = sys.stdin.read()
    print(run_code(code, [int(x) for x in sys.argv[1:]]))
