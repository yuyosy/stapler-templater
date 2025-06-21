import argparse
import sys
from pathlib import Path

from src.args import Argument, set_parser


def test_argument_defaults():
    arg = Argument()
    assert arg.config == Path("config.yaml")
    assert arg.input is None
    assert arg.recipes is None
    assert arg.presets is None
    assert arg.verbose is False


def test_argument_custom():
    arg = Argument(
        config=Path("foo.yaml"),
        input=Path("in.txt"),
        recipes=["a"],
        presets=["b"],
        verbose=True,
    )
    assert arg.config == Path("foo.yaml")
    assert arg.input == Path("in.txt")
    assert arg.recipes == ["a"]
    assert arg.presets == ["b"]
    assert arg.verbose is True


def test_set_parser_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog"])
    parser, args = set_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    assert isinstance(args, Argument)
    assert args.config == Path("config.yaml")
    assert args.input is None
    assert args.recipes is None
    assert args.presets is None
    assert args.verbose is False


def test_set_parser_all_args(monkeypatch):
    argv = [
        "prog",
        "-c",
        "myconf.yaml",
        "-i",
        "input.txt",
        "-r",
        "rec1",
        "rec2",
        "-p",
        "pre1",
        "pre2",
        "--verbose",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    _, args = set_parser()
    assert args.config == Path("myconf.yaml")
    assert args.input == Path("input.txt")
    assert args.recipes == ["rec1", "rec2"]
    assert args.presets == ["pre1", "pre2"]
    assert args.verbose is True
