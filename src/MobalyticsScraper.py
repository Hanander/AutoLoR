import os
import time

import numpy as np
import pandas as pd

from PIL import Image

import io
import json
import requests
from selenium import webdriver

from Cards import Card    

class MobalyticsScraper:
    # ------------------------------------------------------------------------------------------------------------------
    # Const vars
    _START_PAGE = 'https://lor.mobalytics.gg/cards'

    _FIRST_CARD_CLASS = 'linkstyles__InternalLink-sc-1ddk6s0-1.kWVUtj.cardstyles__CardWrapper-sc-1soldd6-0.bBRVyy'
    _NEXT_CARD_CLASS = 'base-buttonstyles__BaseButton-x8lzus-0.hufmpG.card-infostyles__NextCard-sc-1gwxo1f-13.crgpOR'
    _PREV_CARD_CLASS = 'base-buttonstyles__BaseButton-x8lzus-0.hufmpG.card-infostyles__PrevCard-sc-1gwxo1f-14.hUUZPg'
    _DELAY_BETWEEN_PARSE = 1

    _CARD_TITLE_CLASS = 'text__Text36x500-l0hs2y-1.headerstyles__Title-sc-1j3vndq-3.bDkYqw'
    # region, type, rarity
    _CARD_MAIN_CLASS = 'card-infostyles__Label-sc-1gwxo1f-6.cMhlng'
    # health, attack
    _CARD_STATS_CLASS = 'text__Text20x500-l0hs2y-6.card-infostyles__CardStrength-sc-1gwxo1f-10.NWojM'
    _CARD_ABILITIES_CLASS = 'text__Text14x400-l0hs2y-12.keyword-with-descriptionstyles__KeywordName-sc-10e0wo5-0.pNlag'
    _CARD_IMG_CLASS = 'base-imagecomponent__Image-sc-16xmea5-1.fksMOd.lozad'
    _CARD_ASSOCIATED_BOX = 'h-boxstyles__HBoxStartStart-ug1ouj-0.h-boxstyles__HBoxCenterCenter-ug1ouj-5.kEeqYc'
    

    # ------------------------------------------------------------------------------------------------------------------
    # Public methods

    @staticmethod
    def CollectData(outputFolderPath, chromeDriverPath):
        MobalyticsScraper._CreateOutFolder(outputFolderPath)

        driver = MobalyticsScraper._StartChromeDriver(chromeDriverPath)
        driver.get(MobalyticsScraper._START_PAGE)
        cards = MobalyticsScraper._CollectCardsInfo(driver)
        driver.close()
        
        MobalyticsScraper._CollectCardsImg(outputFolderPath, cards)

        cardsJSON = {}
        for card in cards:
            cardsJSON[card.id] = card.info 
        
        outputInfoPath = os.path.join(outputFolderPath, 'cards_info.json')
        with open(outputInfoPath, 'w') as f:
            json.dump(cardsJSON, f, indent=4)

    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    @staticmethod
    def _CreateOutFolder(outputFolderPath):
        assert os.path.exists(outputFolderPath)
        imgFolderPath = os.path.join(outputFolderPath, 'img')
        if not os.path.exists(imgFolderPath):
            os.mkdir(imgFolderPath)

    @staticmethod
    def _CollectCardsInfo(driver):
        MobalyticsScraper._OpenFirstCard(driver)
        cards = []
        while True:
            # get list cards (many if card has associated)
            cards += MobalyticsScraper._ParseCard(driver)
            if not MobalyticsScraper._ClickButton(driver, MobalyticsScraper._NEXT_CARD_CLASS):
                break 
            driver.refresh()
        
        return cards

    @staticmethod
    def _CollectCardsImg(outputFolderPath, cards):
        for card in cards:
            response = requests.get(card.info['img link'])
            img = Image.open(io.BytesIO(response.content))
            imgPath = os.path.join(outputFolderPath, 'img', '{}.png'.format(card.info['title']))
            img.save(imgPath, 'PNG')

    @staticmethod
    def _FindReqElements(driver, className):
        while True:
            elements = driver.find_elements_by_class_name(className)
            if len (elements) != 0:
                break
            time.sleep(MobalyticsScraper._DELAY_BETWEEN_PARSE)
        return elements

    @staticmethod
    def _ParseCard(driver, isAssociated=False):
        time.sleep(MobalyticsScraper._DELAY_BETWEEN_PARSE)
        associatedCards = []
        cardsNumber = 1
        i = 0
        while i < cardsNumber:
            # check associated cards
            associatedBox = MobalyticsScraper._FindReqElements(driver, MobalyticsScraper._CARD_ASSOCIATED_BOX)
            childs = associatedBox[0].find_elements_by_css_selector('*')
            # waiting and get images card and all associated elements
            imgElements = MobalyticsScraper._FindReqElements(driver, MobalyticsScraper._CARD_IMG_CLASS)
            cardsNumber = max(len(childs), 1)
            # open next associated card and wait loading
            if len(childs) > 0:
                childs[i].click()
                if (i != 0):
                    time.sleep(MobalyticsScraper._DELAY_BETWEEN_PARSE)        
            parsedFields = {'abilities': []}
            parsedFields['title'] = driver.find_element_by_class_name(MobalyticsScraper._CARD_TITLE_CLASS).text
            parsedFields['title'] = parsedFields['title'].replace('> ', '')
            # get main info elements: region, type, rarity
            mainEls = driver.find_elements_by_class_name(MobalyticsScraper._CARD_MAIN_CLASS)
            # get stats info elements: health, attack
            statsEls = driver.find_elements_by_class_name(MobalyticsScraper._CARD_STATS_CLASS)
            # get abilities info
            abilitiesEls = driver.find_elements_by_class_name(MobalyticsScraper._CARD_ABILITIES_CLASS)
            # and filter it by data-sel-id
            elements = mainEls + statsEls + abilitiesEls
            for el in elements:
                id = el.get_attribute('data-sel-id')
                if id == 'cardType':
                    parsedFields['type'] = el.text
                elif id == 'cardRegion':
                    parsedFields['region'] = el.text
                elif id == 'cardRarity':
                    parsedFields['rarity'] = el.text
                elif id == 'cardHealth':
                    parsedFields['health'] = el.text
                elif id == 'cardAttack':
                    parsedFields['attack'] = el.text
                elif id == 'keyword':
                    parsedFields['abilities'].append(el.text)
            # get img link by associated img number i
            link = imgElements[i].get_attribute('src')
            parsedFields['img link'] = link
            cardId = link.split('/')[-1].split('.webp')[0]
            # get content with full description (for mana cost)
            elements = driver.find_elements_by_name('description')
            description = elements[0].get_attribute('content')
            parsedFields['mana cost'] = description.split('Mana Cost: ')[1]
            # add to cards list
            card = Card(id=cardId, params=parsedFields)
            associatedCards.append(card)
            i += 1

        return associatedCards

    @staticmethod  
    def _OpenFirstCard(driver):
        allowCard = driver.find_element_by_class_name(MobalyticsScraper._FIRST_CARD_CLASS)
        link = allowCard.get_attribute('href')
        driver.get(link)
        # Is it true first card
        while True:
            # prev card button is not allow -> it is first card
            if not MobalyticsScraper._ClickButton(driver, MobalyticsScraper._PREV_CARD_CLASS):
                break

    @staticmethod
    def _ClickButton(driver, className):
        els = driver.find_elements_by_class_name(className)
        if len(els) > 0:
            els[0].click()
            return True

        return False

    @staticmethod
    def _StartChromeDriver(webDriverPath,
                           proxy={"ip":None, "port":None},
                           maximize_window=True):
        if proxy["ip"] and proxy["port"]:
            chromeOptions = webdriver.ChromeOptions()
            chromeOptions.add_argument('--proxy-server={}:{}'.format(proxy["ip"], proxy["port"]))
            driver = webdriver.Chrome(webDriverPath, chrome_options=chromeOptions)
        else:
            driver = webdriver.Chrome(webDriverPath)
        if maximize_window:
            driver.maximize_window()

        return driver


if __name__ == "__main__":
    chromeDriverPath = os.path.join('..', 'application', 'chromedriver.exe')
    outputFolderPath = os.path.join('..', 'cards')

    MobalyticsScraper.CollectData(outputFolderPath, chromeDriverPath)
        