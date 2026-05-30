#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cpy.py —— c-like-python (.cpy) 转换并运行器。

用法：
    python cpy.py abc.cpy [args...]

把 abc.cpy 转换成同目录下的 abc.py，然后运行 abc.py。
多余的命令行参数会原样透传给被运行的脚本。

语言规则（见《项目目标.txt》）：
    换行     -> 行内时等同空格，行首时忽略（吞掉）
    ;        -> 换行，并进入行首状态（吞掉其后的空格/换行/{ /}）
    {        -> 缩进计数 +1（不输出字符）
    }        -> 缩进计数 -1（不输出字符）
    ${ $} $; -> 字面量 { } ;
    $$       -> 字面量 $
    其余     -> 原样输出（行首时先补 缩进*4 个空格）
"""

import os
import runpy
import sys

INDENT_UNIT = "    "  # 每一级缩进 4 个空格


def convert(src: str) -> str:
    """把 c-like-python 源码转换成普通 Python 源码。"""
    out = []
    indent = 0
    at_line_start = True  # 文件开头即行首，吞掉前导空白
    i = 0
    n = len(src)

    def emit(ch: str) -> None:
        """输出一个真实字符；若处于行首，先补缩进。"""
        nonlocal at_line_start
        if at_line_start:
            out.append(INDENT_UNIT * indent)
            at_line_start = False
        out.append(ch)

    while i < n:
        ch = src[i]

        # 先做 $ 转义的 2 字符前看
        if ch == "$" and i + 1 < n:
            nxt = src[i + 1]
            if nxt in "{};$":
                emit(nxt)
                i += 2
                continue
            # $ 后跟其它字符：原样输出 $
            emit("$")
            i += 1
            continue
        if ch == "$":  # 文件末尾孤立的 $
            emit("$")
            i += 1
            continue

        if ch == "{":
            indent += 1
            i += 1
            continue
        if ch == "}":
            indent -= 1
            if indent < 0:
                raise ValueError(
                    "缩进计数变为负数：'}' 多于 '{'，请检查花括号是否配对。"
                )
            i += 1
            continue
        if ch == ";":
            out.append("\n")
            at_line_start = True
            i += 1
            continue
        if ch == "\n":
            if not at_line_start:
                out.append(" ")  # 行内换行 -> 空格（拼接续行）
            # 行首状态下忽略换行
            i += 1
            continue
        if ch == " ":
            if not at_line_start:
                out.append(" ")
            # 行首状态下忽略空格
            i += 1
            continue

        # 其余普通字符
        emit(ch)
        i += 1

    if indent != 0:
        raise ValueError(
            "缩进计数结束时不为 0：'{' 多于 '}'，请检查花括号是否配对。"
        )

    result = "".join(out)
    if not result.endswith("\n"):
        result += "\n"
    return result


def main(argv=None) -> int:
    argv = sys.argv if argv is None else argv
    if len(argv) < 2:
        print("用法：python cpy.py abc.cpy [args...]", file=sys.stderr)
        return 2

    src_path = argv[1]
    if not src_path.lower().endswith(".cpy"):
        print(f"错误：输入文件必须以 .cpy 结尾，得到：{src_path}", file=sys.stderr)
        return 2
    if not os.path.isfile(src_path):
        print(f"错误：找不到文件：{src_path}", file=sys.stderr)
        return 2

    with open(src_path, "r", encoding="utf-8") as f:
        src = f.read()

    try:
        py_code = convert(src)
    except ValueError as e:
        print(f"转换失败：{e}", file=sys.stderr)
        return 1

    out_path = os.path.splitext(src_path)[0] + ".py"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(py_code)

    # 转换后运行生成的 .py，把多余参数透传给它
    sys.argv = [out_path] + list(argv[2:])
    runpy.run_path(out_path, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
