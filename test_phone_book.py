import contextlib
import subprocess
import os


import pytest

@pytest.fixture
def no_db():
    # Use contextlib.suppress to suppress exceptions when trying to delete the database file
    with contextlib.suppress(Exception):
        os.unlink("directory.db")

def run_cmd(cmd):
    # Split the command into a list of arguments
    cmd = cmd.split()
    # Use subprocess.run instead of Popen to simplify code and handle STDOUT and STDERR automatically
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def test_list_without_db(no_db):
    exit_status, op = run_cmd("./phone_book list")
    assert exit_status == 1
    assert op == "Couldn't open database file: No such file or directory"

def test_search_without_db(no_db):
    exit_status, op = run_cmd("./phone_book search foo")
    assert exit_status == 1
    assert op == "Couldn't open database file: No such file or directory"

def test_delete_without_db(no_db):
    exit_status, op = run_cmd("./phone_book delete foo")
    assert exit_status == 1
    assert op == "Couldn't open database file: No such file or directory"

def test_adding_listing(no_db):
    # Use subprocess.run to simplify code
    subprocess.run(["./phone_book", "add", "john", "1234567890"], check=True)
    subprocess.run(["./phone_book", "add", "jack", "0987654321"], check=True)
    subprocess.run(["./phone_book", "add", "james", "5432167890"], check=True)

    exit_status, op = run_cmd("./phone_book list")
    assert exit_status == 0
    expected = """john                 : 1234567890
jack                 : 0987654321
james                : 5432167890
Total entries :  3"""
    assert (op == expected)

def test_adding_searching_found(no_db):
    subprocess.run(["./phone_book", "add", "john", "1234567890"], check=True)
    subprocess.run(["./phone_book", "add", "jack", "0987654321"], check=True)
    subprocess.run(["./phone_book", "add", "james", "5432167890"], check=True)

    exit_status, op = run_cmd("./phone_book search john")
    assert exit_status == 0
    expected = "1234567890"
    assert (op == expected)

def test_adding_searching_notfound(no_db):
    subprocess.run(["./phone_book", "add", "john", "1234567890"], check=True)
    subprocess.run(["./phone_book", "add", "jack", "0987654321"], check=True)
    subprocess.run(["./phone_book", "add", "james", "5432167890"], check=True)

    exit_status, op = run_cmd("./phone_book search wick")
    assert exit_status == 1
    expected = "no match"
    assert (op == expected)

def test_adding_deleting_nonexistent(no_db):
    subprocess.run(["./phone_book", "add", "john", "1234567890"], check=True)
    subprocess.run(["./phone_book", "add", "jack", "0987654321"], check=True)
    subprocess.run(["./phone_book", "add", "james", "5432167890"], check=True)

    exit_status, op = run_cmd("./phone_book delete wick")
    assert exit_status == 1
    expected = "no match"
    assert (op == expected)

def test_adding_deleting_first_list(no_db):
    subprocess.run(["./phone_book", "add", "john", "1234567890"], check=True)
    subprocess.run(["./phone_book", "add", "jack", "0987654321"], check=True)
    subprocess.run(["./phone_book", "add", "james", "5432167890"], check=True)

    subprocess.run(["./phone_book", "delete", "john"], check=True)
    exit_status, op = run_cmd("./phone_book list")
    assert exit_status == 0
    expected = """jack                 : 0987654321
james                : 5432167890
Total entries :  2"""
    assert (op == expected)

def test_adding_deleting_middle_list(no_db):
    subprocess.run(["./phone_book", "add", "john", "1234567890"], check=True)
    subprocess.run(["./phone_book", "add", "jack", "0987654321"], check=True)
    subprocess.run(["./phone_book", "add", "james", "5432167890"], check=True)

    subprocess.run(["./phone_book", "delete", "jack"], check=True)
    exit_status, op = run_cmd("./phone_book list")
    assert exit_status == 0
    expected = """john                 : 1234567890
james                : 5432167890
Total entries :  2"""
    assert (op == expected)

    
def test_valgrind(no_db):
    subprocess.run(["./phone_book", "add", "john", "1234567890"], check=True)
    subprocess.run(["./phone_book", "add", "jack", "0987654321"], check=True)
    subprocess.run(["./phone_book", "add", "james", "5432167890"], check=True)

    exit_status, op = run_cmd("valgrind ./phone_book list")
    assert "All heap blocks were freed -- no leaks are possible" in op, "Memory is not being properly freed"

    
