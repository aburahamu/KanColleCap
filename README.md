## KanColleCap
艦これのゲーム画面をキャプチャし艦隊や基地航空隊の編成画像を作成するアプリです。

## 前提
- Python 3.10以上をインストールしておいてください
- （任意）Git 2.40以上をインストールしておいてください 

## 使い方
1. このリポジトリを任意のフォルダ内で「git clone」する。またはこのリポジトリをZIPでダウンロードし解凍する
2. build.batをダブルクリックする
3. （成功時）フォルダ「dist」が作成され、そのフォルダ内に「KanColleCap.exe」が出力される
4. KanColleCap.exeを任意のフォルダに移動させる（そのままでも良い）
5. 艦これを起動しておく
6. KanColleCap.exeをダブルクリックする
7. アプリが起動するのでボタン「SetFolder」で保存先のフォルダを選ぶ
8. ゲーム側で編成画面や基地航空隊の画面を表示させる
9. アプリ側で画像を取得したいエリアをクリックする
10. アプリ側でボタン「保存」を押す
11. 保存用フォルダに画像が出力される

## 開発環境
- Windows 11 Pro 24H2
- Ryzen 5900X
- GeForce RTX 4080
- python 3.10.6
- git 2.43.0.windows.1

## 切り取る領域の変更方法
1. config.jsonを書き換える
2. build.batをダブルクリックしKanColleCap.exeを作成する

⚙️ 設定ファイル（config.json）
{
  "save_dir": "D:/KanColleCap/Screenshots",
  "hensei": {
    "top_point": 0.2,
    "left_point": 0.4,
    "width": 0.55,
    "height": 0.75
  },
  "kichi": {
    "top_point": 0.3,
    "left_point": 0.7,
    "width": 0.25,
    "height": 0.65
  }
}

## ライセンス
AGPL-3.0

## 開発者
[aburahamu](https://twitter.com/aburahamu_aa)