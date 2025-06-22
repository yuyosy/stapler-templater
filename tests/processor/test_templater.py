import shutil
import tempfile
from pathlib import Path

from src.config import TemplateOption
from src.processor.templater import (
    ip_address,
    ip_interface,
    ip_network,
    is_ip_address,
    is_ip_interface,
    is_ip_network,
    setup_template_environment,
)


def make_template_dir(structure):
    tmpdir = Path(tempfile.mkdtemp())
    for fname, content in structure.items():
        fpath = tmpdir / fname
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
    return tmpdir


def test_setup_template_environment_success():
    structure = {"test.tpl": "Hello {{ name }}"}
    tmpdir = make_template_dir(structure)
    option = TemplateOption(folder=str(tmpdir), file="test.tpl")
    env = setup_template_environment(option)
    assert env is not None
    template = env.get_template("test.tpl")
    assert template.render(name="World") == "Hello World"
    shutil.rmtree(tmpdir)


def test_setup_template_environment_not_exist():
    option = TemplateOption(folder="/not/exist/dir", file="test.tpl")
    env = setup_template_environment(option)
    assert env is None


def test_setup_template_environment_not_dir():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(b"dummy")
        tf.flush()
        option = TemplateOption(folder=tf.name, file="test.tpl")
        env = setup_template_environment(option)
        assert env is None
    Path(tf.name).unlink()


def test_ip_filters():
    # ip_address, ip_network, ip_interface
    assert ip_address("192.0.2.1") == "192.0.2.1"
    assert ip_address("notip") == "notip"
    assert ip_network("192.0.2.0/24") == "192.0.2.0/24"
    assert ip_network("bad") == "bad"
    assert ip_interface("192.0.2.1/24") == "192.0.2.1/24"
    assert ip_interface("bad") == "bad"
    # is_ip_address, is_ip_network, is_ip_interface
    assert is_ip_address("192.0.2.1") is True
    assert is_ip_address("bad") is False
    assert is_ip_network("192.0.2.0/24") is True
    assert is_ip_network("bad") is False
    assert is_ip_interface("192.0.2.1/24") is True
    assert is_ip_interface("bad") is False


def test_jinja_filters_registered():
    structure = {"test.tpl": "{{ '192.0.2.1'|ip_address }}"}
    tmpdir = make_template_dir(structure)
    option = TemplateOption(folder=str(tmpdir), file="test.tpl")
    env = setup_template_environment(option)
    assert env is not None, "Template environment setup failed"
    assert "ip_address" in env.filters
    template = env.get_template("test.tpl")
    assert template.render() == "192.0.2.1"
    shutil.rmtree(tmpdir)
