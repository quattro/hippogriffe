import pathlib
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from hippogriffe._extension import (
    HippogriffeExtension,
    _PublicApi,
    _collect_bases,
    _resolved_bases,
)


class _HashableNamespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __hash__(self):
        return id(self)


def test_extension_exposes_griffe_v2_package_hook():
    assert "on_package" in HippogriffeExtension.__dict__


def test_extra_public_objects_support_nested_module_paths():
    pkg = _HashableNamespace(path="dummy", all_members={})

    public_api = _PublicApi(
        pkg=pkg,
        top_level_public_api=set(),
        builtin_modules=[],
        extra_public_objects=["importlib.metadata.EntryPoint"],
    )

    public_path, autoref = public_api["importlib.metadata.EntryPoint"]
    assert public_path == "importlib.metadata.EntryPoint"
    assert autoref is False


def test_extra_public_objects_do_not_record_duplicate_public_paths():
    pkg = _HashableNamespace(path="dummy", all_members={})

    public_api = _PublicApi(
        pkg=pkg,
        top_level_public_api=set(),
        builtin_modules=[],
        extra_public_objects=["xml.etree.ElementTree.Element"],
    )

    public_path, autoref = public_api["xml.etree.ElementTree.Element"]
    assert public_path == "xml.etree.ElementTree.Element"
    assert autoref is False


def test_resolved_bases_prefers_griffe_resolved_bases_property():
    resolved_base = _HashableNamespace(path="scipy.sparse.linalg.LinearOperator")
    cls = _HashableNamespace(
        resolved_bases=[resolved_base],
        bases=["builtins.object"],
        modules_collection={},
    )

    bases = _resolved_bases(cls)

    assert bases == [resolved_base, "object"]


def test_collect_bases_resolves_external_import_paths():
    pkg = _HashableNamespace(path="dummy", all_members={})
    public_api = _PublicApi(
        pkg=pkg,
        top_level_public_api=set(),
        builtin_modules=[],
        extra_public_objects=["xml.etree.ElementTree.Element"],
    )
    cls = _HashableNamespace(
        resolved_bases=[],
        bases=["xml.etree.ElementTree.Element"],
        modules_collection={},
    )

    bases = _collect_bases(cls, public_api)

    assert bases == {"xml.etree.ElementTree.Element": False}
