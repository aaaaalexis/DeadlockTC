import os
import requests
import json
import re
import fileinput
import sys

# Deadlock（生死僵局）正體中文轉換工具 v1.0
# 遊戲每次更新都要重新跑一次
# 沒特別做除錯 應該也不太會有問題

API_URL = "https://api.zhconvert.org/convert"
ROOT_FOLDER = r"F:\Program Files (x86)\Steam\steamapps\common\Deadlock\game\citadel" # 確認路徑為 "citadel"
CONVERTER = "Taiwan" # 轉換模式
CUSTOM_MODULES = {"Smooth": 1, "EllipsisMark": 1, "Unit": 1, "ProperNoun": 1, "GanToZuo": 1, "QuotationMark": 1, "TengTong": 1, "InternetSlang": 1, "Repeat": 1, "RepeatAutoFix": 1, "Typo": 1, "Computer": 1}
CUSTOM_WORD_LIST = { # 自訂替換詞彙
    "schinese": "tchinese",
    "守望者": "Warden",
    "大和": "Yamato",
    "熾焱": "Infernus",
    "測試英雄": "Test Hero",
    "老七": "Seven",
    "復仇女巫": "Vindicta",
    "灰爪": "Grey Talon",
    "蓋斯特夫人": "Lady Geist",
    "亞伯拉姆斯": "Abrams",
    "靈魅": "Wraith",
    "麥金尼斯": "McGinnis",
    "悖論": "Paradox",
    "奇能博士": "Dynamo",
    "凱爾文": "Kelvin",
    "魔液": "Viscous",
    "暗影": "Haze",
    "哈雷黛": "Holliday",
    "比波普": "Bebop",
    "卡厲可": "Calico",
    "隧底雙煞": "Mo & Krill",
    "西弗": "Shiv",
    "青藤": "Ivy",
    "破壞王": "Wrecker",
    "神鞭": "Lash",
    "阿金駁": "Akimbo",
    "無名氏": "Generic Person",
    "口袋": "Pocket",
    "蜃景": "Mirage",
    "假人靶子": "TargetDummy",
    "禁用": "停用",
    "獲取": "取得",
    "詳情": "詳細資訊",
    "連接": "連線",
    "添加": "增加",
    "紅色貨櫃": "紅色",
    "相關": "情境",
    "應用": "套用",
    "進去": "進攻",
    "訊號": "標記",
    "匹配": "配對",
    "流線型": "常駐啟用",
    "雙擊": "按兩下",
    "重啟": "重新啟動",
}

def convert_text(text):
    payload = {
        'text': text,
        'converter': CONVERTER,
        'modules': json.dumps(CUSTOM_MODULES),
    }
    try:
        response = requests.post(API_URL, data=payload)
        response.raise_for_status()
        return response.json()['data']['text']
    except Exception as e:
        print(f"轉換時發生錯誤：{e}")
        return None

def lang_formatting(text):
    text = re.sub(r'([\u4e00-\u9fff]+)([a-zA-Z0-9]+)', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z0-9]+)([\u4e00-\u9fff]+)', r'\1 \2', text)
    return text

def process_file(file_path):
    if file_path.endswith("_schinese.txt"):
        output_path = file_path.replace("_schinese.txt", "_tchinese.txt")
        
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_text = f.read()
                if len(existing_text) > 10000:
                    print(f"已轉換：{output_path.replace(ROOT_FOLDER, '')}")
                    return

        with open(file_path, 'r', encoding='utf-8') as f:
            simplified_text = f.read()

        print(f"轉換中：{file_path.replace(ROOT_FOLDER, '')}（{len(simplified_text)} 個字元）")

        if traditional_text := convert_text(simplified_text):
            for old_word, new_word in CUSTOM_WORD_LIST.items():
                traditional_text = traditional_text.replace(old_word, new_word)

            # 中英文混排插入空格
            traditional_text = lang_formatting(traditional_text)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(traditional_text)
            print(f"轉換成功。（繁化姬 / https://zhconvert.org/）")
        else:
            print(f"轉換失敗。（繁化姬 / https://zhconvert.org/）")

def search_and_convert(root_folder):
    for root, _, files in os.walk(root_folder):
        for filename in files:
            file_path = os.path.join(root, filename)
            process_file(file_path)

def download_fonts(urls, download_path):
    # 下載字型（獅尾黑體、獅尾喇叭黑體 / max32002）
    os.makedirs(download_path, exist_ok=True)
    for url in urls:
        filename = os.path.join(download_path, url.split('/')[-1])
        if os.path.exists(filename):
            print(f"已下載字型：{filename.replace(ROOT_FOLDER, '')}，略過...")
        else:
            print(f"下載中：{filename.replace(ROOT_FOLDER, '')}")
            response = requests.get(url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"下載字型成功。")
            else:
                print(f"下載字型失敗。")

def update_fonts_config(fonts_conf_path, fontpattern_content, serif_content, sans_content):
    with open(fonts_conf_path, "r") as file:
        file_content = file.read()

    for line in fileinput.input(fonts_conf_path, inplace=True):
        print(line, end='')
        if "<!-- A fontpattern is a font file name, not a font name.  Be aware of filenames across all platforms! -->" in line:
            if fontpattern_content.strip() not in file_content:
                print(fontpattern_content)
                print("載入字型...", file=sys.stderr)
            else:
                print("已載入字型，略過...", file=sys.stderr)
        elif "<!-- SERIF - REAVER -->" in line:
            if serif_content.strip() not in file_content:
                print(serif_content)
                print("設定字型：襯線體...", file=sys.stderr)
            else:
                print("已設定襯線體，略過...", file=sys.stderr)
        elif "<!-- SANS - Radiance -->" in line:
            if sans_content.strip() not in file_content:
                print(sans_content)
                print("設定字型：無襯線體...（", file=sys.stderr)
            else:
                print("已設定無襯線體，略過...", file=sys.stderr)

def update_game_language(root_folder):
    print("設定遊戲語言...")
    for line in fileinput.input(os.path.join(root_folder, "cfg", "boot.vcfg"), inplace=True):
        print(line.replace('english', 'tchinese'), end='')

FONTS_URL = [
    "https://github.com/max32002/swei-bell-sans/raw/refs/heads/master/CJK%20TC/SweiBellSansCJKtc-Light.ttf",
    "https://github.com/max32002/swei-bell-sans/raw/refs/heads/master/CJK%20TC/SweiBellSansCJKtc-Regular.ttf",
    "https://github.com/max32002/swei-bell-sans/raw/refs/heads/master/CJK%20TC/SweiBellSansCJKtc-Medium.ttf",
    "https://github.com/max32002/swei-bell-sans/raw/refs/heads/master/CJK%20TC/SweiBellSansCJKtc-Bold.ttf",
    "https://github.com/max32002/swei-sans/raw/refs/heads/master/CJK%20TC/SweiSansCJKtc-Light.ttf",
    "https://github.com/max32002/swei-sans/raw/refs/heads/master/CJK%20TC/SweiSansCJKtc-Regular.ttf",
    "https://github.com/max32002/swei-sans/raw/refs/heads/master/CJK%20TC/SweiSansCJKtc-Bold.ttf"
]

fontpattern_content = """	<fontpattern>SweiBellSansCJKtc-Light</fontpattern>
	<fontpattern>SweiBellSansCJKtc-Regular</fontpattern>
	<fontpattern>SweiBellSansCJKtc-Medium</fontpattern>
	<fontpattern>SweiBellSansCJKtc-Bold</fontpattern>
	<fontpattern>SweiSansCJKtc-Light</fontpattern>
	<fontpattern>SweiSansCJKtc-Regular</fontpattern>
	<fontpattern>SweiSansCJKtc-Bold</fontpattern>"""
serif_content = """	<match>
		<test name="family">
			<string>Forevs Demo</string>
		</test>
		<test name="lang">
			<string>zh-tw</string>
		</test>
		<edit name="family" mode="assign" binding="strong">
			<string>Swei Bell Sans CJK TC</string>
		</edit>
	</match>
"""
sans_content = """	<match>
        <test name="family">
            <string>Retail Demo</string>
        </test>
        <test name="lang">
            <string>zh-tw</string>
        </test>
        <edit name="family" mode="assign" binding="strong">
            <string>Swei Sans CJK TC</string>
        </edit>
    </match>
"""

FONTS_CONF_PATH = os.path.join(ROOT_FOLDER, "panorama", "fonts", "fonts.conf")

if __name__ == "__main__":
    print(f"Deadlock 正體中文轉換工具 v1.0")
    print(f"遊戲路徑：{ROOT_FOLDER}")
    print()
    print(f"# 轉換遊戲文本")
    print(f"-> 繁化姬 (https://zhconvert.org)")
    search_and_convert(os.path.join(ROOT_FOLDER, "resource", "localization"))
    print()
    print(f"# 下載字型")
    print(f"-> 獅尾黑體 | max32002 (https://github.com/max32002/swei-sans)")
    print(f"-> 獅尾喇叭黑體 | max32002 (https://github.com/max32002/swei-bell-sans)")
    download_fonts(FONTS_URL, os.path.join(ROOT_FOLDER, "panorama", "fonts"))
    print()
    print(f"# 套用字型設定")
    update_fonts_config(FONTS_CONF_PATH, fontpattern_content, serif_content, sans_content)
    print()
    print(f"# 套用語言設定")
    update_game_language(ROOT_FOLDER)