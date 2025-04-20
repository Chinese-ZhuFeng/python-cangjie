import re
class f:
    def __init__(self):
        self.import_statements = []
        self.main_code = []
        self.rules = [
            (r"^import (\w+)$", self._capture_import),
            (r"^([A-Z_]+) = \d+$", self._wrap_main_declaration),
            (r"^n = 0$", "var n: UInt32 = 0"),
            (r"for _ in range\((\w+)\):", r"for (__ in 0..\1) {"),
            (r"random\.random\(\)", "random.nextFloat64()"),
            (r"math\.pi", "Float64.PI"),
            (r"(\b[nN]\b)(\s*[/\*])", r"Float64(\1)\2"),
            (r'print\(f"([^{"]*)\{(\w+)\}([^{"]*)"\)',r'println("\1${\2}\3")'),
            (r"\bN\b", "a"),  # 新增变量替换规则
            (r"\bn\b", "b"),
            (r"\bpi\b", "c"),
            (r"\bmath\.pi\b", "Float64.PI")
        ]


    def _capture_import(self, match) -> str:
        lib = match.group(1)
        self.import_statements.append(f"from std import {lib}.*;")
        return None
    def _wrap_main_declaration(self, match) -> str:
        var_name = match.group(1)
        return f"    const {var_name} = {var_name}"
    def translate(self, python_code: str) -> str:
        lines = [ln.strip() for ln in python_code.split('\n') if ln.strip()]
        for line in lines:
            processed = False
            for pattern, replacement in self.rules:
                if callable(replacement):
                    match = re.match(pattern, line)
                    if match:
                        result = replacement(match)
                        if result is None:
                            processed = True
                            break
                        else:
                            self.main_code.append(result)
                            processed = True
                            break
                else:
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        self.main_code.append(new_line)
                        processed = True
                        break
            if not processed:
                self.main_code.append(line)
        cangjie_code = []
        cangjie_code.extend(self.import_statements)
        cangjie_code.append("main() {")
        if any("random.nextFloat64()" in ln for ln in self.main_code):
            cangjie_code.append("    let random = Random()")
        cangjie_code.extend([f"    {ln}" for ln in self.main_code
                             if not re.match(r"^from std", ln)])
        cangjie_code.append("}")
        cangjie_code.append("}")
        code = []
        level = 0
        for line in cangjie_code:
            if line.endswith("{"):
                code.append("    " * level + line)
                level += 1
            elif line.startswith("}"):
                level -= 1
                code.append("    " * level + line)
            else:
                code.append("    " * level + line)

        return "\n".join(code)


# 使用示例
if __name__ == "__main__":
    s = """
import random
import math

N = 100000
n = 0

for _ in range(N):
    x = random.random()
    y = random.random
    if (x - 0.5)**2 + (y - 0.5)**2 < 0.25:
        n += 1

pi = n / N * 4.0
print(f"deviation: {abs(math.pi - pi)}")
print(f"π = {pi}")

    """
    translator = f()
    print(translator.translate(s))
