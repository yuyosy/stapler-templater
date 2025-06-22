# stapler-templater


## Config
```yaml
version: "1.0" # バージョン情報
name: default # 名前
recipes: # レシピ設定
    - enabled: true # 有効/無効 (省略可能; default=true)
        id: "" # レシピID
        name: "" # レシピ名
        input: # 入力設定
            file_pattern: "" # 入力ファイルのパターン
        output: # 出力設定
            path: "" # 出力ファイルのパス
            encoding: utf-8 # 出力ファイルのエンコーディング (省略可能; default=utf-8)
            write_mode: w # 書き込みモード (省略可能; choice=w|a; default=w)
        template: # テンプレート設定
            folder: "" # テンプレートフォルダ
            file: "" # テンプレートファイル名
            encoding: utf-8 # テンプレートのエンコーディング (省略可能; default=utf-8)
        read_content: # 読み込み設定
            start: # 読み込み開始位置 (省略可能)
                extract_type: auto # 抽出タイプ (省略可能; choice=auto|index|line|exact|regex; default=auto)
                target: "" # 抽出対象 (型: str|int)
                include_match: true # 抽出結果に一致部分を含めるか (省略可能; default=true)
            end: # 読み込み終了位置 (省略可能)
                extract_type: auto # 抽出タイプ (省略可能; choice=auto|index|line|exact|regex; default=auto)
                target: "" # 抽出対象 (型: str|int)
                include_match: true # 抽出結果に一致部分を含めるか (省略可能; default=true)
            encoding: utf-8 # 読み込みエンコーディング (省略可能; default=utf-8)
        parse: # パース設定
            parse_type: plain # パースタイプ (choice=plain|json|yaml|xml|dsv|textfsm)
            parse_result_name: parse_result # パース結果の名前 (省略可能; default=parse_result)
            json_options: {} # JSONオプション (省略可能; 現状オプションなし)
            yaml_options: {} # YAMLオプション (省略可能; 現状オプションなし)
            xml_options: # XMLオプション (省略可能)
                attribute_key: "@{key}" # XML属性キー (省略可能; default=@{key})
                text_key: "#text" # XMLテキストキー (省略可能; default=#text)
            dsv_options: # DSVオプション (省略可能)
                parse_type: dict # DSVパースタイプ (省略可能; choice=list|dict; default=dict)
                enable_header: true # ヘッダーを有効にするか (省略可能; default=true)
                delimiter: "\t" # 区切り文字 (省略可能; default=\t)
                skip_empty_lines: true # 空行をスキップするか (省略可能; default=true)
                comment_line: "" # コメント行の識別文字 (省略可能)
            textfsm_options: # TextFSMオプション (省略可能)
                parse_type: dict # TextFSMパースタイプ (省略可能; choice=list|dict; default=dict)
                enable_header: true # ヘッダーを有効にするか (省略可能; default=true)
                template: "" # TextFSMテンプレートファイル
                encoding: utf-8 # テンプレートエンコーディング (省略可能; default=utf-8)
        variables: # 変数設定
            presets_overwrite: # プリセット変数のオプション上書き
                '': # 変数名 (choice=fileName|fileExt|filePath|parentName|parentPath|templateName|templateFolder)
                    path_separator: '' # パス区切り文字 (省略可能; local|posix; default=posix)
            defined: # 変数定義
                '': # 変数名
                    target: '' # 対象 (choice=filename|filepath|content)
                    path_separator: '' # パス区切り文字 (省略可能; local|posix; default=posix)
                    pattern: '' # パターン (正規表現; 省略可能)
                    match_index: '' # マッチインデックス or パターン名 (省略可能; default=0)
        additional_params: # 追加パラメータ (str|dict)
            '': '' # パラメータ名: 値
            '': # パラメータ名
                value: '' # パラメータ値
presets: # プリセット設定
    - enabled: true # 有効/無効 (省略可能; default=true)
        id: "" # プリセットID
        name: "" # プリセット名
        recipes:
            - recipe: "" # レシピID
                enabled: true # 有効/無効 (省略可能; default=true)
```

### 定義済みのプリセット変数一覧
    - fileName: ファイル名
    - fileExt: ファイル拡張子
    - filePath: ファイルパス
    - parentName: 親フォルダ名
    - parentPath: 親フォルダパス
    - templateName: テンプレート名
    - templateFolder: テンプレートフォルダ


## License
MIT License Copyright (c) 2025 yuyosy
