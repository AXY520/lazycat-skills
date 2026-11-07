"""严格检查普通 YAML；不冒充 Go template/#@build 的运行时验证。"""

from pathlib import Path
import re
import subprocess
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    keys = set()
    for key_node, _ in node.value:
        # 本仓库示例不用 YAML merge；拒绝它，避免隐式覆盖绕过重复键检查。
        if key_node.tag == "tag:yaml.org,2002:merge":
            raise yaml.constructor.ConstructorError("mapping", node.start_mark,
                                                     "不支持隐式 merge", key_node.start_mark)
        key = loader.construct_object(key_node, deep=deep)
        if key in keys:
            raise yaml.constructor.ConstructorError("mapping", node.start_mark,
                                                     f"重复键：{key}", key_node.start_mark)
        keys.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def parse_yaml(text):
    return list(yaml.load_all(text, Loader=UniqueKeyLoader))


class DocumentExamplesTests(unittest.TestCase):
    def test_duplicate_keys_are_rejected(self):
        with self.assertRaises(yaml.constructor.ConstructorError):
            parse_yaml("application: {}\napplication: {}\n")
        with self.assertRaises(yaml.constructor.ConstructorError):
            parse_yaml("services:\n  web:\n    image: alpine\n    image: nginx\n")

    def test_bash_fences_have_valid_syntax(self):
        checked = 0
        documents = sorted((ROOT / "skills").rglob("*.md")) + [ROOT / "README.md"]
        for path in documents:
            for match in re.finditer(r"(?ms)^```(?:bash|sh)\s*\n(.*?)^```\s*$", path.read_text("utf-8")):
                with self.subTest(document=str(path.relative_to(ROOT))):
                    result = subprocess.run(["bash", "-n"], input=match.group(1),
                                            text=True, capture_output=True, timeout=5)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    checked += 1
        self.assertGreater(checked, 15)
        print(f"\nBash 语法：{checked} 个代码片段通过；未执行命令或验证设备状态。")

    def test_app_examples_have_bilingual_metadata_and_no_default_usage(self):
        packages = 0
        manifests = 0
        paths = sorted((ROOT / "skills").rglob("*")) + [ROOT / "README.md"]
        for path in paths:
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".yml"}:
                continue
            text = path.read_text("utf-8")
            regions = []
            is_package_file = path.name in {"package.yml", "package.yaml"}
            if is_package_file or path.name in {"lzc-manifest.yml", "lzc-manifest.yaml"}:
                regions.append((1, text))
            if path.suffix == ".md":
                for match in re.finditer(r"(?ms)^```ya?ml\s*\n(.*?)^```\s*$", text):
                    regions.append((text.count("\n", 0, match.start(1)) + 1, match.group(1)))
            for line, source in regions:
                if "{{" in source or re.search(r"(?m)^\s*#@build\b", source):
                    continue
                for index, value in enumerate(parse_yaml(source)):
                    label = f"{path.relative_to(ROOT)}:{line}"
                    with self.subTest(document=label, yaml_document=index):
                        if is_package_file:
                            self.assertIsInstance(value, dict)
                        if not isinstance(value, dict):
                            continue
                        self.assertNotIn("usage", value, "默认示例不添加 usage")
                        locales = value.get("locales", {})
                        self.assertIsInstance(locales, dict)
                        for locale in locales.values():
                            self.assertIsInstance(locale, dict)
                            self.assertNotIn("usage", locale, "默认示例不添加本地化 usage")
                        if is_package_file or {"package", "version"} <= value.keys():
                            packages += 1
                            for language in ("zh-CN", "en-US"):
                                self.assertIn(language, locales)
                                for field in ("name", "description"):
                                    content = locales[language].get(field)
                                    self.assertIsInstance(content, str, f"{language}.{field}")
                                    self.assertTrue(content.strip(), f"{language}.{field} 不能为空")
                        if "application" in value or path.name.startswith("lzc-manifest."):
                            manifests += 1
        self.assertGreater(packages, 0)
        self.assertGreater(manifests, 0)
        print(f"\n应用示例覆盖：{packages} 个 package、{manifests} 个 manifest（双语元数据与默认 usage 检查）。")

    def test_plain_yaml_and_frontmatter(self):
        checked = 0
        excluded = []
        for path in sorted((ROOT / "skills").rglob("*")):
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".yml"}:
                continue
            text = path.read_text("utf-8")
            regions = []
            if path.suffix in {".yaml", ".yml"}:
                regions.append((1, text))
            if path.name == "SKILL.md":
                front = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
                self.assertIsNotNone(front, str(path))
                value = parse_yaml(front.group(1))[0]
                self.assertIsInstance(value, dict, str(path))
                self.assertEqual(value.get("name"), path.parent.name)
                self.assertIsInstance(value.get("description"), str)
                self.assertTrue(value["description"].strip())
                checked += 1
            for match in re.finditer(r"(?ms)^```ya?ml\s*\n(.*?)^```\s*$", text):
                regions.append((text.count("\n", 0, match.start(1)) + 1, match.group(1)))
            for line, source in regions:
                label = f"{path.relative_to(ROOT)}:{line}"
                if "{{" in source or re.search(r"(?m)^\s*#@build\b", source):
                    excluded.append(label)
                    continue
                with self.subTest(document=label):
                    parse_yaml(source)
                    checked += 1
        self.assertGreater(checked, 30)
        print(f"\n严格 YAML：{checked} 个普通片段/文件/表头；排除 {len(excluded)} 个模板或构建指令片段。")
        for label in excluded:
            print(f"  未做运行时渲染验证：{label}")


if __name__ == "__main__":
    unittest.main()
