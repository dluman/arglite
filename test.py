from arglite import parser as cliarg

class Test:

    def __init__(self, code):
        print(code)

def main():
    code = cliarg.code
    t = Test(code)

if __name__ == "__main__":
    main()
