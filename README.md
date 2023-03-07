# Photon_FPS
Photon Networkを使って、実験用のオンラインFPSゲームをUnity上で作成した.
参考youtube：(\url{https://www.youtube.com/watch?v=_EgC03tzU-k&t=0s})

sooting\がFPS用のフォルダとなっている.
pythonにはゲーム情報のログをとるためのファイル、python\DRLには使用した推定用の深層強化学習用のファイル(2DRL_train.py, 2DRL_exe.py)が入っている。

Unity Hub(\url{https://docs.unity3d.com/ja/2019.4/Manual/GettingStartedInstallingHub.html})を使用してUnity(ver. 2020.3.11f1)を起動し、Unity上で編集・実行ができる.
WebGL Buildで実行ファイルを作成するとUnity無しでゲームが実行できる.

# git clone(pull) 後にすること

## ゲームの起動方法(2種類)
 + webserver for chrome を使って index.html を開く
 + 開かないときはWebGL-BuildのLを小文字にしてみる（Build以下のファイルも同様）

 + WexGL-Build で実行ファイルを作成する

## キャラクターが表示されない
 + キャラクターのshooting/Assets/Model1/Slim Shooter Pack/Ch49_nonPBR.fbx をmixamo(\url{https://www.mixamo.com/#/})からダウンロードしなおす

## Build時の注意点
 + オブジェクトのひも付けが解除されている場合は修正が必要
 + 各webサイトからAssetのダウンロード
   + Animatorはmixamo \url{https://www.mixamo.com/#/}からダウンロードできる
   + 地形のtextureはtexture Heaven　からダウンロードできる\url{https://polyhaven.com/textures}

## UbuntuでBuildする際
 +  sudo apt install libtinfo5
    