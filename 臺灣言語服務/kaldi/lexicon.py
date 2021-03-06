from 臺灣言語工具.基本物件.公用變數 import 無音
from 臺灣言語工具.基本物件.字 import 字
from 臺灣言語服務.漢語語音處理 import 漢語語音處理


class 辭典輸出:
    def __init__(self, 羅馬字, 選擇函式):
        self.羅馬字系統 = 羅馬字
        self.輸出函式 = getattr(self, 選擇函式)

    def 拆做音素(self, 字物件):
        原聲, 韻, 調 = self._提出音值(字物件).音
        聲 = 原聲 + '-'
        新韻類 = []
        新調類 = set()
        for 一个音素 in 漢語語音處理.切漢語韻(韻):
            一个音素調 = 一个音素 + 調
            新韻類.append((一个音素, 一个音素調))
            新調類.add((調, 一个音素調))
        return [聲], 新韻類, 新調類

    def 拆做聲韻(self, 字物件):
        原聲, 韻, 調 = self._提出音值(字物件).音
        聲 = 原聲 + '-'
        一个音素調 = 韻 + 調
        return [聲], [(韻, 一个音素調)], {(調, 一个音素調)}

    def 拆做聲韻莫調(self, 字物件):
        原聲, 原韻, _調 = self._提出音值(字物件).音
        聲 = 原聲 + '-'
        韻 = 原韻.rstrip('0123456789')
        return [聲], [(韻, 韻)], set()

    def 拆做音節(self, 字物件):
        原聲, 韻, 調 = self._提出音值(字物件).音
        一个音素調 = 原聲 + 韻 + 調
        return [], [(原聲 + 韻, 一个音素調)], {(調, 一个音素調)}

    def _提出音值(self, 字物件):
        if 字物件.音 != 無音:
            檢查字物件 = 字物件
        else:
            檢查字物件 = 字(字物件.型, 字物件.型)
        if not 檢查字物件.音標敢著(self.羅馬字系統):
            raise ValueError('音標無合法')
        return 檢查字物件.轉音(self.羅馬字系統, '音值')

    def 漢字聲韻(self,  音節):
        音標物件 = self.羅馬字系統(音節)
        return 音標物件.聲 + 音標物件.韻
