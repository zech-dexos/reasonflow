from reasonflow import trace


@trace
def ask_ai(prompt):
    return f"AI response to: {prompt}"


if __name__ == "__main__":
    ask_ai("how do I design a login system?")
