#!/usr/bin/env python
# coding: utf-8

# In[1]:


from lxml import etree as ET
from collections import defaultdict
import re
from array import *

namespace = "{http://www.mediawiki.org/xml/export-0.10/}"

def parseWiktionary(wiktionary_filepath):
    print("Parsing wiktionary...")
    lexicon = ET.Element('lexicon')
    wordID = 1
    verbsCounter = 0
    nounsCounter = 0
    adjCoutner = 0
    advCounter = 0
    
    for event, elem in ET.iterparse(wiktionary_filepath, recover = True):
        # general word information
        base = ""
        category = ""
        genus = ""
        
        # flag if entry for this word should be created
        create = False

        # attributes for verb flexion
        reflexive = False
        
        ###TENSES
        fail_tenses = False
        tpg_matrix = [[""]*6 for _ in range(3)] #tense-person-gender
        for y in range(3):
            tpg_matrix[1][y]=[""]*3
        for y in range(3):
            tpg_matrix[1][y+3]=[""]*2
        #layout:    
        #         1st   2nd   3rd   1st   2nd   3rd
        #present   ()    ()    ()    ()    ()    ()
        #past    (M,F,N)(M,F,N)(M,F,N)(M,N)(M,N)(M,N)
        #command   ()    ()    ()    ()    ()    ()
        
        
        p_less = ""
        transgressive = ""
        IPB = [[""]*3 for _ in range(2)]
        IPC = [[""]*3 for _ in range(2)]
        IPU = ""
        
        # inflected noun forms according to grammatical cases
        conj = True
        noun_case_matrix = [[""]*2 for _ in range(7)]
        case_count = 0
        #mianownik, dopełniacz, celownik, biernik, narzędnik, miejscownik, wołacz
        
        # adjective cases
        comp = ""
        no_comp = False
        desc_comp = False
        adj_case_matrix = [[""]*6 for _ in range(7)]
        adj_case_matrix_comp = [[""]*6 for _ in range(7)]
        adj_case_matrix_sup = [[""]*6 for _ in range(7)]
        #all adjectives conjugate automatically in the document
        #layout: 
        #      masc-person sin    masc-object sin    fem    neuter    masc pl    nonmasc pl
        #CASES
        
        # adverbs
        sup = ""
        multi_def = False
        
        
        
        if elem.tag != namespace+'page':
            continue
        # parse title (word)
        title = elem.find('./' + namespace + 'title')
        if title is None:
            elem.clear()
            continue
        # skip multi-base pages 
        base = title.text
        comp = base
        if not base or ":" in base:
            elem.clear()
            continue
        # parse futher content
        text_element = elem.find('.//' + namespace + 'text')
        if text_element is None or text_element.text is None:
            elem.clear()
            continue
        text = text_element.text.splitlines()
        
        defined = False
		
        for line in text:
            if line.startswith('== ') and line.endswith('=='):
                if 'język polski' not in line:
                    #create = False
                    break
            if line.startswith("''") and not defined:
                defined = True
                if "czasownik" in line or "rzeczownik" in line or "przymiotnik" in line or "przysłówek" in line or "przyimek" in line or "skrótowiec" in line:
                    if not "forma" in line and not "fraza" in line and not "skrót" in line:
                        create = True
                        # get part of speech
                        if "czasownik" in line:
                            category = "verb"
                            if "zwrotny" in line or " się" in base:
                                reflexive = True 
                        elif "rzeczownik" in line:
                            category = "noun"
                            if "rodzaj nijaki" in line:
                                genus = "N"
                            if "rodzaj męskoosobowy" in line:
                                genus = "MP"
                            if "rodzaj męskozwierzęcy" in line:
                                genus = "MZ"
                            if "rodzaj męskorzeczowy" in line:
                                genus = "MO"
                            if "rodzaj żeński" in line:
                                genus = "F"
                            if "liczba mnoga" in line:
                                if "rodzaj męskoosobowy" in line:
                                    genus = "M"
                                if "rodzaj niemęskoosobowy" in line:
                                    genus = "F"
                        elif "przymiotnik" in line:
                            category = "adjective"
                            adjCoutner +=1
                        elif "przysłówek" in line:
                            category = "adverb"
                            advCounter +=1
                        elif "przyimek" in line:
                            category = "prepositional"
                        elif "skrótowiec" in line:
                            category = "acronym"
                        else:
                            create = False
                            break
                            
            if category == "noun":
                if "nieodm-rzeczownik-polski" in line:
                    conj = False
                    for x in range(7):
                        for y in range(2):
                            noun_case_matrix[x][y] = base   
                    
                if "Mianownik" in line or "Dopełniacz" in line or "Celownik" in line or "Biernik" in line or "Narzędnik" in line or "Miejscownik" in line or "Wołacz" in line:
                    split_case = re.split(r'\W+', line)
                    if split_case[2] == "lp":
                        if split_case[1] == "Mianownik":
                            noun_case_matrix[0][0] = split_case[3]
                        if split_case[1] == "Dopełniacz":
                            noun_case_matrix[1][0] = split_case[3]
                        if split_case[1] == "Celownik":
                            noun_case_matrix[2][0] = split_case[3]
                        if split_case[1] == "Biernik":
                            noun_case_matrix[3][0] = split_case[3]
                        if split_case[1] == "Narzędnik":
                            noun_case_matrix[4][0] = split_case[3]
                        if split_case[1] == "Miejscownik":
                            noun_case_matrix[5][0] = split_case[3]
                        if split_case[1] == "Wołacz":
                            noun_case_matrix[6][0] = split_case[3]
                    elif split_case[2] == "lm":
                        if split_case[1] == "Mianownik":
                            noun_case_matrix[0][1] = split_case[3]
                        if split_case[1] == "Dopełniacz":
                            noun_case_matrix[1][1] = split_case[3]
                        if split_case[1] == "Celownik":
                            noun_case_matrix[2][1] = split_case[3]
                        if split_case[1] == "Biernik":
                            noun_case_matrix[3][1] = split_case[3]
                        if split_case[1] == "Narzędnik":
                            noun_case_matrix[4][1] = split_case[3]
                        if split_case[1] == "Miejscownik":
                            noun_case_matrix[5][1] = split_case[3]
                        if split_case[1] == "Wołacz":
                            noun_case_matrix[6][1] = split_case[3]
                    
            
            if category == "adjective":
                if "odmiana-przymiotnik-polski|" in line:
                    if "brak" in line:
                        no_comp = True
                        continue
                    if "bardziej" in line:
                        desc_comp = True
                        continue
                    split_comp = re.split(r'odmiana-przymiotnik-polski\W+',line)
                    comp_temp = re.split(r'\W',split_comp[1])
                    if comp_temp[0] != "":
                        comp = comp_temp[0]
                    else:
                        for x in comp_temp:
                            if x != "":
                                comp = x
                                break
                if "nieodm}}" in line:
                    no_comp = True
                    continue
                
                #POLISH WIKIPEDIA AUTOMATICALLY DECLINES ADJECTIVES
            
            
            if category == "adverb":
                if "niestopn}}" in line or "nieodm}}" in line:
                    no_comp = True
                    continue
                if "stopn|" in line:
                    split_comp = re.split(r'stopn\W+|}|[|]', line)
                    comp = split_comp[1]
                    sup = split_comp[2]
                    
            if category == "verb":
                if ("robię=" in line or "robię =" in line) and tpg_matrix[0][0] == "":
                    split_tense = re.split('robię=\W*|\W+', line)
                    tpg_matrix[0][0] = split_tense[2]
                if ("robi=" in line or "robi =" in line) and tpg_matrix[0][2] == "":
                    split_tense = re.split('robi=\W*|\W+', line)
                    tpg_matrix[0][2] = split_tense[2]
                if ("robią=" in line or "robią =" in line) and tpg_matrix[0][5] == "":
                    split_tense = re.split('robią=\W*|\W+', line)
                    tpg_matrix[0][5] = split_tense[2]
                if ("robiłem=" in line or "robiłem =" in line) and tpg_matrix[1][0][0] == "":
                    split_tense = re.split('robiłem=\W*|\W+', line)
                    tpg_matrix[1][0][0] = split_tense[2]
                if ("robił=" in line or "robił =" in line) and tpg_matrix[1][2][0] == "":
                    split_tense = re.split('robił=\W*|\W+', line)
                    tpg_matrix[1][2][0] = split_tense[2]
                if ("robiła=" in line or "robiła =" in line) and tpg_matrix[1][2][1] == "":
                    split_tense = re.split('robiła=\W*|\W+', line)
                    tpg_matrix[1][2][1] = split_tense[2]
                if ("robili=" in line or "robili =" in line) and tpg_matrix[1][5][0] == "":
                    split_tense = re.split('robili=\W*|\W+', line)
                    tpg_matrix[1][5][0] = split_tense[2]
                if ("robiono=" in line or "robiono =" in line) and p_less == "":
                    split_tense = re.split('robiono=\W*|\W+', line)
                    p_less = split_tense[2]
                if ("rób=" in line or "rób =" in line) and tpg_matrix[2][1] == "":
                    split_tense = re.split('rób=\W*|\W+', line)
                    tpg_matrix[2][1] = split_tense[2]
                if ("róbmy=" in line or "róbmy =" in line) and tpg_matrix[2][3] == "":
                    split_tense = re.split('róbmy=\W*|\W+', line)
                    tpg_matrix[2][3] = split_tense[2]
                if ("róbcie=" in line or "róbcie =" in line) and tpg_matrix[2][4] == "":
                    split_tense = re.split('róbcie=\W*|\W+', line)
                    tpg_matrix[2][4] = split_tense[2]
                if ("robiąc=" in line or "robiąc =" in line) and transgressive == "":
                    split_tense = re.split('robiąc=\W*|\W+', line)
                    transgressive = split_tense[2]
                if ("robiony=" in line or "robiony =" in line) and IPB[0][0] == "":
                    split_tense = re.split('robiony=\W*|\W+', line)
                    IPB[0][0] = split_tense[2]
                if ("robieni=" in line or "robieni =" in line) and IPB[0][1] == "":
                    split_tense = re.split('robieni=\W*|\W+', line)
                    IPB[1][0] = split_tense[2]
                if ("robiwszy=" in line or "robiwszy =" in line) and IPU == "":
                    split_tense = re.split('robiwszy=\W*|\W+', line)
                    IPU = split_tense[2]
                    
                #generate the rest...
                #for reference on formation:
                #robię* | robi + sz | robi* | robi + my | robi + cie | robią*
                    #robiłem*/łam/łom | robiła - a + eś/robiła + ś | robił*/robiła*/robiła - a + o | 
                    #robili* + śmy/robiły + śmy | robili + ście/robiły + ście | robili*/robiła - a + y
                        #niech + robię | rób* | niech + robi | róbmy* | róbcie* | niech + robią
                            #* - already given

                    
            # After that, word entry with interesting fields for lexicon should be completed
            if "{{przykłady}}" in line or "{{synonimy}}" in line:
                break
                
                
        if category == "verb":  
            tpg_matrix[0][1] = tpg_matrix[0][2] + "sz"
                
            tpg_matrix[0][3] = tpg_matrix[0][2] + "my"
            tpg_matrix[0][4] = tpg_matrix[0][2] + "cie"
                
            tpg_matrix[1][0][1] = tpg_matrix[1][0][0][:-2] + "am"
            tpg_matrix[1][1][0] = tpg_matrix[1][2][1][:-1] + "eś"
            tpg_matrix[1][1][1] = tpg_matrix[1][2][1] + "ś"
            tpg_matrix[1][2][2] = tpg_matrix[1][2][1][:-1] + "o"
                
            tpg_matrix[1][3][0] = tpg_matrix[1][5][0] + "śmy"
            tpg_matrix[1][4][0] = tpg_matrix[1][5][0] + "ście"
            tpg_matrix[1][5][1] = tpg_matrix[1][2][1][:-1] + "y"
            tpg_matrix[1][3][1] = tpg_matrix[1][5][1] + "śmy"
            tpg_matrix[1][4][1] = tpg_matrix[1][5][1] + "ście"
                
            tpg_matrix[2][0] = "niech " + tpg_matrix[0][0]
            tpg_matrix[2][2] = "niech " + tpg_matrix[0][2]
            if tpg_matrix[2][3] == "":
                tpg_matrix[2][3] = tpg_matrix[2][1] + "my"
            if tpg_matrix[2][4] == "":
                tpg_matrix[2][4] = tpg_matrix[2][1] + "cie"
            tpg_matrix[2][5] = "niech " + tpg_matrix[0][5]
                
            IPB[0][1] = IPB[0][0][:-1] + "a"
            IPB[0][2] = IPB[0][0][:-1] + "e"
            IPB[1][1] = IPB[0][0][:-1] + "e"
            IPB[1][2] = IPB[0][0][:-1] + "e"
                
            IPC[0][0] = transgressive + "y"
            IPC[0][1] = transgressive + "a"
            IPC[0][2] = transgressive + "e"
            IPC[1][0] = transgressive + "y"
            IPC[1][1] = transgressive + "e"
            IPC[1][2] = transgressive + "e"
            
            if reflexive:
                for x in range(3):
                    for y in range(6):
                        if x == 1:
                            if y < 3:
                                for z in range(3):
                                    tpg_matrix[x][y][z] = tpg_matrix[x][y][z] + " się"
                            else:
                                for z in range(2):
                                        
                                    tpg_matrix[x][y][z] = tpg_matrix[x][y][z] + " się"
                        else:
                            tpg_matrix[x][y] = tpg_matrix[x][y] + " się"
                
            if tpg_matrix[0][0] == "":
                fail_tenses = True
                for x in range(3):
                    for y in range(6):
                        if x == 1:
                            if y < 3:
                                for z in range(3):
                                    tpg_matrix[x][y][z] = "-"
                            else:
                                for z in range(2):
                                        
                                    tpg_matrix[x][y][z] = "-"
                        else:
                            tpg_matrix[x][y] = "-"
                
            
        
        if category == "noun":  
            if noun_case_matrix[0][0] == "" and noun_case_matrix[0][1] == "":
                for x in range(7):
                    for y in range(2):
                        noun_case_matrix[x][y] = "-"
                        
        if category == "adjective":
            
            if base[-1] == "y":
                adj_case_matrix[0][0] = base
                adj_case_matrix[0][1] = base
                adj_case_matrix[0][2] = base[:-1] + "a"
                adj_case_matrix[0][3] = base[:-1] + "e"
                
                adj_case_matrix[1][0] = base[:-1] + "ego"
                adj_case_matrix[1][1] = base[:-1] + "ego"
                adj_case_matrix[1][2] = base[:-1] + "ej"
                adj_case_matrix[1][3] = base[:-1] + "emu"
                
                adj_case_matrix[2][0] = base[:-1] + "emu"
                adj_case_matrix[2][1] = base[:-1] + "emu"
                adj_case_matrix[2][2] = base[:-1] + "ej"
                adj_case_matrix[2][3] = base[:-1] + "emu"
                
                adj_case_matrix[3][0] = base[:-1] + "ego"
                adj_case_matrix[3][1] = base
                adj_case_matrix[3][2] = base[:-1] + "ą"
                adj_case_matrix[3][3] = base[:-1] + "e"
                
                adj_case_matrix[4][0] = base + "m"
                adj_case_matrix[4][1] = base + "m"
                adj_case_matrix[4][2] = base[:-1] + "ą"
                adj_case_matrix[4][3] = base + "m"
                
                adj_case_matrix[5][0] = base + "m"
                adj_case_matrix[5][1] = base + "m"
                adj_case_matrix[5][2] = base[:-1] + "ej"
                adj_case_matrix[5][3] = base + "m"
                
                adj_case_matrix[6][0] = base
                adj_case_matrix[6][1] = base
                adj_case_matrix[6][2] = base[:-1] + "a"
                adj_case_matrix[6][3] = base[:-1] + "e"
                
                if base[-2] == "r":
                    adj_case_matrix[0][4] = base[:-1] + "zy"
                    adj_case_matrix[0][5] = base[:-1] + "e"
                elif base[-2] == "n":
                    adj_case_matrix[0][4] = base[:-1] + "ni"
                    adj_case_matrix[0][5] = base[:-1] + "e"
                elif base[-2] == "ł":
                    adj_case_matrix[0][4] = base[:-1] + "li"
                    adj_case_matrix[0][5] = base[:-1] + "e"
                    if base[-3] == "o":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "e" + adj_case_matrix[0][4][-2:]
                    if base[-3] == "z":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "ź" + adj_case_matrix[0][4][-2:]
                    if base[-3] == "s":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "ś" + adj_case_matrix[0][4][-2:]
                    if base[-3] == "c":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "ć" + adj_case_matrix[0][4][-2:]
                    if base[-3] == "ł":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "l" + adj_case_matrix[0][4][-2:]
                elif base[-2] == "z" and base[-3] == "c":
                    adj_case_matrix[0][4] = base
                    adj_case_matrix[0][5] = base[:-1] + "e"
                elif base[-2] == "w":
                    adj_case_matrix[0][4] = base[:-1] + "i"
                    adj_case_matrix[0][5] = base[:-1] + "e"
                else:
                    adj_case_matrix[0][4] = base[:-1] + "i"
                    adj_case_matrix[0][5] = base[:-1] + "e"
                        
                adj_case_matrix[1][4] = base + "ch"
                adj_case_matrix[1][5] = base + "ch"
                
                adj_case_matrix[2][4] = base + "m"
                adj_case_matrix[2][5] = base + "m"
                
                adj_case_matrix[3][4] = base + "ch"
                adj_case_matrix[3][5] = base[:-1] + "e"
                
                adj_case_matrix[4][4] = base + "mi"
                adj_case_matrix[4][5] = base + "mi"
                
                adj_case_matrix[5][4] = base + "ch"
                adj_case_matrix[5][5] = base + "ch"
                    
                adj_case_matrix[6][4] = adj_case_matrix[0][4]
                adj_case_matrix[6][5] = adj_case_matrix[0][5]
                    
            elif base[-1] == "i":
                adj_case_matrix[0][0] = base
                adj_case_matrix[0][1] = base
                adj_case_matrix[0][2] = base[:-1] + "a"
                adj_case_matrix[0][3] = base + "e"
                
                adj_case_matrix[1][0] = base + "ego"
                adj_case_matrix[1][1] = base + "ego"
                adj_case_matrix[1][2] = base + "ej"
                adj_case_matrix[1][3] = base + "emu"
                
                adj_case_matrix[2][0] = base + "emu"
                adj_case_matrix[2][1] = base + "emu"
                adj_case_matrix[2][2] = base + "ej"
                adj_case_matrix[2][3] = base + "emu"
                
                adj_case_matrix[3][0] = base + "ego"
                adj_case_matrix[3][1] = base
                adj_case_matrix[3][2] = base[:-1] + "ą"
                adj_case_matrix[3][3] = base + "e"
                
                adj_case_matrix[4][0] = base + "m"
                adj_case_matrix[4][1] = base + "m"
                adj_case_matrix[4][2] = base + "ą"
                adj_case_matrix[4][3] = base + "m"
                
                adj_case_matrix[5][0] = base + "m"
                adj_case_matrix[5][1] = base + "m"
                adj_case_matrix[5][2] = base + "ej"
                adj_case_matrix[5][3] = base + "m"
                
                adj_case_matrix[6][0] = base
                adj_case_matrix[6][1] = base
                adj_case_matrix[6][2] = base[:-1] + "a"
                adj_case_matrix[6][3] = base + "e"
                
                if base[-2] == "k":
                    adj_case_matrix[0][4] = base[:-1] + "cy"
                    adj_case_matrix[0][5] = base + "e"
                if base[-2] == "n":
                    adj_case_matrix[0][4] = base
                    adj_case_matrix[0][5] = base + "e"
                if base[-2] == "ł":
                    adj_case_matrix[0][4] = base[:-1] + "li"
                    adj_case_matrix[0][5] = base[:-1] + "e"
                    if base[-3] == "o":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "e" + adj_case_matrix[0][4][-2:]
                    if base[-3] == "z":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "ź" + adj_case_matrix[0][4][-2:]
                    if base[-3] == "s":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "ś" + adj_case_matrix[0][4][-2:]
                    if base[-3] == "c":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "ć" + adj_case_matrix[0][4][-2:]
                    if base[-3] == "ł":
                        adj_case_matrix[0][4] = adj_case_matrix[0][4][:-3] + "l" + adj_case_matrix[0][4][-2:]
                        
                adj_case_matrix[1][4] = base + "ch"
                adj_case_matrix[1][5] = base + "ch"
                
                adj_case_matrix[2][4] = base + "m"
                adj_case_matrix[2][5] = base + "m"
                
                adj_case_matrix[3][4] = base + "ch"
                adj_case_matrix[3][5] = base + "e"
                
                adj_case_matrix[4][4] = base + "mi"
                adj_case_matrix[4][5] = base + "mi"
                
                adj_case_matrix[5][4] = base + "ch"
                adj_case_matrix[5][5] = base + "ch"
                    
                adj_case_matrix[6][4] = adj_case_matrix[0][4]
                adj_case_matrix[6][5] = adj_case_matrix[0][5]
            
            else:
                for x in range(7):
                    for y in range(6):
                        adj_case_matrix[x][y] = "-"
            
            if adj_case_matrix[0][0] != "-":
                        
                if comp[-1] == "y" and not no_comp:
                    adj_case_matrix_comp[0][0] = comp
                    adj_case_matrix_comp[0][1] = comp
                    adj_case_matrix_comp[0][2] = comp[:-1] + "a"
                    adj_case_matrix_comp[0][3] = comp[:-1] + "e"

                    adj_case_matrix_comp[1][0] = comp[:-1] + "ego"
                    adj_case_matrix_comp[1][1] = comp[:-1] + "ego"
                    adj_case_matrix_comp[1][2] = comp[:-1] + "ej"
                    adj_case_matrix_comp[1][3] = comp[:-1] + "emu"

                    adj_case_matrix_comp[2][0] = comp[:-1] + "emu"
                    adj_case_matrix_comp[2][1] = comp[:-1] + "emu"
                    adj_case_matrix_comp[2][2] = comp[:-1] + "ej"
                    adj_case_matrix_comp[2][3] = comp[:-1] + "emu"

                    adj_case_matrix_comp[3][0] = comp[:-1] + "ego"
                    adj_case_matrix_comp[3][1] = comp
                    adj_case_matrix_comp[3][2] = comp[:-1] + "ą"
                    adj_case_matrix_comp[3][3] = comp[:-1] + "e"

                    adj_case_matrix_comp[4][0] = comp + "m"
                    adj_case_matrix_comp[4][1] = comp + "m"
                    adj_case_matrix_comp[4][2] = comp[:-1] + "ą"
                    adj_case_matrix_comp[4][3] = comp + "m"

                    adj_case_matrix_comp[5][0] = comp + "m"
                    adj_case_matrix_comp[5][1] = comp + "m"
                    adj_case_matrix_comp[5][2] = comp[:-1] + "ej"
                    adj_case_matrix_comp[5][3] = comp + "m"

                    adj_case_matrix_comp[6][0] = comp
                    adj_case_matrix_comp[6][1] = comp
                    adj_case_matrix_comp[6][2] = comp[:-1] + "a"
                    adj_case_matrix_comp[6][3] = comp[:-1] + "e"

                    if comp[-2] == "r":
                        adj_case_matrix_comp[0][4] = comp[:-1] + "zy"
                        adj_case_matrix_comp[0][5] = base[:-1] + "e"
                    elif comp[-2] == "n":
                        adj_case_matrix_comp[0][4] = comp[:-1] + "ni"
                        adj_case_matrix_comp[0][5] = comp[:-1] + "e"
                    elif comp[-2] == "ł":
                        adj_case_matrix_comp[0][4] = comp[:-1] + "li"
                        adj_case_matrix_comp[0][5] = comp[:-1] + "e"
                        if comp[-3] == "o":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "e" + adj_case_matrix_comp[0][4][-2:]
                        if comp[-3] == "z":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "ź" + adj_case_matrix_comp[0][4][-2:]
                        if comp[-3] == "s":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "ś" + adj_case_matrix_comp[0][4][-2:]
                        if comp[-3] == "c":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "ć" + adj_case_matrix_comp[0][4][-2:]
                        if comp[-3] == "ł":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "l" + adj_case_matrix_comp[0][4][-2:]
                    elif comp[-2] == "z" and comp[-3] == "c":
                        adj_case_matrix_comp[0][4] = comp
                        adj_case_matrix_comp[0][5] = comp[:-1] + "e"
                    elif comp[-2] == "z" and comp[-3] == "s":
                        adj_case_matrix_comp[0][4] = comp[:-2] + "i"
                        adj_case_matrix_comp[0][5] = comp[:-1] + "e"
                    elif comp[-2] == "w":
                        adj_case_matrix_comp[0][4] = comp[:-1] + "i"
                        adj_case_matrix_comp[0][5] = comp[:-1] + "e"
                    else:
                        adj_case_matrix_comp[0][4] = comp[:-1] + "i"
                        adj_case_matrix_comp[0][5] = comp[:-1] + "e"

                    adj_case_matrix_comp[1][4] = comp + "ch"
                    adj_case_matrix_comp[1][5] = comp + "ch"

                    adj_case_matrix_comp[2][4] = comp + "m"
                    adj_case_matrix_comp[2][5] = comp + "m"

                    adj_case_matrix_comp[3][4] = comp + "ch"
                    adj_case_matrix_comp[3][5] = comp[:-1] + "e"

                    adj_case_matrix_comp[4][4] = comp + "mi"
                    adj_case_matrix_comp[4][5] = comp + "mi"

                    adj_case_matrix_comp[5][4] = comp + "ch"
                    adj_case_matrix_comp[5][5] = comp + "ch"

                    adj_case_matrix_comp[6][4] = adj_case_matrix_comp[0][4]
                    adj_case_matrix_comp[6][5] = adj_case_matrix_comp[0][5]

                elif comp[-1] == "i" and not no_comp:
                    adj_case_matrix_comp[0][0] = comp
                    adj_case_matrix_comp[0][1] = comp
                    adj_case_matrix_comp[0][2] = comp[:-1] + "a"
                    adj_case_matrix_comp[0][3] = comp + "e"

                    adj_case_matrix_comp[1][0] = comp + "ego"
                    adj_case_matrix_comp[1][1] = comp + "ego"
                    adj_case_matrix_comp[1][2] = comp + "ej"
                    adj_case_matrix_comp[1][3] = comp + "emu"

                    adj_case_matrix_comp[2][0] = comp + "emu"
                    adj_case_matrix_comp[2][1] = comp + "emu"
                    adj_case_matrix_comp[2][2] = comp + "ej"
                    adj_case_matrix_comp[2][3] = comp + "emu"

                    adj_case_matrix_comp[3][0] = comp + "ego"
                    adj_case_matrix_comp[3][1] = comp
                    adj_case_matrix_comp[3][2] = comp[:-1] + "ą"
                    adj_case_matrix_comp[3][3] = comp + "e"

                    adj_case_matrix_comp[4][0] = comp + "m"
                    adj_case_matrix_comp[4][1] = comp + "m"
                    adj_case_matrix_comp[4][2] = comp + "ą"
                    adj_case_matrix_comp[4][3] = comp + "m"

                    adj_case_matrix_comp[5][0] = comp + "m"
                    adj_case_matrix_comp[5][1] = comp + "m"
                    adj_case_matrix_comp[5][2] = comp + "ej"
                    adj_case_matrix_comp[5][3] = comp + "m"

                    adj_case_matrix_comp[6][0] = comp
                    adj_case_matrix_comp[6][1] = comp
                    adj_case_matrix_comp[6][2] = comp[:-1] + "a"
                    adj_case_matrix_comp[6][3] = comp + "e"

                    if comp[-2] == "k":
                        adj_case_matrix_comp[0][4] = comp[:-1] + "cy"
                        adj_case_matrix_comp[0][5] = comp + "e"
                    if comp[-2] == "n":
                        adj_case_matrix_comp[0][4] = comp
                        adj_case_matrix_comp[0][5] = comp + "e"
                    if comp[-2] == "ł":
                        adj_case_matrix_comp[0][4] = comp[:-1] + "li"
                        adj_case_matrix_comp[0][5] = comp[:-1] + "e"
                        if comp[-3] == "o":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "e" + adj_case_matrix_comp[0][4][-2:]
                        if comp[-3] == "z":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "ź" + adj_case_matrix_comp[0][4][-2:]
                        if comp[-3] == "s":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "ś" + adj_case_matrix_comp[0][4][-2:]
                        if comp[-3] == "c":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "ć" + adj_case_matrix_comp[0][4][-2:]
                        if comp[-3] == "ł":
                            adj_case_matrix_comp[0][4] = adj_case_matrix_comp[0][4][:-3] + "l" + adj_case_matrix_comp[0][4][-2:]

                    adj_case_matrix_comp[1][4] = comp + "ch"
                    adj_case_matrix_comp[1][5] = comp + "ch"

                    adj_case_matrix_comp[2][4] = comp + "m"
                    adj_case_matrix_comp[2][5] = comp + "m"

                    adj_case_matrix_comp[3][4] = comp + "ch"
                    adj_case_matrix_comp[3][5] = comp + "e"

                    adj_case_matrix_comp[4][4] = comp + "mi"
                    adj_case_matrix_comp[4][5] = comp + "mi"

                    adj_case_matrix_comp[5][4] = comp + "ch"
                    adj_case_matrix_comp[5][5] = comp + "ch"

                    adj_case_matrix_comp[6][4] = adj_case_matrix_comp[0][4]
                    adj_case_matrix_comp[6][5] = adj_case_matrix_comp[0][5]
                else:
                    for x in range(7):
                        for y in range(6):
                            adj_case_matrix_comp[x][y] = "bardziej " + adj_case_matrix[x][y]

                if adj_case_matrix_comp[0][0] == adj_case_matrix[0][0]:
                    for x in range(7):
                        for y in range(6):
                            adj_case_matrix_comp[x][y] = "bardziej " + adj_case_matrix[x][y]

                if not no_comp:
                    for x in range(7):
                        for y in range(6):
                            adj_case_matrix_sup[x][y] = "naj" + adj_case_matrix_comp[x][y]            
            
                        
        if comp == "":
            comp = "-"
            sup = "-"
                
        if create:
            if category == "verb":
                verbsCounter += 1
                # if word already exists, i.e. was created by a flexion entry
                searchstring = './/base[text()="' + base + '"]'
                if len(lexicon.xpath(searchstring)) > 0:
                    if lexicon.xpath(searchstring)[0].text == base:
                        # print("Base word: " + base + " already exists in lexikon! Enrich existing entry.")
                        # find existing entry
                        searchstringParent = './/base[text()="' + base + '"]/..'
                        word = lexicon.xpath(searchstringParent)[0]
                        # print(ET.tostring(word, pretty_print = True))
                else:
                # word does not yet exist, create new entry
                    # print(base + " does not yet exist. Create new entry.")
                    word = ET.SubElement(lexicon, 'word')
                    baseXML = ET.SubElement(word, 'base')
                    baseXML.text = base
                    idXML = ET.SubElement(word, 'id')
                    idXML.text = str(wordID)
                    wordID += 1
            
                pres1sinXML = ET.SubElement(word, 'present_sin_1')
                pres2sinXML = ET.SubElement(word, 'present_sin_2')
                pres3sinXML = ET.SubElement(word, 'present_sin_3')
                pres1plXML = ET.SubElement(word, 'present_pl_1')
                pres2plXML = ET.SubElement(word, 'present_pl_2')
                pres3plXML = ET.SubElement(word, 'present_pl_3')
                
                pres1sinXML.text = tpg_matrix[0][0]
                pres2sinXML.text = tpg_matrix[0][1]
                pres3sinXML.text = tpg_matrix[0][2]
                pres1plXML.text = tpg_matrix[0][3]
                pres2plXML.text = tpg_matrix[0][4]
                pres3plXML.text = tpg_matrix[0][5]
                
                comm1sinXML = ET.SubElement(word, 'command_sin_1')
                comm2sinXML = ET.SubElement(word, 'command_sin_2')
                comm3sinXML = ET.SubElement(word, 'command_sin_3')
                comm1plXML = ET.SubElement(word, 'command_pl_1')
                comm2plXML = ET.SubElement(word, 'command_pl_2')
                comm3plXML = ET.SubElement(word, 'command_pl_3')

                comm1sinXML.text = tpg_matrix[2][0]
                comm2sinXML.text = tpg_matrix[2][1]
                comm3sinXML.text = tpg_matrix[2][2]
                comm1plXML.text = tpg_matrix[2][3]
                comm2plXML.text = tpg_matrix[2][4]
                comm3plXML.text = tpg_matrix[2][5]
                
                
                past1sinXMLm = ET.SubElement(word, 'past_sin_1_m')
                past1sinXMLf = ET.SubElement(word, 'past_sin_1_f')
                past1sinXMLn = ET.SubElement(word, 'past_sin_1_n')
                past1sinXMLm.text = tpg_matrix[1][0][0]
                past1sinXMLf.text = tpg_matrix[1][0][1]
                past1sinXMLn.text = tpg_matrix[1][0][2]
                
                past2sinXMLm = ET.SubElement(word, 'past_sin_2_m')
                past2sinXMLf = ET.SubElement(word, 'past_sin_2_f')
                past2sinXMLn = ET.SubElement(word, 'past_sin_2_n')
                past2sinXMLm.text = tpg_matrix[1][1][0]
                past2sinXMLf.text = tpg_matrix[1][1][1]
                past2sinXMLn.text = tpg_matrix[1][1][2]
                
                past3sinXMLm = ET.SubElement(word, 'past_sin_3_m')
                past3sinXMLf = ET.SubElement(word, 'past_sin_3_f')
                past3sinXMLn = ET.SubElement(word, 'past_sin_3_n')
                past3sinXMLm.text = tpg_matrix[1][2][0]
                past3sinXMLf.text = tpg_matrix[1][2][1]
                past3sinXMLn.text = tpg_matrix[1][2][2]
                
                past1plXMLmp = ET.SubElement(word, 'past_pl_1_m')
                past1plXMLnm = ET.SubElement(word, 'past_pl_1_f')
                past1plXMLmp.text = tpg_matrix[1][3][0]
                past1plXMLnm.text = tpg_matrix[1][3][1]
                
                past2plXMLmp = ET.SubElement(word, 'past_pl_2_m')
                past2plXMLnm = ET.SubElement(word, 'past_pl_2_f')
                past2plXMLmp.text = tpg_matrix[1][4][0]
                past2plXMLnm.text = tpg_matrix[1][4][1]
                
                past3plXMLmp = ET.SubElement(word, 'past_pl_3_m')
                past3plXMLnm = ET.SubElement(word, 'past_pl_3_f')
                past3plXMLmp.text = tpg_matrix[1][5][0]
                past3plXMLnm.text = tpg_matrix[1][5][1]
                
                if IPB[0][0] != "" and IPB[0][0] != "a":

                    ipbsinm = ET.SubElement(word, 'ipb_sin_m')
                    ipbsinf = ET.SubElement(word, 'ipb_sin_f')
                    ipbsinn = ET.SubElement(word, 'ipb_sin_n')
                    ipbsinm.text = IPB[0][0]
                    ipbsinf.text = IPB[0][1]
                    ipbsinn.text = IPB[0][2]

                    ipbplmp = ET.SubElement(word, 'ipb_pl_m')
                    ipbplnm = ET.SubElement(word, 'ipb_pl_f')
                    ipbplmp.text = IPB[1][0]
                    ipbplnm.text = IPB[1][1]
                
                if IPC[0][0] != "y":

                    ipcsinm = ET.SubElement(word, 'ipc_sin_m')
                    ipcsinf = ET.SubElement(word, 'ipc_sin_f')
                    ipcsinn = ET.SubElement(word, 'ipc_sin_n')
                    ipcsinm.text = IPC[0][0]
                    ipcsinf.text = IPC[0][1]
                    ipcsinn.text = IPC[0][2]

                    ipcplmp = ET.SubElement(word, 'ipc_pl_m')
                    ipcplnm = ET.SubElement(word, 'ipc_pl_f')
                    ipcplmp.text = IPC[1][0]
                    ipcplnm.text = IPC[1][1]
                
                if transgressive !=  "":
                    
                    transgressiveXML = ET.SubElement(word, 'transgressive')
                    transgressiveXML.text = transgressive
                
                if IPU != "":
                    ipuXML = ET.SubElement(word, 'ipu')
                    ipuXML.text = IPU
                
                
            else:
                # non-verbs
                word = ET.SubElement(lexicon, 'word')
                baseXML = ET.SubElement(word, 'base')
                baseXML.text = base
                idXML = ET.SubElement(word, 'id')
                idXML.text = str(wordID)
                wordID += 1

            categoryXML = ET.SubElement(word, 'category')
            categoryXML.text = category   
                
            if category == "noun":
                nounsCounter += 1
                if genus != "":
                    genusXML = ET.SubElement(word, 'genus')
                    genusXML.text = genus
                mianownik_sin = ET.SubElement(word, 'm_sin')
                mianownik_sin.text = noun_case_matrix[0][0]
                dopełniacz_sin = ET.SubElement(word, 'd_sin')
                dopełniacz_sin.text = noun_case_matrix[1][0]
                celownik_sin = ET.SubElement(word, 'c_sin')
                celownik_sin.text = noun_case_matrix[2][0]
                biernik_sin = ET.SubElement(word, 'b_sin')
                biernik_sin.text = noun_case_matrix[3][0]
                narzędnik_sin = ET.SubElement(word, 'n_sin')
                narzędnik_sin.text = noun_case_matrix[4][0]
                miejscownik_sin = ET.SubElement(word, 'msc_sin')
                miejscownik_sin.text = noun_case_matrix[5][0]
                wołacz_sin = ET.SubElement(word, 'w_sin')
                wołacz_sin.text = noun_case_matrix[6][0]
                
                mianownik_pl = ET.SubElement(word, 'm_pl')
                mianownik_pl.text = noun_case_matrix[0][1]
                dopełniacz_pl = ET.SubElement(word, 'd_pl')
                dopełniacz_pl.text = noun_case_matrix[1][1]
                celownik_pl = ET.SubElement(word, 'c_pl')
                celownik_pl.text = noun_case_matrix[2][1]
                biernik_pl = ET.SubElement(word, 'b_pl')
                biernik_pl.text = noun_case_matrix[3][1]
                narzędnik_pl = ET.SubElement(word, 'n_pl')
                narzędnik_pl.text = noun_case_matrix[4][1]
                miejscownik_pl = ET.SubElement(word, 'msc_pl')
                miejscownik_pl.text = noun_case_matrix[5][1]
                wołacz_pl = ET.SubElement(word, 'w_pl')
                wołacz_pl.text = noun_case_matrix[6][1]
                
            if category == "adjective":
                m = ET.SubElement(word, 'm_sin_m')
                f = ET.SubElement(word, 'm_sin_f')
                n = ET.SubElement(word, 'm_sin_n')
                m.text = adj_case_matrix[0][0]
                f.text = adj_case_matrix[0][2]
                n.text = adj_case_matrix[0][3]
                
                m = ET.SubElement(word, 'd_sin_m')
                f = ET.SubElement(word, 'd_sin_f')
                n = ET.SubElement(word, 'd_sin_n')
                m.text = adj_case_matrix[1][0]
                f.text = adj_case_matrix[1][2]
                n.text = adj_case_matrix[1][3]
                
                m = ET.SubElement(word, 'c_sin_m')
                f = ET.SubElement(word, 'c_sin_f')
                n = ET.SubElement(word, 'c_sin_n')
                m.text = adj_case_matrix[2][0]
                f.text = adj_case_matrix[2][2]
                n.text = adj_case_matrix[2][3]
                
                mp = ET.SubElement(word, 'b_sin_m_p')
                mo = ET.SubElement(word, 'b_sin_m_o')
                f = ET.SubElement(word, 'b_sin_f')
                n = ET.SubElement(word, 'b_sin_n')
                mp.text = adj_case_matrix[3][0]
                mo.text = adj_case_matrix[3][1]
                f.text = adj_case_matrix[3][2]
                n.text = adj_case_matrix[3][3]
                
                m = ET.SubElement(word, 'n_sin_m')
                f = ET.SubElement(word, 'n_sin_f')
                n = ET.SubElement(word, 'n_sin_n')
                m.text = adj_case_matrix[4][0]
                f.text = adj_case_matrix[4][2]
                n.text = adj_case_matrix[4][3]
                
                m = ET.SubElement(word, 'msc_sin_m')
                f = ET.SubElement(word, 'msc_sin_f')
                n = ET.SubElement(word, 'msc_sin_n')
                m.text = adj_case_matrix[5][0]
                f.text = adj_case_matrix[5][2]
                n.text = adj_case_matrix[5][3]
                
                m = ET.SubElement(word, 'w_sin_m')
                f = ET.SubElement(word, 'w_sin_f')
                n = ET.SubElement(word, 'w_sin_n')
                m.text = adj_case_matrix[6][0]
                f.text = adj_case_matrix[6][2]
                n.text = adj_case_matrix[6][3]
                
                mp = ET.SubElement(word, 'm_pl_m')
                nm = ET.SubElement(word, 'm_pl_f')
                mp.text = adj_case_matrix[0][4]
                nm.text = adj_case_matrix[0][5]
                    
                dopełniacz = ET.SubElement(word, 'd_pl')
                dopełniacz.text = adj_case_matrix[1][4]
                    
                celownik = ET.SubElement(word, 'c_pl')
                celownik.text = adj_case_matrix[2][4]
                
                mp = ET.SubElement(word, 'b_pl_m')
                nm = ET.SubElement(word, 'b_pl_f')
                mp.text = adj_case_matrix[3][4]
                nm.text = adj_case_matrix[3][5]
            
                narzędnik = ET.SubElement(word, 'n_pl')
                narzędnik.text = adj_case_matrix[4][4]
                
                miejscownik = ET.SubElement(word, 'msc_pl')
                miejscownik.text = adj_case_matrix[5][4]
                
                mp = ET.SubElement(word, 'w_pl_m')
                nm = ET.SubElement(word, 'w_pl_f')
                mp.text = adj_case_matrix[6][4]
                nm.text = adj_case_matrix[6][5]
                
                if not no_comp:
                    m = ET.SubElement(word, 'm_sin_m_comp')
                    f = ET.SubElement(word, 'm_sin_f_comp')
                    n = ET.SubElement(word, 'm_sin_n_comp')
                    m.text = adj_case_matrix_comp[0][0]
                    f.text = adj_case_matrix_comp[0][2]
                    n.text = adj_case_matrix_comp[0][3]
                    
                    m = ET.SubElement(word, 'd_sin_m_comp')
                    f = ET.SubElement(word, 'd_sin_f_comp')
                    n = ET.SubElement(word, 'd_sin_n_comp')
                    m.text = adj_case_matrix_comp[1][0]
                    f.text = adj_case_matrix_comp[1][2]
                    n.text = adj_case_matrix_comp[1][3]
                    
                    m = ET.SubElement(word, 'c_sin_m_comp')
                    f = ET.SubElement(word, 'c_sin_f_comp')
                    n = ET.SubElement(word, 'c_sin_n_comp')
                    m.text = adj_case_matrix_comp[2][0]
                    f.text = adj_case_matrix_comp[2][2]
                    n.text = adj_case_matrix_comp[2][3]
                    
                    mp = ET.SubElement(word, 'b_sin_m_p_comp')
                    mo = ET.SubElement(word, 'b_sin_m_o_comp')
                    f = ET.SubElement(word, 'b_sin_f_comp')
                    n = ET.SubElement(word, 'b_sin_n_comp')
                    mp.text = adj_case_matrix_comp[3][0]
                    mo.text = adj_case_matrix_comp[3][1]
                    f.text = adj_case_matrix_comp[3][2]
                    n.text = adj_case_matrix_comp[3][3]
                    
                    m = ET.SubElement(word, 'n_sin_m_comp')
                    f = ET.SubElement(word, 'n_sin_f_comp')
                    n = ET.SubElement(word, 'n_sin_n_comp')
                    m.text = adj_case_matrix_comp[4][0]
                    f.text = adj_case_matrix_comp[4][2]
                    n.text = adj_case_matrix_comp[4][3]
                    
                    m = ET.SubElement(word, 'msc_sin_m_comp')
                    f = ET.SubElement(word, 'msc_sin_f_comp')
                    n = ET.SubElement(word, 'msc_sin_n_comp')
                    m.text = adj_case_matrix_comp[5][0]
                    f.text = adj_case_matrix_comp[5][2]
                    n.text = adj_case_matrix_comp[5][3]
                    
                    m = ET.SubElement(word, 'w_sin_m_comp')
                    f = ET.SubElement(word, 'w_sin_f_comp')
                    n = ET.SubElement(word, 'w_sin_n_comp')
                    m.text = adj_case_matrix_comp[6][0]
                    f.text = adj_case_matrix_comp[6][2]
                    n.text = adj_case_matrix_comp[6][3]
                    
                    mp = ET.SubElement(word, 'm_pl_m_comp')
                    nm = ET.SubElement(word, 'm_pl_f_comp')
                    mp.text = adj_case_matrix_comp[0][4]
                    nm.text = adj_case_matrix_comp[0][5]
                    
                    dopełniacz = ET.SubElement(word, 'd_pl_comp')
                    dopełniacz.text = adj_case_matrix_comp[1][4]
                    
                    celownik = ET.SubElement(word, 'c_pl_comp')
                    celownik.text = adj_case_matrix_comp[2][4]
                    
                    mp = ET.SubElement(word, 'b_pl_m_comp')
                    nm = ET.SubElement(word, 'b_pl_f_comp')
                    mp.text = adj_case_matrix_comp[3][4]
                    nm.text = adj_case_matrix_comp[3][5]
                    
                    narzędnik = ET.SubElement(word, 'n_pl_comp')
                    narzędnik.text = adj_case_matrix_comp[4][4]
                    
                    miejscownik = ET.SubElement(word, 'msc_pl_comp')
                    miejscownik.text = adj_case_matrix_comp[5][4]
                    
                    mp = ET.SubElement(word, 'w_pl_m_comp')
                    nm = ET.SubElement(word, 'w_pl_f_comp')
                    mp.text = adj_case_matrix_comp[6][4]
                    nm.text = adj_case_matrix_comp[6][5]
                    
                    m = ET.SubElement(word, 'm_sin_m_sup')
                    f = ET.SubElement(word, 'm_sin_f_sup')
                    n = ET.SubElement(word, 'm_sin_n_sup')
                    m.text = adj_case_matrix_sup[0][0]
                    f.text = adj_case_matrix_sup[0][2]
                    n.text = adj_case_matrix_sup[0][3]
                    
                    m = ET.SubElement(word, 'd_sin_m_sup')
                    f = ET.SubElement(word, 'd_sin_f_sup')
                    n = ET.SubElement(word, 'd_sin_n_sup')
                    m.text = adj_case_matrix_sup[1][0]
                    f.text = adj_case_matrix_sup[1][2]
                    n.text = adj_case_matrix_sup[1][3]
                    
                    m = ET.SubElement(word, 'c_sin_m_sup')
                    f = ET.SubElement(word, 'c_sin_f_sup')
                    n = ET.SubElement(word, 'c_sin_n_sup')
                    m.text = adj_case_matrix_sup[2][0]
                    f.text = adj_case_matrix_sup[2][2]
                    n.text = adj_case_matrix_sup[2][3]
                    
                    mp = ET.SubElement(word, 'b_sin_m_p_sup')
                    mo = ET.SubElement(word, 'b_sin_m_o_sup')
                    f = ET.SubElement(word, 'b_sin_f_sup')
                    n = ET.SubElement(word, 'b_sin_n_sup')
                    mp.text = adj_case_matrix_sup[3][0]
                    mo.text = adj_case_matrix_sup[3][1]
                    f.text = adj_case_matrix_sup[3][2]
                    n.text = adj_case_matrix_sup[3][3]
                    
                    m = ET.SubElement(word, 'n_sin_m_sup')
                    f = ET.SubElement(word, 'n_sin_f_sup')
                    n = ET.SubElement(word, 'n_sin_n_sup')
                    m.text = adj_case_matrix_sup[4][0]
                    f.text = adj_case_matrix_sup[4][2]
                    n.text = adj_case_matrix_sup[4][3]
                    
                    m = ET.SubElement(word, 'msc_sin_m_sup')
                    f = ET.SubElement(word, 'msc_sin_f_sup')
                    n = ET.SubElement(word, 'msc_sin_n_sup')
                    m.text = adj_case_matrix_sup[5][0]
                    f.text = adj_case_matrix_sup[5][2]
                    n.text = adj_case_matrix_sup[5][3]
                    
                    m = ET.SubElement(word, 'w_sin_m_sup')
                    f = ET.SubElement(word, 'w_sin_f_sup')
                    n = ET.SubElement(word, 'w_sin_n_sup')
                    m.text = adj_case_matrix_sup[6][0]
                    f.text = adj_case_matrix_sup[6][2]
                    n.text = adj_case_matrix_sup[6][3]
                    
                    mp = ET.SubElement(word, 'm_pl_m_sup')
                    nm = ET.SubElement(word, 'm_pl_f_sup')
                    mp.text = adj_case_matrix_sup[0][4]
                    nm.text = adj_case_matrix_sup[0][5]
                    
                    dopełniacz = ET.SubElement(word, 'd_pl_sup')
                    dopełniacz.text = adj_case_matrix_sup[1][4]
                    
                    celownik = ET.SubElement(word, 'c_pl_sup')
                    celownik.text = adj_case_matrix_sup[2][4]
                    
                    mp = ET.SubElement(word, 'b_pl_m_sup')
                    nm = ET.SubElement(word, 'b_pl_f_sup')
                    mp.text = adj_case_matrix_sup[3][4]
                    nm.text = adj_case_matrix_sup[3][5]
                    
                    narzędnik = ET.SubElement(word, 'n_pl_sup')
                    narzędnik.text = adj_case_matrix_sup[4][4]
                    
                    miejscownik = ET.SubElement(word, 'msc_pl_sup')
                    miejscownik.text = adj_case_matrix_sup[5][4]
                    
                    mp = ET.SubElement(word, 'w_pl_m_sup')
                    nm = ET.SubElement(word, 'w_pl_f_sup')
                    mp.text = adj_case_matrix_sup[6][4]
                    nm.text = adj_case_matrix_sup[6][5]
            
            if category == "adverb":
                compXML = ET.SubElement(word, 'comp')
                compXML.text = comp
                supXML = ET.SubElement(word, 'sup')
                supXML.text = comp
            
        print (wordID, end="\r")
               
    # Write new lexicon to file
    tree = ET.ElementTree(lexicon)
    tree.write('wiktionary-lexicon-6.xml', pretty_print=True, xml_declaration=True, encoding="utf-8")
    print("Done. Number of entries: " + str(wordID-1))
    print("Number of nouns: " + str(nounsCounter))
    print("Number of verbs: " + str(verbsCounter))
    print("Number of adjectives: " + str(adjCoutner))
    print("Number of adverbs: " + str(advCounter))
       
    
parseWiktionary('plwiktionary.xml')

