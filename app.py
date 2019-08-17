import json
import PIL
import requests
import tkinter
from io import BytesIO
from PIL import Image, ImageTk
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
        self.geometry('625x515')
        self.pack_propagate(0)
        self.resizable(0,0)
        self.grid_rowconfigure(1, weight=1)
        self.protocol('WM_DELETE_WINDOW', self.closeApp)

        # starts on first page and no filter
        self.currentPage = 0
        self.manaFilter = False

        # cards rendered arrays:
        self.cardsLabels = []
        self.images = []
        self.tk_images = []

        # frames
        self.previousPage_frame = Frame(self, bg='yellow', width=25, height=465)
        self.previousPage_frame.grid(row=0, column=0, sticky='nsew')
        self.main_frame = Frame(self, bg='#fee5a3', width=575, height=465)
        self.main_frame.grid(row=0, column=1, sticky='nsew')
        self.nextPage_frame = Frame(self, bg='yellow', width=25, height=465)
        self.nextPage_frame.grid(row=0, column=2, sticky='nsew')
        self.bottom_frame = Frame(self, bg='#5d1717', width=625, height=50)
        self.bottom_frame.grid(row=1, columnspan=3, sticky='nsew')

        # buttons
        self.previousPage_frame.bind("<1>", self.previousPage)
        self.nextPage_frame.bind("<1>", self.nextPage)

        # current page label
        self.currentPage_label = Label(
            self.main_frame,
            bg='#fee5a3',
            width=8,
            height=1,
            font=('Arial', 12),
            text='Page 1'
        )
        self.currentPage_label.grid(row=3, columnspan=4, padx=(20, 0), pady=(7, 0))

        # first row of 4 cards
        self.shownCards_frames = []
        self.shownCards_frames.append(Frame(self.main_frame, bg='#fee5a3', width=113, height=168))
        self.shownCards_frames[0].grid(row=0, column=0, padx=(22, 0), pady=(55, 0))
        self.shownCards_frames.append(Frame(self.main_frame, bg='#fee5a3', width=113, height=168))
        self.shownCards_frames[1].grid(row=0, column=1, padx=(15, 0), pady=(55, 0))
        self.shownCards_frames.append(Frame(self.main_frame, bg='#fee5a3', width=113, height=168))
        self.shownCards_frames[2].grid(row=0, column=2, padx=(15, 0), pady=(55, 0))
        self.shownCards_frames.append(Frame(self.main_frame, bg='#fee5a3', width=113, height=168))
        self.shownCards_frames[3].grid(row=0, column=3, padx=(15, 0), pady=(55, 0))

        # second row of 4 cards
        self.shownCards_frames.append(Frame(self.main_frame, bg='#fee5a3', width=113, height=168))
        self.shownCards_frames[4].grid(row=2, column=0, padx=(22, 0), pady=(35, 0))
        self.shownCards_frames.append(Frame(self.main_frame, bg='#fee5a3', width=113, height=168))
        self.shownCards_frames[5].grid(row=2, column=1, padx=(15, 0), pady=(35, 0))
        self.shownCards_frames.append(Frame(self.main_frame, bg='#fee5a3', width=113, height=168))
        self.shownCards_frames[6].grid(row=2, column=2, padx=(15, 0), pady=(35, 0))
        self.shownCards_frames.append(Frame(self.main_frame, bg='#fee5a3', width=113, height=168))
        self.shownCards_frames[7].grid(row=2, column=3, padx=(15, 0), pady=(35, 0))

    def previousPage(self, event):
        if (self.currentPage != 0):
            self.currentPage -= 1
            self.currentPage_label.configure(text= 'Page {}'.format(self.currentPage + 1))
            self.renderPage()

    def nextPage(self, event):
        if (self.currentPage + 1 < self.collection.getSize() / 8):
            self.currentPage += 1
            self.currentPage_label.configure(text= 'Page {}'.format(self.currentPage + 1))
            self.renderPage()

    def closeApp(self):
        self.destroy()
        # sys.exit()

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
            # ignore cards without images
            try:
                imgUrl = card['img']    
                # insert remaining cards into collection
                cardId = card['cardId']
                mana = card['cost']
                name = card['name']
                self.collection.insertCard(Card(cardId, imgUrl, mana, name))
            except:
                continue
        self.collection.cards.sort(key=lambda x: x.mana)

        # downloading images
        print('Downloading images... Please wait.')
        imagesDownloaded = 0
        i = 0
        size = 113, 168
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
                # print('    Downloading image of', card)
            except:
                # deleting problematic cards from collection
                self.collection.removeCard(card.cardId)

    def renderPage(self):
        firstCardIndex = self.currentPage * 8
        i = 0
        cardsRendered = 0
        self.cardsLabels = []

        # empty all 8 frames
        while i < 8:
            frame = self.shownCards_frames[i]
            for widget in frame.winfo_children():
                widget.destroy()
            i += 1

        i = 0
        for card in self.collection.getCards():
            if (i < firstCardIndex):
                i += 1
                continue
            if (cardsRendered == 8) or (i == self.collection.getSize()):
                break
            self.cardsLabels.append(
                Label(self.shownCards_frames[cardsRendered], image=self.tk_images[i], bg='#fee5a3')
            )
            self.cardsLabels[cardsRendered].place(x=0, y=0)
            i += 1
            cardsRendered += 1

if __name__ == '__main__':
    app = App()
    app.fillCollection()
    app.renderPage()
    app.mainloop()