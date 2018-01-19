#!/usr/bin/python
#coding=utf-8
import re
import xml.etree.ElementTree as ET
import os

strArrayCommunity = [
        ['鴻柏', '鴻向', '', u'新竹縣竹北市自強北路331~360號'],
        ['富宇', '雲極', 'A', u'新竹縣竹北市勝利八街二段91~120號'],
        ['富宇', '雲極', 'B', u'新竹縣竹北市十興二街151~180號'],
        ['富宇', '雲極', 'C', u'新竹縣竹北市勝利八街二段121~150號'],
        ['仁發', '藏綠', 'A', u'新竹縣竹北市十興五街61~90號'],
        ['仁發', '藏綠', 'B', u'新竹縣竹北市十興五街91~120號']
        ]

SQUARE_METER_PER_PING = 3.305785
WORKSPACE = './'

############# vWriteTitle() start  #############
def vWriteTitle(csvFile):
    csvFile.write('建商,')
    csvFile.write('社區,')
    csvFile.write('棟向,')
    csvFile.write('日期,')
    csvFile.write('總坪,')
    csvFile.write('室內實坪,')
    csvFile.write('停車坪,')
    csvFile.write('樓層,')
    csvFile.write('樓層等分,')
    csvFile.write('總價,')
    csvFile.write('每坪單價\r')
#############  vWriteTitle() end  #############

############# vWriteHouseData() start #############
def vWriteHouseData(csvFile, structHouse):
    csvFile.write(structHouse[0] + ',')  # strCommunity[0]      建商
    csvFile.write(structHouse[1] + ',')  # strCommunity[1]      社區
    csvFile.write(structHouse[2] + ',')  # strCommunity[2]      棟向
    csvFile.write(structHouse[3] + ',')  # Data.text            日期
    csvFile.write(structHouse[4] + ',')  # str(fTotalPING)      總坪
    csvFile.write(structHouse[5] + ',')  # str(fExactPING)      室內實坪
    csvFile.write(structHouse[6] + ',')  # str(fParkPING)       停車坪
    csvFile.write(structHouse[7] + ',')  # uTargetFloor         樓層
    csvFile.write(structHouse[8] + ',')  # uFloorPercent        樓層等分
    csvFile.write(structHouse[9] + ',')  # fTotalPrice          總價
    csvFile.write(structHouse[10] + '\r') # strExactPricePerPING 每坪單價
#############  vWriteHouseData() end  #############

############# uDenterminFloor() start #############
def uDenterminFloor(strFloor):
    uFloor = 0
    for i in range(len(strFloor)):
        if ord(strFloor[i]) == ord(u"一"):
            uFloor += 1

        elif ord(strFloor[i]) == ord(u"二"):
            uFloor += 2

        elif ord(strFloor[i]) == ord(u"三"):
            uFloor += 3

        elif ord(strFloor[i]) == ord(u"四"):
            uFloor += 4

        elif ord(strFloor[i]) == ord(u"五"):
            uFloor += 5

        elif ord(strFloor[i]) == ord(u"六"):
            uFloor += 6

        elif ord(strFloor[i]) == ord(u"七"):
            uFloor += 7

        elif ord(strFloor[i]) == ord(u"八"):
            uFloor += 8

        elif ord(strFloor[i]) == ord(u"九"):
            uFloor += 9

        elif ord(strFloor[i]) == ord(u"十"):
            if i is 0:
                uFloor = 1
            uFloor *= 10

        elif ord(strFloor[i]) == ord(u"全"):
            return 0

        elif ord(strFloor[i]) == ord(u"層"):
            return uFloor

        else:
            print strFloor[i]
            print uFloor
            uFloor = 0
############# uDenterminFloor() end   #############

############# vHandleDeals() start #############
def vHandleDeals(strFilePath, csvFile):
    xmlTree = ET.parse(strFilePath)
    root = xmlTree.getroot()
    for Deal in root.findall(u"./買賣"):
        for Community in Deal.findall(u"./土地區段位置或建物區門牌"):
            for strCommunity in strArrayCommunity:
                utf8Target = strCommunity[3]

                #------------ guardian line ------------#
                if not Community.text:
                    break
                #---------------------------------------#

                # Compare the address
                for i in range(len(Community.text)):
                    if Community.text[i] != utf8Target[i]:
                        break
                # Skip if address does not match
                if i + 1 != len(Community.text):
                    continue

                csvFileCommunity = open(WORKSPACE + 'HomeSale' + strCommunity[0] + strCommunity[1] + strCommunity[2] + '.csv', 'a')
                print Deal.find(u'編號').text

                TotalArea = Deal.find(u"建物移轉總面積平方公尺")
                TotalPrice = Deal.find(u"總價元")
                ParkArea = Deal.find(u"車位移轉總面積平方公尺")
                ParkPrice = Deal.find(u"車位總價元")
                Data = Deal.find(u"交易年月日")
                TotalFloor = Deal.find (u"總樓層數")
                TargetFloor = Deal.find(u"移轉層次")

                print "社區: " + strCommunity[1]
                print "日期: " + Data.text

                #============ Determine the floor info ===========#
                if TotalFloor.text:
                    uTotalFloor = uDenterminFloor(TotalFloor.text)
                else:
                    uTotalFloor = 0

                if TargetFloor.text:
                    uTargetFloor = uDenterminFloor(TargetFloor.text)
                else:
                    uTargetFloor = 0

                if uTotalFloor != 0:
                    uFloorPercent = (uTargetFloor * 4) / uTotalFloor
                else:
                    uFloorPercent = 0xFFFF

                #============ Calculate the cost per square meter ===========#
                fTotalArea = float(TotalArea.text)
                fTotalPrice = float(TotalPrice.text)
                fParkArea = float(ParkArea.text)
                fParkPrice = float(ParkPrice.text)

                fExactArea = fTotalArea - fParkArea
                fExactPrice = fTotalPrice - fParkPrice

                if fExactArea == 0:
                    fExactPricePerArea = 0
                    strExactPricePerArea = "N/A"
                else:
                    fExactPricePerArea = fExactPrice / fExactArea
                    strExactPricePerArea = str(fExactPricePerArea)

                #============ Calculate the cost per PING ===========#
                fTotalPING = fTotalArea / SQUARE_METER_PER_PING
                fParkPING = fParkArea / SQUARE_METER_PER_PING

                fExactPING = fTotalPING - fParkPING
                if fExactPING == 0:
                    fExactPricePerPING = 0
                    strExactPricePerPING = "N/A"
                else:
                    fExactPricePerPING = fExactPrice / fExactPING / 10000
                    strExactPricePerPING = str(fExactPricePerPING)

                structHouse = [strCommunity[0],
                               strCommunity[1],
                               strCommunity[2],
                               Data.text,
                               str(fTotalPING),
                               str(fExactPING),
                               str(fParkPING),
                               str(uTargetFloor),
                               str(uFloorPercent),
                               str(fTotalPrice),
                               strExactPricePerPING]

                vWriteHouseData(csvFile, structHouse)
                vWriteHouseData(csvFileCommunity, structHouse)

                csvFileCommunity.close()
#############  vHandleDeals() end  #############








############# main() start  #############

#============ Remove old csv ===========#
for dirPath, dirNames, fileNames in os.walk(WORKSPACE):
    if dirPath is not './':
        continue
    for f in fileNames:
        if re.match('.*csv', f):
            os.remove(os.path.join(dirPath, f))

#============ Create new csv ===========#
csvFile = open(WORKSPACE + 'HomeSale.csv', 'w')
vWriteTitle(csvFile)

for strCommunity in strArrayCommunity:
    csvFileCommunity = open(WORKSPACE + 'HomeSale' + strCommunity[0] + strCommunity[1] + strCommunity[2] + '.csv', 'a')
    vWriteTitle(csvFileCommunity)
    csvFileCommunity.close()

#============ Handle Deals in each files ===========#
for dirPath, dirNames, fileNames in os.walk(WORKSPACE):
    for f in fileNames:
        #------------ guardian line ------------#
        if not re.match('.*[xX][mM][lL]', f) or not re.match('[OJ].*', f):
            continue
        #---------------------------------------#
        print os.path.join(dirPath, f)

        vHandleDeals(os.path.join(dirPath, f), csvFile)



csvFile.close()
#############  main() end   #############
