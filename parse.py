#!/usr/bin/env python3

import argparse
import os
import re
import math
from decimal import Decimal
import sys
import xlsxwriter
import random

 
NB=3000
NBPERFO=10
SCORE1AN=0.5
SCORE3ANS=0.25
SCORE5ANS=0.25

listreplace=["Actions","italisations","-","logie","ernatif","ectionnelle","mmation","munication","/","reprises","-","_","érales","reprises"]

def shortenname(sheetname):
    for r in listreplace:
        sheetname=sheetname.replace(r,"")
    sheetname=sheetname.lower()
    return(sheetname)

def getperfo(c,year):
    try:
        valeur=1+(float)(c)/100.0
    except:
        valeur=1.0

    out=(math.pow(valeur,1/year)-1)*100
    return(out)
def strFund(l):
    out=l[0]+" "+l[1]+" "+(str)(l[-1])
    return(out)
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="convert raw funds file to CSV")
    parser.add_argument("file_to_parse", help="the file to parse")
    args = parser.parse_args()
    assert os.path.exists(args.file_to_parse), "the file to parse doesn't exist"
    money=args.file_to_parse.split('.')[0][-3:]
    fi = open(args.file_to_parse)
    funds = fi.readlines()
    listeFonds=[]
    listFondsByCat={}
    listPerfoCat=[]
    cpterror=0
    workbook = xlsxwriter.Workbook(money+'.xlsx')


    # c1='\s\d+\.\d+\sEUR.*'
    c1 = '\s\d+\.\d+\s' + money + '.*'
    #c2='\s-\sEUR.*'
    c2='\s-\s'+money+'.*'
    for fund in funds:
        error=False
        fund = fund.strip()

        # we ignore the headers which appear several times in the file
        if fund.find('Nom Catégorie')!=-1:
            continue
        # we extract the title of the fund
        title = re.sub('[A-Z][a-z].*$', '', fund).strip()
        # we remove the title from the remaing sub-string to parse
        remaining = fund.replace(title, '')

        # === next, we extract the category of the fund ====
        category = ""
        # case XX.YY EUR


        if re.search(c1, remaining):
            # regexp:
            #   first character is space, then at least one digit
            #   then one dot then at least one digit, then one space
            #   then EUR followed by any characters until the end of the
            #   string
            #c2='\s\d+\.\d+\sEUR.*'

            category = re.sub(c1, '', remaining).strip()
        # case - EUR
        elif re.search(c2, remaining):
            # regexp:
            #   space - space EUR followed by any characters until the
            #   end of the string
            category = re.sub(c2, '', remaining).strip()
        else:
            error=True

            #sys.stderr.write("Error while parsing line "+fund+"\n")
            cpterror+=1
            category="xxxxx"
            funds=fund.split("%")
            title=funds[0].split(".")[0][:-3]
            #print("=======================================")
            #print(funds)
            #raise Exception("error while parsing fund")
        # we remove the category from the remaining sub-string to parse
        if error==False:
            remaining = remaining.replace(category + ' ', '')
            c3= ' '+money
            remaining = remaining.replace(c3, '')
            remaining = remaining.replace(' %', '')
            remaining = remaining.split(' ')
            fund = title + ';' + category + ';'.join(remaining)
            funds=fund.split(";")
        if error==False:
            try:
                perfo5ans=getperfo(funds[-1],5)
            except:
                perfo5ans=0
            try:
                perfo3ans=getperfo(funds[-2],3)
            except:
                perfo3ans=0
            try:
                perfo1an=getperfo(funds[-3],1)
            except:
                perfo1an=0
        else:
            try:
                perfo5ans=getperfo(funds[4],5)
            except:
                perfo5ans=0
            try:
                perfo3ans=getperfo(funds[3],3)
            except:
                perfo3ans=0
            try:
                perfo1an=getperfo(funds[2],1)
            except:
                perfo1an=0
        if error==False:
            nomFonds=funds[0]
        else:
            nomFonds=title
        if error==False:
            categorie=funds[1].replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","").replace(" ","").replace("-","")
        else:
            categorie="xxxxx"
        categorie = shortenname(categorie)
        metrique=round(Decimal(SCORE1AN*perfo1an+SCORE3ANS*perfo3ans+SCORE5ANS*perfo5ans),2)
        #print(nomFonds,":",metrique,perfo1an,perfo3ans,perfo5ans,metrique)
        listeFonds.append([nomFonds,categorie,perfo1an,perfo3ans,perfo5ans,metrique])
        if not(categorie in listFondsByCat):
            listFondsByCat[categorie]=[]
            listFondsByCat[categorie].append([nomFonds,categorie,perfo1an,perfo3ans,perfo5ans,metrique])
        else:
            listFondsByCat[categorie].append([nomFonds,categorie,perfo1an,perfo3ans,perfo5ans,metrique])
    listeFondsTri=sorted(listeFonds,key=lambda x:-x[-1])
    print("Computation with 1 YEAR=",SCORE1AN,"3 YEARS=",SCORE3ANS,"5 YEAR=",SCORE5ANS)
    print("================= 50000 best funds ====================")
    worksheet = workbook.add_worksheet("Best-Off")
    row = 0
    col = 0
    bold = workbook.add_format({'bold': True})
    worksheet.write(row, col, "Nom du fonds", bold)
    worksheet.write(row, col + 1, "Categorie", bold)
    worksheet.write(row, col + 2, "Perfo 1 an", bold)
    worksheet.write(row, col + 3, "Perfo 3 ans", bold)
    worksheet.write(row, col + 4, "Perfo 5 ans", bold)
    worksheet.write(row, col + 5, "Perfo", bold)
    row += 1
    nn=min(50000,len(listeFondsTri)-1)
    for l in listeFondsTri[0:nn]:
        print(strFund(l))
        worksheet.write(row, col, str(l[0]))  # nom
        worksheet.write(row, col + 1, str(l[1]))  # cat
        worksheet.write(row, col + 2, str(l[2]))  # 1an
        worksheet.write(row, col + 3, str(l[3]))  # 3ans"
        worksheet.write(row, col + 4, str(l[4]))  # 5 ans
        worksheet.write(row, col + 5, str(l[-1]))  # metrique
        row+=1
    keylist=listFondsByCat.keys()
    keylist=sorted(keylist)
    print("\n\n\n\n=================Ranking by category=============")
    #for c in (listFondsByCat):
    for c in keylist:
        sheetname=c
        sheetname=shortenname(sheetname)

        if len(sheetname)>31:
            sheetname=sheetname[0:28]

        if len(listFondsByCat[c])>-1:
            print("============",c,"("+str(len(listFondsByCat[c]))+" funds)============")
            row = 0
            col = 0
            try:
                worksheet = workbook.add_worksheet(sheetname)
            except:
                worksheet = workbook.add_worksheet(sheetname+(str(random.randint(1,100))))
                print("DOUBLE",sheetname)
            worksheet.write(row, col, "Nom du fonds",bold)
            worksheet.write(row, col + 1, "Categorie",bold)
            worksheet.write(row, col + 2, "Perfo 1 an", bold)
            worksheet.write(row, col + 3, "Perfo 3 ans", bold)
            worksheet.write(row, col + 4, "Perfo 5 ans", bold)
            worksheet.write(row, col + 5, "Perfo",bold)
            row+=1
            perfoGlob=0
            cpt=0
            l=listFondsByCat[c]
            lTri=sorted(l,key=lambda x:-x[-1])
            for ll in lTri[0:NB]:
                print(strFund(ll))
                worksheet.write(row,col,str(ll[0]))#nom
                worksheet.write(row, col+1, str(ll[1]))#cat
                worksheet.write(row, col + 2, str(ll[2]))#1an
                worksheet.write(row, col + 3, str(ll[3]))#3ans"
                worksheet.write(row, col + 4, str(ll[4]))#5 ans
                worksheet.write(row, col + 5, str(ll[-1]))#metrique
                row+=1
                #perfoGlob=perfoGlob+ll[-1]/len(lTri[0:NB])
            for ll in lTri[0:NBPERFO]:
                perfoGlob=perfoGlob+ll[-1]/len(lTri[0:NBPERFO])
                cpt+=1
            listPerfoCat.append([ll[1],perfoGlob,cpt])
    print("\n\n\n\n=================Ranking of categories=============")
    worksheet = workbook.add_worksheet("Classement categories")
    lcatTri=sorted(listPerfoCat,key=lambda x:-x[1])
    row=0
    col=0
    for ll in lcatTri:
        v=round(Decimal(ll[1]),2)
        print(ll[0],v,"computed on ",ll[2]," values")
        worksheet.write(row,col,str(ll[0]))
        worksheet.write(row, col+1, str(v))
        row+=1

    #print(cpterror,"lines could not be parsed")
    workbook.close()

