#!/usr/bin/python
#coding=utf-8
import re
import xml.etree.ElementTree as ET
import os
import csv

strArrayCommunity = [
        ['仁發 藏綠 A', u'新竹縣竹北市十興五街61~90號'],
        ['仁發 藏綠 B', u'新竹縣竹北市十興五街91~120號']
        ]

SQUARE_METER_PER_PING = 3.305785
WORKSPACE = './'

for dirPath, dirNames, fileNames in os.walk(WORKSPACE):
    for f in fileNames:
        ############# guardian line #############
        if not re.match('.*[xX][mM][lL]', f):
            continue
        #########################################

        FILEPATH = os.path.join(dirPath, f)
        xmlTree = ET.parse(FILEPATH)
        root = xmlTree.getroot()
        for Deal in root.findall(u"./買賣"):
            for strCommunity in strArrayCommunity:
                for Community in Deal.findall(u"./土地區段位置或建物區門牌"):
                    utf8Target = strCommunity[1]

                    ############# guardian line #############
                    if not Community.text:
                        break
                    #########################################

                    # Compare the address
                    for i in range(len(Community.text)):
                        if Community.text[i] != utf8Target[i]:
                            break
                    # Skip if address does not match
                    if i + 1 != len(Community.text):
                        continue

                    TotalArea = Deal.find(u"建物移轉總面積平方公尺")
                    TotalPrice = Deal.find(u"總價元")
                    ParkArea = Deal.find(u"車位移轉總面積平方公尺")
                    ParkPrice = Deal.find(u"車位總價元")
                    Data = Deal.find(u"交易年月日")

                    fTotalArea = float(TotalArea.text)
                    fTotalPrice = float(TotalPrice.text)
                    fParkArea = float(ParkArea.text)
                    fParkPrice = float(ParkPrice.text)

                    fExactArea = fTotalArea - fParkArea
                    fExactPrice = fTotalPrice - fParkPrice

                    fExactPricePerArea = fExactPrice / fExactArea

                    print "社區: " + strCommunity[0]
                    print "日期: " + Data.text

                    fTotalPING = fTotalArea / SQUARE_METER_PER_PING
                    fParkPING = fParkArea / SQUARE_METER_PER_PING

                    fExactPING = fTotalPING - fParkPING
                    fExactPricePerPING = fExactPrice / fExactPING / 10000

                    print "總坪: " + str(fTotalPING)
                    print "實坪: " + str(fExactPING)
                    print "停車坪: " + str(fParkPING)
                    print "每坪單價: " + str(fExactPricePerPING)
                    print "\r"
