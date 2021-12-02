from click.testing import CliRunner

from meru.command_line import (
    main_cli,
    process_cli,
    register_process,
    start_all,
    start_multiple,
)


def test_main_cli():
    runner = CliRunner()
    result = runner.invoke(main_cli)

    assert result.exit_code == 0


def test_run_multiple_processes_no_argument(mocker):
    runner = CliRunner()
    result = runner.invoke(start_multiple)

    assert result.exit_code == 2
    assert "Missing argument 'PROCESSES...'" in result.output


def test_run_multiple_processes(mocker):
    mocker.patch("meru.command_line.run_process")
    mocker.patch("meru.command_line.AVAILABLE_PROCESSES", {})

    register_process("process1", "x")
    register_process("process2", "y")

    runner = CliRunner()
    result = runner.invoke(start_multiple, ["process1", "process2"])

    assert result.exit_code == 0


def test_run_multiple_processes_single_call(mocker):
    mocker.patch("meru.command_line.run_process")
    mocker.patch("meru.command_line.AVAILABLE_PROCESSES", {})

    register_process("process1", "x")

    runner = CliRunner()
    result = runner.invoke(start_multiple, ["process1"])

    assert result.exit_code == 0


def test_run_multiple_processes_process_not_found(mocker):
    mocker.patch("meru.command_line.run_process")
    mocker.patch("meru.command_line.AVAILABLE_PROCESSES", {})

    runner = CliRunner()
    result = runner.invoke(start_multiple, ["process1"])

    assert result.exit_code == 1
    assert "names are invalid: process1" in result.output


def test_run_all(mocker):
    mocker.patch("meru.command_line.run_process")
    mocker.patch("meru.command_line.AVAILABLE_PROCESSES", {})

    register_process("process1", "x")

    runner = CliRunner()
    result = runner.invoke(start_all)

    assert result.exit_code == 0


def test_register_process(mocker):
    registered_processes = mocker.patch("meru.command_line.AVAILABLE_PROCESSES", {})
    runner = CliRunner()

    register_process("process_name", "x.x.x.x")
    assert registered_processes == {"process_name": "x.x.x.x"}

    result = runner.invoke(process_cli)

    assert result.exit_code == 0
    assert "process_name" in result.output
