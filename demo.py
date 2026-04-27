from reasonflow import trace

@trace
def solve(task):
    return f"solved: {task}"

solve("design a login system")
