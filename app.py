import json
import PIL
import requests
import tkinter
from io import BytesIO
from PIL import ImageTk
from tkinter import *
from urllib.request import Request, urlopen, urlretrieve

class Collection(object):
    def __init__(self):
        self.cards = []

    def __str__(self):
        return 'Collection size = %s' % (len(self.cards))

    def getSize(self):
        return len(self.cards)

    def getCards(self):
        return self.cards

    def insertCard(self, card):
        self.cards.append(card)

    def removeCard(self, cardId):
        i = self.getSize() - 1
        while i >= 0:
            if (self.cards[i].cardId == cardId):
                self.cards.pop(i)
                break
            i -= 1

class Card(object):
    def __init__(self, cardId, imgUrl, mana, name):
        self.cardId = cardId
        self.imgUrl = imgUrl
        self.mana = mana
        self.name = name

    def __str__(self):
        return 'Card: %s' % (self.name)

class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('Birdie Processo Seletivo')
        self.geometry('625x465')
        self.pack_propagate(0)
        self.resizable(0,0)
        self.grid_rowconfigure(1, weight=1)
        self.protocol('WM_DELETE_WINDOW', self.closeApp)

        # starts on first page and with no mana filter
        self.currentPage = 0
        self.manaFilter = False

        # cards rendered arrays:
        self.cardsLabels = []
        self.images = []
        self.tk_images = []

        # main canvas
        self.main_background = ImageTk.PhotoImage(file="assets\\background.png")
        self.main_canvas = Canvas(self, width=575, height=465)
        self.main_canvas.create_image(0, 0, anchor='nw', image=self.main_background)
        self.main_canvas.grid(row=0, column=1, sticky='nsew')

        # frames
        self.previousPage_frame = Frame(self, width=25, height=465)
        self.previousPage_frame.grid(row=0, column=0, sticky='nsew')
        self.nextPage_frame = Frame(self, width=25, height=465)
        self.nextPage_frame.grid(row=0, column=2, sticky='nsew')

        # buttons
        self.previousPage_frame.bind("<1>", self.previousPage)
        self.nextPage_frame.bind("<1>", self.nextPage)

        # current page label
        self.main_canvas.create_text(
            280,
            440,
            text='Page 1',
            fill='#5a4b2e',
            font=('MS Serif', 16, 'bold'),
            tag='pageNumber'
        )

    def previousPage(self, event):
        if (self.currentPage != 0):
            self.currentPage -= 1
            self.main_canvas.delete('pageNumber')
            self.main_canvas.create_text(
                280,
                440,
                text='Page {}'.format(self.currentPage + 1),
                fill='#5a4b2e',
                font=('MS Serif', 16, 'bold'),
                tag='pageNumber'
            )
            self.renderPage()

    def nextPage(self, event):
        if (self.currentPage + 1 < self.collection.getSize() / 8):
            self.currentPage += 1
            self.main_canvas.delete('pageNumber')
            self.main_canvas.create_text(
                280,
                440,
                text='Page {}'.format(self.currentPage + 1),
                fill='#5a4b2e',
                font=('MS Serif', 16, 'bold'),
                tag='pageNumber'
            )
            self.renderPage()

    def closeApp(self):
        self.destroy()
        sys.exit()

    def fillCollection(self):
        self.collection = Collection()

        # downloading cards info
        q = Request('https://omgvamp-hearthstone-v1.p.rapidapi.com/cards/sets/Basic')
        q.add_header('X-RapidAPI-Host', 'omgvamp-hearthstone-v1.p.rapidapi.com')
        q.add_header('X-RapidAPI-Key', 'caab949769msh41345c6c3779b9ep151794jsn089fad479330')
        r = urlopen(q).read()
        cards = json.loads(r)
        for card in cards:
            # ignore Heroes and Hero Powers
            if card['type'] in ['Hero', 'Hero Power']:
                continue
            try:
                imgUrl = card['img']
                # ignore cards without images
                cardId = card['cardId']
                mana = card['cost']
                name = card['name']
                # insert remaining cards into collection
                self.collection.insertCard(Card(cardId, imgUrl, mana, name))
            except:
                continue
        self.collection.cards.sort(key=lambda card: card.mana)

        # downloading images
        print('Downloading images... Please wait.')
        imagesDownloaded = 0
        i = 0
        size = 123, 297
        while i < self.collection.getSize():
            card = self.collection.cards[i]
            try:
                r = requests.get(card.imgUrl)
                self.images.append(PIL.Image.open(BytesIO(r.content)))
                self.images[imagesDownloaded].thumbnail(size, PIL.Image.ANTIALIAS)
                self.tk_images.append(ImageTk.PhotoImage(self.images[imagesDownloaded]))
                test0 = self.images[imagesDownloaded]
                test1 = self.tk_images[imagesDownloaded]
                imagesDownloaded += 1
                i += 1
                print('    Downloaded image of', card)
            except:
                # deleting problematic cards from collection
                self.collection.removeCard(card.cardId)

    def renderPage(self):
        cardsFull = self.collection.getCards()
        if (self.manaFilter != False):
            cards = list(filter(lambda card : card.mana == self.manaFilter, cardsFull))
        else:
            cards = cardsFull

        # empty all 8 frames
        i = 0
        while i < 8:
            self.main_canvas.delete('cardImage{}'.format(i))
            i += 1

        cardsRendered = 0
        firstCardIndex = self.currentPage * 8
        i = firstCardIndex
        for card in cards:
            if (cardsRendered == 8) or (i == self.collection.getSize()):
                break
            self.main_canvas.create_image(
                35 + 120 * int(cardsRendered%4),
                40 + 200 * int(cardsRendered/4),
                image=self.tk_images[i],
                tag='cardImage{}'.format(cardsRendered),
                anchor='nw'
            )
            i += 1
            cardsRendered += 1

if __name__ == '__main__':
    app = App()
    app.fillCollection()
    app.renderPage()
    app.mainloop()