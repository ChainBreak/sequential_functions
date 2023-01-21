from pathlib import Path
from subprocess import run

def main():

    file_list = list(Path("./example_files").glob("*.py"))

    file_list = sorted(file_list)

    with open("compiled_examples.md","w") as f:

        for example_file in file_list:
            print(example_file)
            file_str = read_file_into_string(example_file)
            output = run_file_and_collect_output_as_string(example_file)

            f.write("## Example\n")
            f.write("```python\n")
            f.write(file_str)
            f.write("\n")
            f.write("```\n")
            
            f.write("```shell\n")
            f.write(output)
            f.write("```\n")


def read_file_into_string(file_path):

    with open(file_path) as f:
        return f.read()

def run_file_and_collect_output_as_string(file_path):
    completed_process = run(
        ["python",str(file_path)]
        ,capture_output=True
    )
    return completed_process.stdout.decode("utf-8")

if __name__ == "__main__":
    main()