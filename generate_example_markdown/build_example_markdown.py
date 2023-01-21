from pathlib import Path
from subprocess import run

def main():

    file_list = list(Path("./example_files").glob("*.py"))

    file_list = sorted(file_list)

    with open("compiled_examples.md","w") as f:

        for example_file in file_list:
            print(example_file)
            
            name, description, code = read_file_into_string(example_file)
            output = run_file_and_collect_output_as_string(example_file)

            f.write(f"## {name}\n")
            f.write(f"{description}\n")
            f.write("```python\n")
            f.write(code)
            f.write("\n")
            f.write("```\n")
            
            f.write("```shell\n")
            f.write(output)
            f.write("```\n")


def read_file_into_string(file_path):
    name = file_path.stem
    description = ""
    code = ""
    with open(file_path) as f:
        
        comment_lines = read_comment_lines(f)

        if len(comment_lines) >= 1:
            name = comment_lines[0]

        if len(comment_lines) >= 2:
            description = "\n".join(comment_lines[1:])
            
        code = f.read()

    return name, description, code

def read_comment_lines(f):
    last_position = f.tell()
    comment_lines = []
    try:
        while True:
            line = f.readline()

            if line[0] == "#":
                comment_lines.append( line[1:].strip() )
                last_position = f.tell()
                continue

            break
    finally:
        f.seek(last_position)
    return comment_lines



def get_first_char_in_string(line):
    if len(line)>0:
        return line[0]
    else:
        return ""

def run_file_and_collect_output_as_string(file_path):
    completed_process = run(
        ["python",str(file_path)]
        ,capture_output=True
    )
    return completed_process.stdout.decode("utf-8")

if __name__ == "__main__":
    main()