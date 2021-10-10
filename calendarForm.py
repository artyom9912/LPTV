import calendar
import random
import sys
import os

import threading
from threading import Thread
from kivy.animation import Animation, AnimationTransition
from kivy.app import App
from time import sleep
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as Img
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from PIL import Image, ImageDraw
from kivy.uix.widget import Widget
import pymysql
import datetime
from LongPressButton import LongpressButton
from StoppableThread import StoppableThread
from DB import DB

db=DB()
PROJECT = 'FF'
PROJECT = db.GetProjects('act', datetime.datetime.today().year)[0][0]
USER = 'Алексей Лаптев'
MONTHS = ['январь','февраль','март','апрель','май','июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь']
curMonth = datetime.datetime.today().month
curYear = datetime.datetime.today().year
# Builder.load_file('StageBox.kv')
class Color():
    db = DB()
    white = [1, 1, 1, 1]
    black = [0, 0, 0, 1]
    weeknd = [.88, .88, .9, 1]
    berry = [1, .5, 0, 1]
    down = [1, .5, 0, 1]
    user = db.GetUserColor(USER)
    # user = [.55,.99,.37, 1]


class SV(ScrollView):
    stageList = ('ПОДГОТОВКА', ' 3D ГРАФИКА', '   ЗАКАЗНЫЕ\n    ПОЗИЦИИ', '         СМР', ' КОМПЛЕКТАЦИЯ', 'РЕАЛИЗАЦИЯ')
    sizeBox = NumericProperty(100)
    deadl = db.GetDeadlines(PROJECT)
    deadl[-2]='   '+str(deadl[-2])
    def __init__(self,days, **kwargs):
        super(SV, self).__init__(**kwargs)
        # Body = GridLayout(cols = 1, spacing = 4)

        for i in range(0,len(self.stageList)):
            stage = ' '+self.stageList[i] + ' \n' +'    [color=#787878]'+ str(self.deadl[i])+'[/color]    '
            self.ids.Body.add_widget(StageBox(stage=stage, days=days))


class MyLabel(Label):
    pass


class UserLabel(AnchorLayout):
    text = StringProperty('none')


class MyButton(Button):
    pass

class NextButton(Button):
    src=StringProperty('')
    fcolor=ListProperty([1,1,1,1])
class Cell(BoxLayout):
    text = StringProperty()
    source = StringProperty('')
    color = ListProperty([1, 1, 1, 1])
    font_name = StringProperty('Roboto')
    font_size = StringProperty('12dp')
    halign = StringProperty('center')


class MyTable(BoxLayout):
    color = ListProperty([.6, .6, .6, 1])
    orientation = StringProperty('vertical')
    padding = ListProperty([0, 0, 0, 0])


def MessageBox(text):
    Box = Window.children[0].children[1].ids.CentralBox.children[0]
    LeftBox = Window.children[0].children[1].ids.ProjectName
    if Box.children[0].text != '':
        Box.children[0].text = ''
        Box.children[1].size_hint_y = 10
        sleep(1)
    Box.children[0].text = text
    Box.children[1].size_hint_y = 1
    anim = Animation(pos=(Box.pos[0] + 21, Box.pos[1]), t='out_back')
    anim.start(Box)
    sleep(2)
    Box.children[0].text = ''
    Box.children[1].size_hint_y = 10
    anim = Animation(pos=(LeftBox.pos[0] + LeftBox.size[0], Box.pos[1]), duration=0.03)
    anim.start(Box)


def MassageBoxSetImg(img):
    Box = Window.children[0].children[1].ids.CentralBox.children[0]
    Box.children[1].source = img



backs = ['src/background1.png', 'src/background2.png', 'src/background3.png', 'src/background4.png',
         'src/background5.png', 'src/background6.png']


class StageBox(BoxLayout):
    text = StringProperty()
    curFlag = ''
    pressFlag = False

    def onLongClick(self, instance):
        id = instance.id
        color = None
        level = int(id[id.find('h') + 1:])
        day = int(id[id.find('d') + 1:id.find('h')])
        sets = self.ids['GridBox'].children
        box = instance.parent
        if len(box.children)<12: box = box.parent
        if instance.background_color == Color.user:
            self.pressFlag = True
            for widget in box.children:
                if type(widget) != type(BoxLayout()):
                    if widget.background_color == Color.user:
                        widget.background_color = Color.white
                else:
                    for it in widget.children:
                        if it.background_color != Color.user:
                            color = it.background_color
                            id = it.id
                    box.add_widget(LongpressButton(text='', background_color=color, background_normal=''
                                                   , on_release=self.onClick, id=id, long_press_time=1,
                                                   on_long_press=self.onLongClick, on_press=self.onPress),
                                   index=-1 * int(id[id.index('h') + 1:]))
                    box.remove_widget(widget)

            #MassageBoxSetImg('src/delete.png')
            T = StoppableThread(target=MessageBox, args=('Запись [color=#FCA000]удалена[/color]!',))
            T.start()
            stage = self.children[0].children[1].text.split('\n')[0].replace(' ', '')
            date = str(curYear) + '-' + str(curMonth) + '-' + str(id[id.index('d') + 1:id.index('h')])
            sett = {'user': self.parent.parent.parent.parent.children[1].ids.UserBox.children[1].text,
                    'project': PROJECT,
                    'stage': stage,
                    'date': date}
            db = DB()
            db.DeleteReport(sett)



    def onPress(self, instance):
        if instance.background_color == Color.user:
            return
        instance.text = instance.id[instance.id.find('h') + 1:]

    def coloFill(self, box, level, upd):
        for widget in box.children[0:12-level]:
            color = None
            id = None
            if type(widget) == type(BoxLayout()):
                for it in widget.children:
                    if it.background_color!=Color.user:
                        color = it.background_color
                        id = it.id
                box.add_widget(LongpressButton(text='', background_color=color, background_normal=''
                                                     , on_release=self.onClick, id=id, long_press_time=1,
                                                     on_long_press=self.onLongClick, on_press=self.onPress),
                                                     index=-1*int(id[id.index('h')+1:]))
                box.remove_widget(widget)

            else:
                if widget.background_color == Color.user:
                    widget.background_color = Color.white
                    widget.text = ''

        for widget in reversed(box.children[12 - level:12]):
            if type(widget)==type(BoxLayout()):continue
            sleep(0.08)
            if widget.background_color == Color.white or widget.background_color==Color.user:
                widget.background_color = Color.user
                widget.text = ''
            else:
                first = widget.background_color
                second = Color.user
                id = widget.id

                split=BoxLayout(orientation='horizontal')
                split.add_widget(LongpressButton(text='', background_color=second, background_normal=''
                                            , on_release=self.onClick, id=id, long_press_time=1,
                                            on_long_press=self.onLongClick, on_press=self.onPress))
                split.add_widget(LongpressButton(text='', background_color=first, background_normal=''
                                                 , on_release=self.onClick, id=id, long_press_time=1,
                                                 on_long_press=self.onLongClick, on_press=self.onPress))

                box.add_widget(split,index=-1*int(id[id.index('h')+1:]))
                box.remove_widget(widget)
        #MassageBoxSetImg('src/done.png')
        if upd:
            T = StoppableThread(target=MessageBox, args=('Запись обновлена!',))
        else: T = StoppableThread(target=MessageBox, args=('Запись добавлена!',))
        T.start()

    def onClick(self, instance):
        instance.text = ''
        if self.pressFlag:
            self.pressFlag = False
            return
        s = instance.id
        box = instance.parent
        if len(box.children)<12:
            box = box.parent
        first = box.children[-1]
        if type(first)==type(BoxLayout()):
            if first.children[0].background_color != Color.user and first.children[1].background_color != Color.user:
                MassageBoxSetImg('')
                T = StoppableThread(target=MessageBox, args=('[color=#FF9B00]Ошибка![/color] Выбранный день занят',))
                T.start()
                return
        level = int(s[s.find('h') + 1:])

        upd= False

        if type(box.children[-1]) == type(BoxLayout()):
            if box.children[-1].children[-1].background_color == Color.user or box.children[-1].children[0].background_color == Color.user:
                upd = True

        else:
            if box.children[-1].background_color == Color.user:

                upd = True
        stage = self.children[0].children[1].text.split('\n')[0].replace(' ', '')
        id = s
        date = str(curYear)+'-'+str(curMonth)+'-'+str(id[id.index('d')+1:id.index('h')])
        sett = {'user': self.parent.parent.parent.parent.children[1].ids.UserBox.children[1].text,
                  'project' : PROJECT,
                  'stage' : stage,
                  'date' : date,
                  'hours' : id[id.index('h')+1:]}

        db = DB()
        if upd != True :
            db.InsertReport(sett)
        else:
            db.UpdateReport(sett)
        T = Thread(target=self.coloFill, args=(box, level,upd))
        T.start()

    def clearData(self,last, delta):
        sets = self.ids['GridBox'].children
        for col in sets:

            if type(col.children[-1]) == type(BoxLayout()):
                id = col.children[-1].children[-1].id
                id = id[0:id.index('h') + 1]
                par = col
                for i in range(1,13):
                    par.remove_widget(par.children[-1])
                    ID = id + str(i)
                    par.add_widget(LongpressButton(text='', background_color=Color.white, background_normal=''
                                                   , on_release=self.onClick, id=ID, long_press_time=1,
                                                   on_long_press=self.onLongClick, on_press=self.onPress),index=0)
            else:
                for widget in col.children:
                    widget.background_color = Color.white

        if delta != 0:
            if delta< 0:
                for j in range(0, abs(delta)):
                        self.ids.GridBox.remove_widget(self.ids.GridBox.children[0])
            elif delta >0:
                for d in range(last+1, last+abs(delta)+1):
                    box = BoxLayout(orientation='vertical', spacing=1)
                    for h in range(1, 13):
                        id = ''.join(('d', str(d), 'h', str(h)))
                        box.add_widget(
                            LongpressButton(text='', background_color=Color.white, background_normal=''
                                            , on_release=self.onClick, id=id, long_press_time=1,
                                            on_long_press=self.onLongClick, on_press=self.onPress))
                    self.ids.GridBox.add_widget(box)
    def loadData(self, stage):
        set = {}
        addlist = []
        #SELECT userId, projectId, stageId, dateStamp, hours
        stage = stage.split('\n')[0].replace(' ','')

        result = db.loadReports(db.GetStageID(stage),PROJECT, curMonth)
        if len(result)==0: return
        for item in result:
            for i in range(1,item[4]+1):
                id = "d{0}h{1}".format(item[3].day, i)
                if id in set.keys():
                    set[id] = [set[id],db.GetUserColorById(item[0])]
                else: set[id] = db.GetUserColorById(item[0])

        boxex = self.ids['GridBox'].children
        sets = {}
        for box in boxex:
            for cell in box.children:
                sets[cell.id]=cell

        for id in set.keys():
            if id in sets.keys():
                addlist.append([sets[id],set[id]])


        for widget in addlist:
            if type(widget[1][0]) is list:
                split = BoxLayout(orientation='horizontal')
                id = widget[0].id

                if widget[1][0] == Color.user:
                    first = widget[1][0]
                    second = widget[1][1]
                else:
                    first = widget[1][1]
                    second = widget[1][0]
                split.add_widget(LongpressButton(text='', background_color=first, background_normal=''
                                                 , on_release=self.onClick, id=id, long_press_time=1,
                                                 on_long_press=self.onLongClick, on_press=self.onPress))
                split.add_widget(LongpressButton(text='', background_color=second, background_normal=''
                                                 , on_release=self.onClick, id=id, long_press_time=1,
                                                 on_long_press=self.onLongClick, on_press=self.onPress))
                par = widget[0].parent

                par.add_widget(split, index=-1 * int(id[id.index('h') + 1:]))
                par.remove_widget(widget[0])

            else:
                widget[0].background_color = widget[1]



    def __init__(self, stage, days, **kwargs):
        super(StageBox, self).__init__(**kwargs)

        self.ids.StageCell.text = stage
        back = backs[0]
        backs.remove(back)
        self.ids.StageCell.source = back
        for i in range(1, 13):
            self.ids.HoursBox.add_widget(Cell(text=str(i)))

        for d in range(1, days+1):
            column = BoxLayout(orientation='vertical', spacing =1)
            for h in range(1,13):
                id = ''.join(('d', str(d), 'h', str(h)))
                column.add_widget(LongpressButton(text='', background_color=Color.white, background_normal=''
                                                        , on_release=self.onClick, id=id, long_press_time=1,
                                                        on_long_press=self.onLongClick, on_press=self.onPress))
            self.ids.GridBox.add_widget(column)

        self.loadData(self.children[0].children[1].text)



class TopBox(BoxLayout):
    pass

class CalendarApp(App):
    title = 'LPTV'
    BODY = None
    def update(self, instance):
        global curMonth, curYear
        if instance.text == '[b]>[/b]':
            curMonth = MONTHS.index(instance.parent.children[1].text.lower()) + 2
        elif instance.text == '[b]<[/b]':
            curMonth = MONTHS.index(instance.parent.children[1].text.lower())
        if curMonth > 12 :
            curMonth = 1
            curYear+=1
        elif curMonth < 1 :
            curMonth = 12
            curYear-=1
        instance.parent.children[1].text = MONTHS[curMonth - 1].upper()

        daysCount = calendar.monthrange(curYear, curMonth)[1]
        weeknd = []
        for i in range(1, daysCount + 1):
            day = datetime.date(curYear, curMonth, i)
            if day.weekday() >= 5:
                weeknd.append(i)
        DaysBox=instance.parent.parent.children[0]
        count = len(DaysBox.children)
        for i in range(0,count):
            DaysBox.remove_widget(DaysBox.children[0])
        for i in range(1, daysCount+1):
            if i in weeknd:
                cell = Cell(text=str(i), color=Color.weeknd)
                DaysBox.add_widget(cell)
            else:
                cell = Cell(text=str(i))
                DaysBox.add_widget(cell)

        stages = self.BODY.children[0].children
        print(stages)
        for item in stages:
            item.clearData(count,daysCount-count)
            item.loadData(item.children[0].children[1].text)

    def build(self):
        global PROJECT, USER
        print('a')
        try:
            print(sys.argv[2]+' sssssssss')
            PROJECT = sys.argv[2]
            USER = sys.argv[1]
            Color.user=db.GetUserColor(USER)
        except: pass
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (1250, 780)
        title = PROJECT
        if len(PROJECT) > 14:
            title = PROJECT.split(' ')
            title = ' '.join(title[:-1])+'\n'+title[-1]
        daysCount = calendar.monthrange(curYear,curMonth)[1]
        sqr = db.getProjectSqr(PROJECT)
        SCREEN = BoxLayout(orientation='vertical')
        #SCREEN.add_widget(Cell(size_hint=[1,.005],color=[.7,.7,.7,.5]))
        weeknd = []
        for i in range(1,daysCount+1):
            day = datetime.date(curYear,curMonth,i)
            if day.weekday() >= 5 :
                weeknd.append(i)
        # TOP PART
        Top = TopBox()
        Top.ids.ProjectName.text = '[size=14][color=#A6A6A6]ПРОЕКТ:[/color][/size]' \
                                   '\n[font=src/futural.ttf]'+title+'[/font]' \
                                   '[color=#686868]  '+str(sqr)+' m²[/color]'

        Top.ids.UserBox.add_widget(MyLabel(text=USER, size_hint=[.5, 1], font_size='16dp',
                                           color=[0, 0, 0, 1], halign='right'))
        Top.ids.UserBox.add_widget(Img(source='src/circle2.png', size_hint=[.3, 1], color=Color.user))
        # Top.add_widget(UserBox)
        SCREEN.add_widget(Top)

        TABLE = MyTable(padding=[3, 3, 3, 3])
        # HEADER PART
        HEADER = MyTable(orientation='horizontal', size_hint=[1, .08], spacing=2, )
        HEADER.add_widget(Cell(text='ЧАСЫ', size_hint=[.045, 1]))
        HEADER.add_widget(Cell(text='ЭТАП РАБОТЫ', size_hint_x=None,width=109.4))
        DataBox = BoxLayout(orientation='vertical', spacing=3)
        month = datetime.datetime.today().month
        MonthBox = BoxLayout(orientation='horizontal')
        MonthBox.add_widget(NextButton(size_hint=[1/daysCount,1], fcolor=Color.user, text='[b]<[/b]'))
        MonthBox.add_widget(Cell(text=MONTHS[month-1].upper(), color=Color.user))
        MonthBox.add_widget(NextButton(size_hint=[1/daysCount,1],fcolor=Color.user, text='[b]>[/b]'))
        DataBox.add_widget(MonthBox)
        DaysBox = BoxLayout(orientation='horizontal', spacing=1)
        for i in range(1, daysCount+1):
            if i in weeknd:
                cell = Cell(text=str(i), color=Color.weeknd)
                DaysBox.add_widget(cell)
            else:
                cell = Cell(text=str(i))
                DaysBox.add_widget(cell)
        DataBox.add_widget(DaysBox)
        HEADER.add_widget(DataBox)
        TABLE.add_widget(HEADER)

        # BODY PART
        self.BODY = SV(days=daysCount)
        TABLE.add_widget(self.BODY)
        SCREEN.add_widget(TABLE)
        # SCREEN.add_widget(Widget(size_hint=[1,.12]))
        return SCREEN


if __name__ == "__main__":
    CalendarApp().run()
