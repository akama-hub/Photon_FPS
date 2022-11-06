using System.Diagnostics;
using System.IO;
using UnityEngine;
using System.Collections.Generic;

public class PythonFromCs : MonoBehaviour
{
    //pythonがある場所
    // import sys
    // sys.executable で確認できる
    // 家のデスクトップ
    private string pyExePath = @"C:\\Users\\ssk-d\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\python.exe";

    //実行したいスクリプトがある場所
    private string pyCodePath = @"D:\Unity-Project\Photon_FPS\python\DRL\test.py";
    // private string pyCodePath = @"\mnt\HDD\Photon_FPS\python\DRL\test.py";

    private int i = 0;

    private void Start () {
        // python で実行するファイルの引数を設定
        var arguments = new List<string> {
            pyCodePath,
            "Hello",
            "python",
            "from cs"
        };

        //外部プロセスの設定
        ProcessStartInfo processStartInfo = new ProcessStartInfo() {
            FileName = pyExePath, //実行するファイル(python)
            UseShellExecute = false,//シェルを使うかどうか
            CreateNoWindow = true, //ウィンドウを開くかどうか
            RedirectStandardOutput = true, //テキスト出力をStandardOutputストリームに書き込むかどうか
            // Arguments = pyCodePath + " " + "Hello,python.", //実行するスクリプト 引数(複数可)
            Arguments = string.Join(" ", arguments),
        };

        //外部プロセスの開始
        Process process = Process.Start(processStartInfo);

        //ストリームから出力を得る
        StreamReader streamReader = process.StandardOutput;
        // string str = streamReader.ReadLine();
        string str = streamReader.ReadToEnd();


        //外部プロセスの終了
        process.WaitForExit();
        process.Close();

        //実行
        print(str);
    }
}