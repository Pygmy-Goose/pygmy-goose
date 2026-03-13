#!/usr/bin/env python3

import os
import subprocess
import sys
import argparse
import concurrent.futures
import difflib
import re
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from format_test_benchmark import format_file_content

try:
    ver = subprocess.check_output(("black", "--version"), text=True)
    if int(ver.split(" ")[1].split(".")[0]) < 26:
        print('you need to run `uv pip install "black>=26"`', ver)
        if "DUCKDB_FORMAT_SKIP_VERSION_CHECKS" not in os.environ:
            exit(-1)
except Exception as e:
    print('you need to run `uv pip install "black>=26"`', e)
    exit(-1)

try:
    ver = subprocess.check_output(("clang-format", "--version"), text=True)
    if "20." not in ver:
        print("you need to run `uv pip install clang_format==20.1.7 - `", ver)
        if "DUCKDB_FORMAT_SKIP_VERSION_CHECKS" not in os.environ:
            exit(-1)
except Exception as e:
    print("you need to run `uv pip install clang_format==20.1.7 - `", e)
    exit(-1)

try:
    subprocess.check_output(("cmake-format", "--version"), text=True)
except Exception as e:
    print("you need to run `uv pip install cmake-format`", e)
    exit(-1)

EXTENSIONS = [
    ".cpp",
    ".ipp",
    ".c",
    ".hpp",
    ".h",
    ".cc",
    ".hh",
    "CMakeLists.txt",
    ".test",
    ".test_slow",
    ".test_coverage",
    ".benchmark",
    ".py",
    ".java",
]
FORMATTED_DIRECTORIES = ["src", "test", "tools", "scripts"]
IGNORED_FILES = [
    "tpch_constants.hpp",
    "tpcds_constants.hpp",
    "_generated",
    "test_csv_header.hpp",
    "duckdb.cpp",
    "duckdb.hpp",
    "json.hpp",
    "sqlite3.h",
    "shell.c",
    "termcolor.hpp",
    "test_insert_invalid.test",
    "httplib.hpp",
    "os_win.c",
    "glob.c",
    "printf.c",
    "helper.hpp",
    "single_thread_ptr.hpp",
    "types.hpp",
    "default_views.cpp",
    "default_functions.cpp",
    "release.h",
    "genrand.cpp",
    "address.cpp",
    "visualizer_constants.hpp",
    "icu-collate.cpp",
    "icu-collate.hpp",
    "yyjson.cpp",
    "yyjson.hpp",
    "duckdb_pdqsort.hpp",
    "pdqsort.h",
    "stubdata.cpp",
    "nf_calendar.cpp",
    "nf_calendar.h",
    "nf_localedata.cpp",
    "nf_localedata.h",
    "nf_zformat.cpp",
    "nf_zformat.h",
    "expr.cc",
    "function_list.cpp",
    "inlined_grammar.hpp",
]
IGNORED_DIRECTORIES = [
    ".eggs",
    "__pycache__",
    "dbgen",
    os.path.join("tools", "rpkg", "src", "duckdb"),
    os.path.join("tools", "rpkg", "inst", "include", "cpp11"),
    os.path.join("extension", "tpcds", "dsdgen"),
    os.path.join("extension", "jemalloc", "jemalloc"),
    os.path.join("extension", "icu", "third_party"),
    os.path.join("tools", "nodejs", "src", "duckdb"),
]
IGNORED_EXTENSIONS = []

CLANG_FORMAT = ["clang-format", "--sort-includes=0", "-style=file"]
BLACK_FORMAT = ["black", "-q", "--skip-string-normalization", "--line-length", "120"]
CMAKE_FORMAT = ["cmake-format"]
TEST_FORMAT = ["./scripts/format_test_benchmark.py"]

FORMAT_COMMANDS = {
    ".cpp": CLANG_FORMAT,
    ".ipp": CLANG_FORMAT,
    ".c": CLANG_FORMAT,
    ".hpp": CLANG_FORMAT,
    ".h": CLANG_FORMAT,
    ".hh": CLANG_FORMAT,
    ".cc": CLANG_FORMAT,
    ".txt": CMAKE_FORMAT,
    ".py": BLACK_FORMAT,
    ".java": CLANG_FORMAT,
    ".test": TEST_FORMAT,
    ".test_slow": TEST_FORMAT,
    ".test_coverage": TEST_FORMAT,
    ".benchmark": TEST_FORMAT,
}

header_top = "//===----------------------------------------------------------------------===//\n"
header_top += "//                         DuckDB\n" + "//\n"
header_bottom = "//\n" + "//\n"
header_bottom += "//===----------------------------------------------------------------------===//\n\n"
base_dir = os.path.join(os.getcwd(), "src/include")


def parse_args():
    parser = argparse.ArgumentParser(prog="python scripts/format.py", description="Format source directory files")
    parser.add_argument(
        "revision",
        nargs="?",
        default="HEAD",
        help="Revision number or --all to format all files (default: HEAD)",
    )
    parser.add_argument("--check", action="store_true", help="Only print differences (default)")
    parser.add_argument("--fix", action="store_true", help="Fix the files")
    parser.add_argument("-a", "--all", action="store_true", help="Format all files")
    parser.add_argument(
        "-d",
        "--directories",
        nargs="*",
        default=[],
        help="Format specified directories",
    )
    parser.add_argument("-y", "--noconfirm", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("-q", "--silent", action="store_true", help="Suppress output")
    parser.add_argument("-f", "--force", action="store_true", help="Force formatting")
    return parser.parse_args()


def file_is_ignored(full_path):
    if os.path.basename(full_path) in IGNORED_FILES:
        return True
    dirnames = os.path.sep.join(full_path.split(os.path.sep)[:-1])
    for ignored_directory in IGNORED_DIRECTORIES:
        if ignored_directory in dirnames:
            return True
    return False


def can_format_file(full_path):
    if not os.path.isfile(full_path):
        return False
    full_path.split(os.path.sep)[-1]
    found = False
    for ext in EXTENSIONS:
        if full_path.endswith(ext):
            found = True
            break
    if not found:
        return False
    if file_is_ignored(full_path):
        return False
    for dname in FORMATTED_DIRECTORIES:
        if full_path.startswith(dname):
            return True
    return False


def get_changed_files(revision):
    proc = subprocess.Popen(["git", "diff", "--name-only", revision], stdout=subprocess.PIPE)
    files = proc.stdout.read().decode("utf8").split("\n")
    changed_files = []
    for f in files:
        if not can_format_file(f):
            continue
        if file_is_ignored(f):
            continue
        changed_files.append(f)
    return changed_files


def format_directory(directory):
    files = os.listdir(directory)
    files.sort()
    result = []
    for f in files:
        full_path = os.path.join(directory, f)
        if os.path.isdir(full_path):
            if f in IGNORED_DIRECTORIES or full_path in IGNORED_DIRECTORIES:
                continue
            result += format_directory(full_path)
        elif can_format_file(full_path):
            result += [full_path]
    return result


def file_is_generated(text):
    if "// This file is automatically generated by scripts/" in text:
        return True
    return False


def format_file(full_path, check_only, force, silent):
    ext = "." + full_path.split(".")[-1] if "." in full_path.split("/")[-1] else ""
    if ext in IGNORED_EXTENSIONS:
        return
    if ext not in FORMAT_COMMANDS:
        return
    if not silent:
        print(full_path)

    with open(full_path, "r", encoding="utf-8") as f:
        original = f.read()

    if file_is_generated(original) and ext != ".py":
        return

    if check_only:
        cmd = None
        if ext in (".test", ".test_slow", ".test_coverage", ".benchmark"):
            with open(full_path, "r", encoding="utf-8") as f:
                original_lines = f.readlines()
            formatted, status = format_file_content(full_path, original_lines)
            if formatted is None:
                print(f"Failed to format {full_path}: {status}")
                sys.exit(1)
            stderr = ""
        elif ext == ".py":
            cmd = FORMAT_COMMANDS[ext] + ["-", "--stdin-filename", full_path]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            formatted, stderr = process.communicate(input=original)
            formatted = formatted or ""
        else:
            cmd = FORMAT_COMMANDS[ext] + [full_path]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            formatted, stderr = process.communicate()
            formatted = formatted or ""
        if cmd and stderr:
            print(os.getcwd())
            print("Failed to format file " + full_path)
            print(" ".join(cmd))
            print(stderr)
            sys.exit(1)
            stderr = ""
        elif ext == ".py":
            cmd = FORMAT_COMMANDS[ext] + ["-", "--stdin-filename", full_path]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            formatted, stderr = process.communicate(input=original)
        else:
            cmd = FORMAT_COMMANDS[ext] + [full_path]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            formatted, stderr = process.communicate()
        if stderr:
            print(os.getcwd())
            print("Failed to format file " + full_path)
            print(" ".join(cmd))
            print(stderr)
            sys.exit(1)
        formatted = formatted.replace("\r", "")
        formatted = re.sub(r"\n*$", "", formatted)
        formatted += "\n"

        if ext == ".hpp" and full_path.startswith("src/include"):
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            header_middle = "// " + os.path.relpath(full_path, base_dir) + "\n"
            text = header_top + header_middle + header_bottom
            is_old_header = True
            for line in lines:
                if not (line.startswith("//") or line.startswith("\n")) and is_old_header:
                    is_old_header = False
                if not is_old_header:
                    text += line
            formatted = text

        if full_path.endswith("list.hpp"):
            file_list = [
                os.path.join(dp, f)
                for dp, dn, filenames in os.walk("src/include")
                for f in filenames
                if os.path.splitext(f)[1] == ".hpp" and not f.endswith("list.hpp")
            ]
            file_list = [x.replace("src/include/", "") for x in file_list]
            file_list.sort()
            result = ""
            for x in file_list:
                result += '#include "%s"\n' % (x)
            formatted = result

        if ext in (".cpp", ".hpp"):
            formatted = formatted.replace("ARGS &&...args", "ARGS &&... args")

        if original != formatted:
            print("----------------------------------------")
            print("----------------------------------------")
            print("Found differences in file " + full_path)
            print("----------------------------------------")
            print("----------------------------------------")
            diff_result = difflib.unified_diff(original.split("\n"), formatted.split("\n"))
            total_diff = ""
            for diff_line in diff_result:
                total_diff += diff_line + "\n"
            total_diff = total_diff.strip()
            print(total_diff)
            return full_path
    else:
        if ext in (".test", ".test_slow", ".test_coverage", ".benchmark"):
            with open(full_path, "r", encoding="utf-8") as f:
                original_lines = f.readlines()
            formatted, status = format_file_content(full_path, original_lines)
            if formatted is None:
                print(f"Failed to format {full_path}: {status}")
                sys.exit(1)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(formatted)
        else:
            if ext == ".py":
                cmd = FORMAT_COMMANDS[ext] + [full_path]
            else:
                cmd = FORMAT_COMMANDS[ext] + ["-i", full_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stderr:
                print(os.getcwd())
                print("Failed to format file " + full_path)
                print(" ".join(cmd))
                print(result.stderr)
                sys.exit(1)

        if ext == ".hpp" and full_path.startswith("src/include"):
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            header_middle = "// " + os.path.relpath(full_path, base_dir) + "\n"
            text = header_top + header_middle + header_bottom
            is_old_header = True
            for line in lines:
                if not (line.startswith("//") or line.startswith("\n")) and is_old_header:
                    is_old_header = False
                if not is_old_header:
                    text += line

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(text)

        if full_path.endswith("list.hpp"):
            file_list = [
                os.path.join(dp, f)
                for dp, dn, filenames in os.walk("src/include")
                for f in filenames
                if os.path.splitext(f)[1] == ".hpp" and not f.endswith("list.hpp")
            ]
            file_list = [x.replace("src/include/", "") for x in file_list]
            file_list.sort()
            result = ""
            for x in file_list:
                result += '#include "%s"\n' % (x)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(result)

        if ext in (".cpp", ".hpp"):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("ARGS &&...args", "ARGS &&... args")
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)


def main():
    args = parse_args()

    revision = args.revision
    check_only = not args.fix
    confirm = not args.noconfirm
    silent = args.silent
    force = args.force
    format_all = args.all
    formatted_dirs = FORMATTED_DIRECTORIES
    if args.directories:
        formatted_dirs = args.directories

    action = "Formatting"
    if check_only:
        action = "Checking"

    files = []
    if os.path.isfile(revision):
        print(action + " individual file: " + revision)
        files = [revision]
    elif os.path.isdir(revision):
        print(action + " files in directory: " + revision)
        files = [os.path.join(revision, x) for x in os.listdir(revision)]
        print("Changeset:")
        for fname in files:
            print(fname)
    elif not format_all:
        if revision == "main":
            os.system("git fetch origin main:main")
        print(action + " since branch or revision: " + revision)
        files = get_changed_files(revision)
        if len(files) == 0:
            print("No changed files found!")
            exit(0)
        print("Changeset:")
        for fname in files:
            print(fname)
    else:
        print(action + " all files")
        for direct in formatted_dirs:
            files += format_directory(direct)

    if confirm and not check_only:
        print("The files listed above will be reformatted.")
        result = input("Continue with changes (y/n)?\n")
        if result != "y":
            print("Aborting.")
            exit(0)

    difference_files = []

    def process_file(f):
        try:
            result = format_file(f, check_only, force, silent)
            if result:
                difference_files.append(result)
        except Exception:
            print(traceback.format_exc())
            sys.exit(1)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        try:
            threads = [executor.submit(process_file, f) for f in files]
            concurrent.futures.wait(threads)
        except KeyboardInterrupt:
            executor.shutdown(wait=True, cancel_futures=True)
            raise

    if check_only:
        if len(difference_files) > 0:
            print("")
            print("")
            print("")
            print("Failed format-check: differences were found in the following files:")
            for fname in difference_files:
                print("- " + fname)
            print('Run "make format-fix" to fix these differences automatically')
            exit(1)
        else:
            print("Passed format-check")
            exit(0)


if __name__ == "__main__":
    main()
