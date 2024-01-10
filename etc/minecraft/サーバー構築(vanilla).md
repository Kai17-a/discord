## マイクラバニラサーバー初期構築手順メモ（EC2）

### 前準備
必要なパッケージをインストール
```shell
sudo yum -y update
sudo yum install -y java-17-amazon-corretto-devel.x86_64
sudo yum install -y tmux
```

### 1. 作業用ディレクトリ作成
```shell
mkdir ~/minecraft && cd ~/minecraft/
```

### 2. マイクラサーバーダウンロード
1. 公式からサーバー用.jarファイルをダウンロード（ver 1.20.2）<br />
    ※最新版でないバージョンの場合はURLが取得できないのでクライアントからサーバーにアップロードする
```shell
wget https://piston-data.mojang.com/v1/objects/8dd1a28015f51b1803213892b50b7b4fc76e594d/server.jar
```

2. .jarファイル名を `server.jar"` に変更
```shell
mv ./ダウンロードしたjarファイル名.jar ./server.jar
```

### 3. サーバー起動
1. `server.jar` を実行（エラー）<br />
    **※初期実行は規約に同意をしていないためエラーになる**
```shell
java -Xmx1024M -Xms1024M -jar server.jar nogui
```
2. 規約に同意
```shell
sed -i -e "s/eula=false/eula=true/g" eula.txt
```

3. 再起動
```shell
java -Xmx1024M -Xms1024M -jar server.jar nogui
```