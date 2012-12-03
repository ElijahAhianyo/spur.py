import functools
import os

from nose.tools import istest, assert_equal

import spur

def test(func):
    @functools.wraps(func)
    def run_test():
        for shell in _create_shells():
            yield func, shell
            
    def _create_shells():
        return [
            spur.LocalShell(),
            _create_ssh_shell()
        ]
        
    def _create_ssh_shell():
        return spur.SshShell(
            hostname=os.environ.get("TEST_SSH_HOSTNAME", "127.0.0.1"),
            username=os.environ["TEST_SSH_USERNAME"],
            password=os.environ["TEST_SSH_PASSWORD"],
            port=int(os.environ.get("TEST_SSH_PORT"))
        )
        
    return istest(run_test)

@test
def output_of_run_is_stored(shell):
    result = shell.run(["echo", "hello"])
    assert_equal("hello\n", result.output)
    
@test
def output_is_not_truncated_when_not_ending_in_a_newline(shell):
    result = shell.run(["echo", "-n", "hello"])
    assert_equal("hello", result.output)
    
@test
def trailing_newlines_are_not_stripped_from_run_output(shell):
    result = shell.run(["echo", "\n\n"])
    assert_equal("\n\n\n", result.output)

@test
def cwd_of_run_can_be_set(shell):
    result = shell.run(["pwd"], cwd="/")
    assert_equal("/\n", result.output)

@test
def environment_variables_can_be_added_for_run(shell):
    result = shell.run(["sh", "-c", "echo $NAME"], update_env={"NAME": "Bob"})
    assert_equal("Bob\n", result.output)