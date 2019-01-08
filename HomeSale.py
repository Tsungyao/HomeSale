#!/usr/local/bin/python3
import re
import xml.etree.ElementTree as ET
import os

strArrayCommunity = [
        ['鴻柏', '鴻向', '', '新竹縣竹北市自強北路331~360號'],
        ['禾寅', '文鼎為美', 'A', '新竹縣竹北市勝利八街二段91~120號'],
        ['禾寅', '文鼎為美', 'B', '新竹縣竹北市十興二街151~180號'],
        ['富宇', '雲極', '', '新竹縣竹北市勝利八街二段121~150號'],
        ['仁發', '藏綠', 'A', '新竹縣竹北市十興五街61~90號'],
        ['仁發', '藏綠', 'B', '新竹縣竹北市十興五街91~120號'],
        ['興富發', '國賓大悅', '', '新竹縣竹北市勝利八街一段211~240號']
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
    csvFile.write('室內坪,')
    csvFile.write('停車坪,')
    csvFile.write('樓層,')
    csvFile.write('樓層等分,')
    csvFile.write('車位價,')
    csvFile.write('總價,')
    csvFile.write('每坪單價\r')
#############  vWriteTitle() end  #############

############# vWriteHouseData() start #############
def vWriteHouseData(csvFile, structHouse):
    csvFile.write(structHouse[0] + ',')     # strCommunity[0]       建商
    csvFile.write(structHouse[1] + ',')     # strCommunity[1]       社區
    csvFile.write(structHouse[2] + ',')     # strCommunity[2]       棟向
    csvFile.write(structHouse[3] + ',')     # Data.text             日期
    csvFile.write(structHouse[4] + ',')     # str(fTotalPING)       總坪
    csvFile.write(structHouse[5] + ',')     # str(fExactPING)       室內坪
    csvFile.write(structHouse[6] + ',')     # str(fParkPING)        停車坪
    csvFile.write(structHouse[7] + ',')     # uTargetFloor          樓層
    csvFile.write(structHouse[8] + ',')     # uFloorPercent         樓層等分
    csvFile.write(structHouse[9] + ',')     # fParkPrice            車位價
    csvFile.write(structHouse[10] + ',')    # fTotalPrice           總價
    csvFile.write(structHouse[11] + '\r')   # strExactPricePerPING  每坪單價
#############  vWriteHouseData() end  #############

############# uDenterminFloor() start #############
def uDenterminFloor(strFloor):
    uFloor = 0
    for i in range(len(strFloor)):
        if ord(strFloor[i]) == ord("一"):
            uFloor += 1

        elif ord(strFloor[i]) == ord("二"):
            uFloor += 2

        elif ord(strFloor[i]) == ord("三"):
            uFloor += 3

        elif ord(strFloor[i]) == ord("四"):
            uFloor += 4

        elif ord(strFloor[i]) == ord("五"):
            uFloor += 5

        elif ord(strFloor[i]) == ord("六"):
            uFloor += 6

        elif ord(strFloor[i]) == ord("七"):
            uFloor += 7

        elif ord(strFloor[i]) == ord("八"):
            uFloor += 8

        elif ord(strFloor[i]) == ord("九"):
            uFloor += 9

        elif ord(strFloor[i]) == ord("十"):
            if i is 0:
                uFloor = 1
            uFloor *= 10

        elif ord(strFloor[i]) == ord("全"):
            return 0

        elif ord(strFloor[i]) == ord("層"):
            return uFloor

        else:
            print(strFloor[i])
            print(uFloor)
            uFloor = 0
############# uDenterminFloor() end   #############

############# vHandleDeals() start #############
def vHandleDeals(strFilePath, csvFile):
    xmlTree = ET.parse(strFilePath)
    root = xmlTree.getroot()
    for Deal in root.findall("./買賣"):
        for Community in Deal.findall("./土地區段位置或建物區門牌") or Deal.findall("./土地區段位置建物區段門牌"):
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
                print(Deal.find('編號').text)

                TotalArea = Deal.find("建物移轉總面積平方公尺")
                TotalPrice = Deal.find("總價元")
                ParkArea = Deal.find("車位移轉總面積平方公尺")
                ParkPrice = Deal.find("車位總價元")
                Data = Deal.find("交易年月日")
                TotalFloor = Deal.find ("總樓層數")
                TargetFloor = Deal.find("移轉層次")

                print("社區: " + strCommunity[1])
                print("日期: " + Data.text)
                print(TotalFloor.text)

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
                    uFloorPercent = (uTargetFloor * 4) // uTotalFloor
                else:
                    uFloorPercent = 0xFFFF

                #============ Calculate the cost per square meter ===========#
                fTotalArea = float(TotalArea.text)
                fTotalPrice = float(TotalPrice.text)
                fParkArea = float(ParkArea.text)
                fParkPrice = float(ParkPrice.text)

                if fParkPrice == 0:
                    fParkPrice = 1122330;
                    if fParkArea > 40:
                        fParkPrice *= round(fParkArea / (10 * SQUARE_METER_PER_PING));

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

                #if uTargetFloor < 6 or uTargetFloor > 12:
                #    continue
                structHouse = [strCommunity[0],
                               strCommunity[1],
                               strCommunity[2],
                               Data.text,
                               str(fTotalPING),
                               str(fExactPING),
                               str(fParkPING),
                               str(uTargetFloor),
                               str(uFloorPercent),
                               str(fParkPrice),
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
        print(os.path.join(dirPath, f))

        vHandleDeals(os.path.join(dirPath, f), csvFile)



csvFile.close()
#############  main() end   #############
