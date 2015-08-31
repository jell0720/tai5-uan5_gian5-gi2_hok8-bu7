# -*- coding: utf-8 -*-
from os import listdir, makedirs
from os.path import join, basename
import traceback


from 臺灣言語資料庫.輸出 import 資料輸出工具
from 臺灣言語工具.翻譯.摩西工具.摩西翻譯模型訓練 import 摩西翻譯模型訓練
from 臺灣言語工具.翻譯.摩西工具.語句編碼器 import 語句編碼器
from 臺灣言語工具.系統整合.程式腳本 import 程式腳本
from 臺灣言語工具.解析整理.物件譀鏡 import 物件譀鏡
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.解析整理.詞物件網仔 import 詞物件網仔
from 臺灣言語工具.基本元素.公用變數 import 標點符號
from 臺灣言語工具.基本元素.公用變數 import 無音
from 臺灣言語工具.辭典.型音辭典 import 型音辭典
from 臺灣言語工具.語言模型.KenLM語言模型 import KenLM語言模型
from 臺灣言語工具.語言模型.KenLM語言模型訓練 import KenLM語言模型訓練
from 臺灣言語工具.斷詞.拄好長度辭典揣詞 import 拄好長度辭典揣詞
from 臺灣言語工具.斷詞.連詞揀集內組 import 連詞揀集內組
from 臺灣言語服務.資料模型路徑 import 翻譯語料資料夾
from 臺灣言語服務.資料模型路徑 import 翻譯模型資料夾
from 臺灣言語服務.語言判斷 import 語言判斷
from sys import stderr
'''
from 臺灣言語服務.模型訓練 import 模型訓練
訓練=模型訓練()
訓練.走()
'''


class 模型訓練(程式腳本):
    _翻譯編碼器 = 語句編碼器()  # 若用著Unicdoe擴充就需要
    _語言判斷 = 語言判斷()
    _分析器 = 拆文分析器()
    _譀鏡 = 物件譀鏡()
    _網仔 = 詞物件網仔()
    _揣詞 = 拄好長度辭典揣詞()
    _揀集內組 = 連詞揀集內組()

    def 走(self):
        self.輸出全部語料(翻譯語料資料夾)
        self.訓練全部摩西翻譯模型(翻譯語料資料夾, 翻譯模型資料夾)

    def 輸出全部語料(self, 語料資料夾):
        語料 = 資料輸出工具()
        語料.輸出翻譯語料(語料資料夾)

    def 訓練全部摩西翻譯模型(self, 語料資料夾, 模型資料夾):
        makedirs(模型資料夾, exist_ok=True)
        for 語言 in listdir(語料資料夾):
            try:
                self.訓練摩西翻譯模型(語料資料夾, 模型資料夾, 語言)
            except RuntimeError:
                print('{}的摩西模型訓練失敗！！'.format(語言), file=stderr)
                traceback.print_exc()
                print(file=stderr)

    def 訓練摩西翻譯模型(self, 語料資料夾, 模型資料夾, 語言):
        語言資料夾 = join(語料資料夾, 語言)
        翻譯模型資料夾路徑 = join(模型資料夾, 語言)
        makedirs(翻譯模型資料夾路徑, exist_ok=True)
        if self._語言判斷.是漢語(語言):
            平行華語, 平行母語, 母語文本 = self._漢語語料訓練(語言資料夾, 翻譯模型資料夾路徑)
        else:
            平行華語, 平行母語, 母語文本 = self._一般語料訓練(語言資料夾)

        模型訓練 = 摩西翻譯模型訓練()
        模型訓練.訓練(
            平行華語, 平行母語, 母語文本,
            翻譯模型資料夾路徑,
            連紲詞長度=2,
            編碼器=self._翻譯編碼器,
            刣掉暫存檔=True,
        )

    def _漢語語料訓練(self, 語言資料夾, 翻譯模型資料夾):
        平行華語, 平行母語, 母語文本 = self._原始語料(語言資料夾)
        全部詞 = set()
        for 檔名 in 母語文本:
            for 一逝 in self._讀檔案(檔名):
                for 詞物件 in self._網仔.網出詞物件(self._分析器.轉做句物件(一逝)):
                    字物件 = 詞物件.內底字[0]
                    if 字物件.音 != 無音 and 字物件.型 not in 標點符號:
                        全部詞.add(詞物件)

        母語辭典檔名 = join(翻譯模型資料夾, '母語辭典.txt.gz')
        詞文本 = []
        母語辭典 = 型音辭典(4)
        for 詞物件 in 全部詞:
            詞文本.append(self._譀鏡.看分詞(詞物件))
            母語辭典.加詞(詞物件)
        self._陣列寫入檔案(母語辭典檔名, 詞文本)

        加工資料夾 = join(語言資料夾, '加工語料')
        makedirs(加工資料夾, exist_ok=True)
        原始母語連詞 = self._文本檔轉模型物件(加工資料夾, 母語文本)
        補漢字音標的母語文本 = self._檔案陣列正規化(母語辭典, 原始母語連詞, 加工資料夾, 母語文本)
        母語連詞 = self._文本檔轉模型物件(語言資料夾, 補漢字音標的母語文本)
        return (
            self._檔案陣列正規化(母語辭典, 母語連詞, 加工資料夾, 平行華語),
            self._檔案陣列正規化(母語辭典, 母語連詞, 加工資料夾, 平行母語),
            補漢字音標的母語文本
        )

    def _檔案陣列正規化(self, 母語辭典, 母語連詞, 加工資料夾, 檔名陣列):
        加工了檔名陣列 = []
        for 檔名 in 檔名陣列:
            新檔名 = join(加工資料夾, basename(檔名))
            self._陣列寫入檔案(新檔名, self._檔案正規化(母語辭典, 母語連詞, 檔名))
            加工了檔名陣列.append(新檔名)
        return 加工了檔名陣列

    def _檔案正規化(self, 母語辭典, 母語連詞, 檔名):
        for 一逝 in self._讀檔案(檔名):
            句物件 = self._分析器.轉做句物件(一逝)
            揣詞句物件, _, _ = self._揣詞.揣詞(母語辭典, 句物件)
            選好句物件, _, _ = self._揀集內組.揀(母語連詞, 揣詞句物件)
            yield self._譀鏡.看分詞(選好句物件)

    def _文本檔轉模型物件(self, 語言資料夾, 母語辭典檔名):
        模型訓練 = KenLM語言模型訓練()
        模型檔 = 模型訓練.訓練(母語辭典檔名,
                      join(語言資料夾, '語言模型資料夾'),
                      連紲詞長度=2,
                      編碼器=self._翻譯編碼器,
                      使用記憶體量='20%',
                      )

        return KenLM語言模型(模型檔)

    def _原始語料(self, 語言資料夾):
        平行華語 = [
            join(語言資料夾, '對齊外語語句.txt.gz'),
            join(語言資料夾, '對齊外語字詞.txt.gz'),
        ]
        平行母語 = [
            join(語言資料夾, '對齊母語語句.txt.gz'),
            join(語言資料夾, '對齊母語字詞.txt.gz'),
        ]
        母語文本 = [
            join(語言資料夾, '語句文本.txt.gz'),
            join(語言資料夾, '字詞文本.txt.gz'),
        ]
        return 平行華語, 平行母語, 母語文本

    def _一般語料訓練(self, 語言資料夾):
        #         '華語斷詞'
        pass
