import io
import os
import sys
import unittest
from unittest.mock import patch

import get_data as src

urls = {
    "2023_S2": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=9c7aa7ee431258f1e440f30712c753852060308494c342eabadeefbbfb625bdf3fb30ef32c156e6fda4d49d2eb1aedfe&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2023_S1": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=302b3663ea7dcc3e7fcd75248c00d7f8dce62d8d0edb5d005fcd4754fe58ba52900176cac788b741aa65d196c1111128&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2022_S2": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=c72ca0619950e8a7d69baf1397024a304e3aa205e67dd26e35d621953c7b9ce57b9a032fda8efa4431b35195a61837d6&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2022_S1": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=ca7566e4e242c8ff6517942eef62517874eca4eb64987298040ca64f5e4f1c2a6f32ed2ab6b9aa07fb5f0a14dcb6fad4&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2021_S2": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=342e051da808e985a0167f990cfe7a46abc5beab60663eb74d8b7ae325870bd446be868b231a7b18c334ccf69834a15e&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2021_S1": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=bcdf1b0ec81352a70535f1de444eda54897d73b744e8f15dc579415feef724afe3d29c238185956deb5781411cb380b8&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2020_S2": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=c9663b45398a251cfdb54ff8998821d140afe639121bbb4aa82cf8dcd86ff720a14c2a17fccbd5c418e2a8446a82c74a&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2020_S1": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=0c9b4b34c0816125c132b1171e502d17c7139773c6f3efee64ae53fe22a74488dd986b5f1dbfbab7d89124d999796767&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2019_S2": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=8d8c53aef941dae8923bc0fa8e063f1a35abf499751151b65cb59092bd0313d869c94b45b80adcf47a66468c423f15e1&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2019_S1": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=643de3bccbfc176c5a41f71bde9f752d4806f18f1c80ab898b196accda2229a8bfda6a758e5c8da418532a2f4f44e021&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2018_S2": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=29fa4c6e6d1651785559a31caa540777d380dc3f72cc12d21b3d77a2956f6f24385a18b81319ecdcc7a23b4531937938&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2018_S1": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=eb99631476f13684f70fd8e798bf8c476962774f196927d6cbf853a18e2d3d8cffa771d01ad99a780f97820bd5074664&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2017_S2": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=8f99cb59ed2c7514f69a3ff8cf8662dd9d46fc7a45defeecdd22f6cb25831a7a17d4db0e8c10d3e22008bb4cc7adbab3&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2017_S1": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=f383a62904bf7f285d4e05dd81e82f60fbcb4ab5790a098fe1786be7a5bddd1a5541c509e19b81f236090be727b1f93c&ReportType=2&regl=en-US&IsReportLandscape=False",
    "2016_S2": "https://monash.bluera.com/monash/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=12ff95e0a78280611bb4c00ae003930993657a5b5c073b9d6ceca631ac8a475ef63f4bf275d6b7259bb0424dc7d5caa3&ReportType=2&regl=en-US&IsReportLandscape=False",
}

def test_block(url):
    try:
        return src.tranform_html_to_data(url)
    except:
        return None

class TestStringMethods(unittest.TestCase):
    def test_2023_S2(self):
        result = test_block(urls["2023_S2"])
        self.assertNotEqual(result, None)

    def test_2023_S1(self):
        result = test_block(urls["2023_S1"])
        self.assertNotEqual(result, None)

    def test_2022_S2(self):
        result = test_block(urls["2022_S2"])
        self.assertNotEqual(result, None)

    def test_2022_S1(self):
        result = test_block(urls["2022_S1"])
        self.assertNotEqual(result, None)

    def test_2021_S2(self):
        result = test_block(urls["2021_S2"])
        self.assertNotEqual(result, None)

    def test_2021_S1(self):
        result = test_block(urls["2021_S1"])
        self.assertNotEqual(result, None)

    def test_2020_S2(self):
        result = test_block(urls["2020_S2"])
        self.assertNotEqual(result, None)

    def test_2020_S1(self):
        result = test_block(urls["2020_S1"])
        self.assertNotEqual(result, None)

    def test_2019_S2(self):
        result = test_block(urls["2019_S2"])
        self.assertNotEqual(result, None)

    def test_2019_S1(self):
        result = test_block(urls["2019_S1"])
        self.assertNotEqual(result, None)

    def test_2018_S2(self):
        result = test_block(urls["2018_S2"])
        self.assertNotEqual(result, None)

    def test_2018_S1(self):
        result = test_block(urls["2018_S1"])
        self.assertNotEqual(result, None)

    def test_2017_S2(self):
        result = test_block(urls["2017_S2"])
        self.assertNotEqual(result, None)

    def test_2017_S1(self):
        result = test_block(urls["2017_S1"])
        self.assertNotEqual(result, None)

    def test_2016_S2(self):
        result = test_block(urls["2016_S2"])
        self.assertNotEqual(result, None)

if __name__ == "__main__":
    unittest.main()
