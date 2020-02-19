# mmgphotos

Google Photos 操作ライブラリ。

## 必要な環境変数

特になし。

## インストール

```(sh)
pip install git+https://github.com/yukkun007/mmgphotos
```

## アップグレード

```(sh)
pip install -U git+https://github.com/yukkun007/mmgphotos
```

## 使い方 (コードからモジュールを利用)

[参照](#モジュールを利用)

## 使い方 (コマンドラインアプリ)

```(sh)
myapp --help
```

## アンインストール

```(sh)
pip uninstall myapp
```

## 開発フロー

### 環境構築

1. プロジェクトディレクトリに仮想環境を作成するために下記環境変数を追加

   - Linux

     ```(sh)
     export PIPENV_VENV_IN_PROJECT=true
     ```

   - Windows

     ```(sh)
     set PIPENV_VENV_IN_PROJECT=true
     ```

1. `pip install pipenv`
1. `git clone git@github.com:yukkun007/mmgphotos.git`
1. `pipenv install --dev`

### install package

下記は編集可能モードでインストールされる。

```(sh)
pip install -e .
```

通常のインストールは下記だがソース編集の都度`upgrade package`が必要なので基本は`-e`をつける。

```(sh)
pip install .
```

### upgrade package

```(sh)
pip install --upgrade . (もしくは-U)
```

## 開発行為

### モジュールを利用

```(python)
$ python
>>> import myapp
>>> myapp.do_something("Foo")
>>> myapp.do_anything("Bar")
```

### コマンドラインアプリを実行

```(sh)
pipenv run start (もしくはmyapp)
```

### unit test

```(sh)
pipenv run ut
```

### lint

```(sh)
pipenv run lint
```

### create api document (sphinx)

```(sh)
pipenv run doc
```

## 配布物関連

<details>

### ソースコード配布物の作成

dist/ 以下に myapp-0.0.1.tar.gz が生成される。

```(sh)
python setup.py sdist
```

### ソースコード配布物から pip でインストール

```(sh)
pip install myapp-0.0.1-tar.gz
```

### ビルド済み配布物(wheel 形式)の作成

dist/ 以下に myapp-0.0.1-py3-none-any.whl が生成される。

```(sh)
python setup.py bdist_wheel (wheelパッケージが必要)
```

### ビルド済み配布物(wheel 形式)から pip でインストール

```(sh)
pip install myapp-0.0.1-py3-none-any.whl
```

</details>

## 参考

<details>

### パッケージング/開発環境

- <https://techblog.asahi-net.co.jp/entry/2018/06/15/162951>
- <https://techblog.asahi-net.co.jp/entry/2018/11/19/103455>

### コマンドライン引数のパース

- <https://qiita.com/kzkadc/items/e4fc7bc9c003de1eb6d0>

### 環境変数の定義

- <https://pod.hatenablog.com/entry/2019/04/29/164109>

### TravisCIでファイルを(簡単に)暗号化して使用する

- <https://qiita.com/kmats@github/items/d22fd856883e6c16d7ea>

</details>
