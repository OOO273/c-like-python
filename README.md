# c-like-python (.cpy)

## 1. Language specification

This project modifies Python to make it look more like C: it uses `{`, `}` and `;`
instead of indentation to express the structure of the code. Everything else stays
the same as Python.

Rules:

- A newline is equivalent to a space.
- `;` represents a newline; any spaces or newlines that follow it are deleted.
- `{` increases the indent count by 1; the space before the indent is filled with spaces.
- `}` decreases the indent count by 1.
- So that the characters `;`, `{`, `}` can still be used literally in a program
  (without meaning newline / increase indent / decrease indent), the following escapes are defined:
  - `${`  means the character `{`
  - `$}`  means the character `}`
  - `$;`  means the character `;`
  - `$$`  means the character `$`

Combining the rules above with Python's own rules forms a language called
**c-like-python**, whose file extension is `cpy`.

We write a program that can run c-like-python directly. Because that would be a lot
of code, instead we provide a program that converts c-like-python into ordinary
Python, then runs the converted Python program. The converter is named `cpy.py`.

Suppose a c-like-python file `abc.cpy` needs to be converted. Run:

```
python cpy.py abc.cpy
```

By default the generated file is placed in the same folder as `abc.cpy`, named `abc.py`.
(The name is just an example — any name works, e.g. `aaa.cpy` produces `aaa.py`.)

## 2. How cpy.py works

The core logic of `cpy.py` is as follows.

To handle indentation correctly, the conversion keeps a **"line-start state"**:

- The program begins in line-start state (so spaces and newlines at the start of the file are swallowed).
- After emitting a newline for an ordinary `;`, it re-enters line-start state.
- While in line-start state, spaces, newlines, `{` and `}` are not output directly
  (`{` and `}` still adjust the indent count), until the first real output character
  appears (an ordinary character, or a character produced by a `$` escape):
  at that point it first pads `indent_count × 4` spaces, then outputs the character,
  and leaves line-start state.
- "newline → space" only applies when NOT at line start (continuation within a line),
  to join an expression spanning multiple physical lines into one line.

Step by step:

- Start: set indent count to 0, enter line-start state (spaces/newlines at the file start are swallowed).
- `${`  → output `{` (real character; if at line start, pad indent first)
- `$}`  → output `}` (real character; if at line start, pad indent first)
- `$;`  → output `;` (real character; if at line start, pad indent first)
- `$$`  → output `$` (real character; if at line start, pad indent first)
- ordinary `{` → delete it, indent count + 1 (no character output)
- ordinary `}` → delete it, indent count − 1 (no character output)
- ordinary `;` → output a newline, enter line-start state (thus swallowing following
  newlines, spaces, `{`, `}`); the next line starts at the indent position, padded with spaces before it
- ordinary newline → line-start state: ignore; otherwise: output a single space
- ordinary space → line-start state: ignore; otherwise: output as-is
- anything else → real character: if at line start, pad `indent_count × 4` spaces then output; otherwise output as-is

Each level of indentation is 4 spaces.

Note: the converter does not recognize strings, dicts/sets/f-strings, or comments.
Any `;`, `{`, `}`, `$` appearing inside them must be escaped as `$;`, `${`, `$}`, `$$`.
A comment must also end with a real `;` to break the line (it cannot rely on a physical
newline, otherwise the next line would be merged into the comment by "newline → space").
Empty code blocks must have `pass` written by the programmer.

---

# c-like-python（.cpy）

## 1、语言规定

希望更改python，让其类似c语言，用 `{`、`}` 和 `;` 代替缩进来表示代码之间的关系，
但其它与python一致。

规定如下：

- 换行等同于空格
- `;` 代表换行，且如果之后有空格或者换行，删除它们
- `{` 代表缩进计数加1，缩进之前的位置用空格填充
- `}` 代表缩进计数减1
- 同时为了程序中能使用 `;`、`{`、`}` 字符，而让其不代表换行、增加缩进、减少缩进，规定：
  - `${`  代表 `{` 字符
  - `$}`  代表 `}` 字符
  - `$;`  代表 `;` 字符
  - `$$`  代表 `$` 字符

由上面的规定结合python的规定，形成了一个 c-like-python 语言，规定这个语言的扩展名为 cpy。

编写一个能直接运行 c-like-python 语言的程序，代码量很大，下面提供了一个将其转换为普通
python 的程序，让其先转换为 python，然后运行转换后的 python 程序。转换程序名字为 `cpy.py`。

假如一个 c-like-python 语言编写的 `abc.cpy` 需要转换，运行命令如下：

```
python cpy.py abc.cpy
```

默认生成的文件放置在 `abc.cpy` 相同文件夹下，名字为 `abc.py`。
（`abc` 只是举例——任意名字均可，例如 `aaa.cpy` 生成 `aaa.py`。）

## 2、cpy.py实现

cpy.py 的核心逻辑如下：

为了正确处理缩进，转换过程维护一个“行首状态”：

- 程序开始即处于行首状态（于是文件开头的空格和换行会被吞掉）；
- 遇到普通 `;` 输出换行后，重新进入行首状态。
- 行首状态下，遇到的空格、换行、`{`、`}` 都不直接输出（`{`、`}` 仍然调整缩进计数），
  直到出现第一个真实输出字符（普通字符，或 `$` 转义出的字符）为止：
  此时先补 缩进计数×4 个空格，再输出该字符，并退出行首状态。
- “换行→空格”只在非行首（行内续行）时生效，用于把跨物理行的表达式拼成一行。

逐条规则：

- 程序开始，设置缩进计数为0，进入行首状态（文件开头的空格或换行会被吞掉）
- `${`  → 输出 `{`（真实字符，行首则先补缩进）
- `$}`  → 输出 `}`（真实字符，行首则先补缩进）
- `$;`  → 输出 `;`（真实字符，行首则先补缩进）
- `$$`  → 输出 `$`（真实字符，行首则先补缩进）
- 遇到普通 `{` → 删掉，缩进计数+1（不输出字符）
- 遇到普通 `}` → 删掉，缩进计数-1（不输出字符）
- 遇到普通 `;` → 输出换行，进入行首状态（从而吞掉后续换行、空格、`{`、`}`），下一行从缩进位置开始，缩进之前用空格填充
- 遇到普通换行 → 行首状态：忽略；非行首：输出一个空格
- 遇到普通空格 → 行首状态：忽略；非行首：原样输出
- 其余 → 真实字符：行首则先补 缩进计数×4 个空格再输出，否则原样输出

每一级缩进为 4 个空格。

注意：转换器不识别字符串、字典/集合/f-string、注释。出现在它们内部的 `;`、`{`、`}`、`$`
必须用 `$;`、`${`、`$}`、`$$` 转义。注释也需用真实的 `;` 结尾来换行（不能依赖物理换行，
否则下一行会因“换行→空格”被并入注释）。空代码块需由程序员自行写 `pass`。

---

# cpy3.py — alternative converter where `{` also breaks the line

`cpy3.py` is a second converter. The original `cpy.py` is kept unchanged and still
follows the rules in section 2. `cpy3.py` differs from `cpy.py` in exactly **one** rule:
the handling of an ordinary `{`.

- `cpy.py`  : `{` only increases the indent count by 1 (no newline), so a block header
  must be written as `if a:; { ... }`.
- `cpy3.py` : `{` increases the indent count by 1 **and** outputs a newline; **but** if it
  is already at line start (for example, a preceding `;` has just broken the line), it only
  adds indentation and does **not** break the line again, to avoid extra blank lines.

So with `cpy3.py` you can write `if a: { ... }` directly — the `{` produces the newline
after `if a:`. An ordinary `;` always breaks the line (even at line start), because that is
considered an intentional line break by the programmer.

**This rule is backward compatible with the old syntax.** Writing `if a:; { ... }` still
produces the correct result with no extra blank line: after `;` breaks the line we are at
line start, so the following `{` only adds indent and does not break the line again.

**Important rule (must follow):** `}` does **not** end a statement and does **not** break the
line — it only decreases the indent count. Therefore **every statement, including the last one
before a `}`, must end with `;`.** For example `{ a(); b(); }` — the final `b()` must also be
followed by `;`. Otherwise the next statement after `}` would be glued onto the same line.

`}` is unchanged: it only decreases the indent count (no character output, no newline).
All other rules (`;`, escapes `${ $} $; $$`, strings/dicts/comments needing escapes,
4-space indent, `pass` for empty blocks) are identical to `cpy.py`.

Usage is the same:

```
python cpy3.py abc.cpy
```

---

# cpy3.py —— 让 `{` 也换行的另一个转换器

`cpy3.py` 是第二个转换器。原 `cpy.py` 保留不变，仍按第 2 节的规则工作。`cpy3.py` 与
`cpy.py` 的区别**仅有一条**：普通 `{` 的处理。

- `cpy.py`  ：`{` 只把缩进计数加 1（不换行），所以块头必须写成 `if a:; { ... }`。
- `cpy3.py` ：`{` 把缩进计数加 1，**并且换行**；**但**如果此时已处于行首（例如前面的 `;`
  刚刚换过行），就只增加缩进、**不再换行**，以避免产生多余的空白行。

因此用 `cpy3.py` 可以直接写 `if a: { ... }`——由 `{` 产生 `if a:` 之后的换行。而普通 `;`
必然换行（即使在行首），因为认为这是程序员有意的换行。

**该规则向后兼容老语法。** 写 `if a:; { ... }` 仍然得到正确结果、且没有多余空行：`;`
换行后已处于行首，于是其后的 `{` 只加缩进、不再换行。

**重要约定（必须遵守）：** `}` **不结束语句**、**也不换行**，它只把缩进计数减 1。因此
**每一条语句（包括 `}` 之前的最后一条）都必须以 `;` 结尾。** 例如 `{ a(); b(); }`——
最后的 `b()` 后面同样要有 `;`。否则 `}` 之后的下一条语句会被拼接到同一行上。

`}` 保持不变：只把缩进计数减 1（不输出字符、不换行）。其余所有规则（`;`、转义
`${ $} $; $$`、字符串/字典/注释需要转义、4 空格缩进、空块写 `pass`）都与 `cpy.py` 相同。

用法相同：

```
python cpy3.py abc.cpy
```
