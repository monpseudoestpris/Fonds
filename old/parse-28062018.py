#!/usr/bin/env python3

import argparse
import os
import re
import math
from decimal import Decimal
NB=5
SCORE1AN=0.6
SCORE3ANS=0.3
SCORE5ANS=0.1
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
    
    fi = open(args.file_to_parse)
    funds = fi.readlines()
    listeFonds=[]
    listFondsByCat={}
    listPerfoCat=[]
    for fund in funds:
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
        if re.search('\s\d+\.\d+\sEUR.*', remaining):
            # regexp:
            #   first character is space, then at least one digit
            #   then one dot then at least one digit, then one space
            #   then EUR followed by any characters until the end of the
            #   string
            category = re.sub('\s\d+\.\d+\sEUR.*', '', remaining).strip()
        # case - EUR
        elif re.search('\s-\sEUR.*', remaining):
            # regexp:
            #   space - space EUR followed by any characters until the 
            #   end of the string
            category = re.sub('\s-\sEUR.*', '', remaining).strip()
        else:
            raise Exception("error while parsing fund")
        # we remove the category from the remaining sub-string to parse
        remaining = remaining.replace(category + ' ', '')
        remaining = remaining.replace(' EUR', '')
        remaining = remaining.replace(' %', '')
        remaining = remaining.split(' ')
        fund = title + ';' + category + ';'.join(remaining)
        funds=fund.split(";")
        perfo5ans=getperfo(funds[-1],5)
        perfo3ans=getperfo(funds[-2],3)
        perfo1an=getperfo(funds[-3],1)
        nomFonds=funds[0]
        categorie=funds[1].replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","").replace(" ","")
        
        metrique=round(Decimal(SCORE1AN*perfo1an+SCORE3ANS*perfo3ans+SCORE5ANS*perfo5ans),2)
        listeFonds.append([nomFonds,categorie,perfo1an,perfo3ans,perfo5ans,metrique])
        if not(categorie in listFondsByCat):
            listFondsByCat[categorie]=[]
            listFondsByCat[categorie].append([nomFonds,categorie,perfo1an,perfo3ans,perfo5ans,metrique])
        else:
            listFondsByCat[categorie].append([nomFonds,categorie,perfo1an,perfo3ans,perfo5ans,metrique])
    listeFondsTri=sorted(listeFonds,key=lambda x:-x[-1])
    print("Computation with 1 YEAR=",SCORE1AN,"3 YEARS=",SCORE3ANS,"5 YEAR=",SCORE5ANS)
    print("================= 20 best funds ====================")
    for l in listeFondsTri[0:20]:
        print(strFund(l))
    print("\n\n\n\n=================Ranking by category=============")
    for c in listFondsByCat:
        if len(listFondsByCat[c])>-1:
            print("============",c,"============")
            perfoGlob=0
            cpt=0
            l=listFondsByCat[c]
            lTri=sorted(l,key=lambda x:-x[-1])
            for ll in lTri[0:NB]:
                print(strFund(ll))
                perfoGlob=perfoGlob+ll[-1]/NB
                cpt+=1
            listPerfoCat.append([ll[1],perfoGlob,cpt])
    print("\n\n\n\n=================Ranking of categories=============")
    lcatTri=sorted(listPerfoCat,key=lambda x:-x[1])
    for ll in lcatTri:
        print(ll[0],ll[1],"computed on ",ll[2]," values")
        
        
        