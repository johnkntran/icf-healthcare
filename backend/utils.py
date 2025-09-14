import os


def write_temp_tokens(tokens: int) -> None:
    with open('temp_token_file.txt', 'w') as g:
        g.write(str(tokens))


def read_temp_tokens() -> int:
    with open('temp_token_file.txt', 'r') as f:
        tokens = f.read()
    os.remove('temp_token_file.txt')
    return int(tokens.strip())