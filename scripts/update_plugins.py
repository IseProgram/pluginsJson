"""plugin.json を、追従元のプラグイン一覧（SOURCES）を上から順に並べた物で作り直す。

追従元が1つでも取れない・JSON として壊れている・空のときは、何も書かずに失敗で終わる。
壊れた一覧を配ると、使う側の Dalamud でプラグインが消えて見えるため。
"""
import json
import sys
import urllib.request
from pathlib import Path

SOURCES = [
    "https://raw.githubusercontent.com/LeonBlade/DalamudPlugins/main/repo.json",
    "https://raw.githubusercontent.com/Aireil/MyDalamudPlugins/master/pluginmaster.json",
]
OUT = Path(__file__).resolve().parent.parent / "plugin.json"


def fetch(url: str) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": "pluginsJson-updater"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    if not isinstance(data, list) or not data:
        raise ValueError(f"プラグインの一覧（空でない配列）になっていない: {url}")
    for entry in data:
        if not isinstance(entry, dict) or not entry.get("InternalName"):
            raise ValueError(f"InternalName の無い項目がある: {url}")
    return data


def main() -> int:
    plugins = []
    for url in SOURCES:
        plugins.extend(fetch(url))

    names = [p["InternalName"] for p in plugins]
    duplicated = sorted({n for n in names if names.count(n) > 1})
    if duplicated:
        raise ValueError(f"同じプラグインが複数の追従元にある: {', '.join(duplicated)}")

    text = json.dumps(plugins, indent=2, ensure_ascii=False) + "\n"
    for p in plugins:
        print(f"{p['InternalName']} {p.get('AssemblyVersion')} (API {p.get('DalamudApiLevel')})")

    current = OUT.read_text(encoding="utf-8").replace("\r\n", "\n") if OUT.exists() else None
    if current == text:
        print("変更なし")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("plugin.json を更新した")
    return 0


if __name__ == "__main__":
    sys.exit(main())
