import datetime
import sys
from random import random
import os
os.environ['KIVY_GL_BACKEND']='angle_sdl2'
from kivy.core.window import Window
from kivy.app import App
from kivy import Config
from kivy.properties import ListProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy_garden.graph import Graph, MeshLinePlot, LinePlot, SmoothLinePlot
from kivy.uix.boxlayout import BoxLayout
import matplotlib
#matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
import numpy
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from DB import DB
MONTHS = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']

class Cell(BoxLayout):
    text = StringProperty()
    source = StringProperty('')
    color = ListProperty([1, 1, 1, 1])
    font_name = StringProperty('Roboto')
    font_size = StringProperty('12dp')
    halign = StringProperty('center')
    fcolor = ListProperty([0,0,0,1])

MONTH = MONTHS[datetime.datetime.now().month-1]
YEAR = str(datetime.datetime.now().year)
PROJECT = 'ЗУМАОКЕ'
USER = 'Анна Бурлака'
isPROJECT = 'False'
isYEAR = False
prjColors=[[.45,.11,.75,1], [.87,0,.52,1], [.97,.36,.16,1], [1,.90,0,1], [.21,.95,.80,1],
           [.27,.78,.78,1], [.36,.39,.45,1],[1,.18,.39,1], [.81,.81,.91,1], [.98,.82,.29,1],
           [.77,1,0,1], [.51,.96,0,1],[0,1,0,1],[.96,.78,1,1], [.91,.85,.58,1],[.83,0,0,1],
           [.71,.86,1,1],[1,.71,.67,1],[1,.75,.45,1],[1,.45,.47,1],[.45,1,.95,1],[.49,.38,.50,1],
           [.48,.64,.49,1],[0,.32,.92,1],[.20,0,.92,1],[0,.40,.25,1]]
TABLE = Widget()

class Table(GridLayout):
    def __init__(self, **kwargs):
        super(Table, self).__init__(**kwargs)
        db=DB()
        month = str(MONTHS.index(MONTH) + 1)
        if isYEAR: month = None
        if isPROJECT:
            set = db.GetUserStats(PROJECT, month, YEAR)
            self.cols=len(set[0])
            i = 0
            self.size_hint=[(self.cols)*10/100,1]
            for item in set:
                size = [.38, .15]
                for subitem in item:
                    color = [.9, .9, .9, 1]
                    fcolor = [0,0,0,1]
                    pos = 'left'
                    if i == 0 and subitem!='':
                        subitem = subitem.split(' ')[0]
                        color = db.GetUserColor(subitem)
                        pos = 'center'
                    if i== len(set)-1:
                        color=[.97,.97,.97,1]
                        fcolor=[0,0,0,.6]
                    self.add_widget(Cell(text=str(subitem).upper(), color=color,
                                         halign=pos,fcolor=fcolor, size_hint=size))
                    size = [.15,.15]
                i+=1
        elif not isPROJECT:
            self.cols = 2
            self.rows = 10
            set=db.GetProjectStats(USER, month, YEAR)
            self.size_hint = [.15, 1]
            self.padding = 85,0,0,0

            if len(set) < 4: self.padding = 85,0,0,65
            elif len(set) > 8:
                self.size_hint=[.5,1]
                self.cols = 4
            elif len(set) > 16:
                self.size_hint = [.75, 1]
                self.cols = 6
            i=0
            f = open('color.txt','r', encoding='utf-8')
            for i in range(0,len(set)):
                try: color = prjColors[i]
                except:
                    color = f.readline().replace('\n','')[1:-1].split(',')
                print(color)
                self.add_widget(Cell(text=set[i][0].upper(), size_hint=[.7,1], color = color))
                self.add_widget(Cell(text=str(set[i][1]), size_hint=[.3,1], color = [.9,.9,.9,1]))
                i+=1


class SCREEN(BoxLayout):
    month = StringProperty(MONTH)
    year = StringProperty(YEAR)
    project = StringProperty(PROJECT)

    def __init__(self, **kwargs):
        global canvas, TABLE
        super(SCREEN,self).__init__(**kwargs)

        fig, ax = plt.subplots()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.grid(linestyle="--", color=(.82,.82,.82))
        ax.set_facecolor((.97, .97, .97))
        plt.tight_layout(pad=0.75)

        if (isPROJECT):
            title = PROJECT
        else:
            title = USER.upper()
        self.project = title
        self.drawLines()

        canvas = FigureCanvasKivyAgg(plt.gcf())
        self.add_widget(canvas)
        canvas.draw()
        self.addTable()
        self.ids.MonthBtn.ids.MidBtn.background_color= [.06, .70, .99, 1]

        self.ids.MonthBtn.ids.LeftBtn.bind(on_release=lambda x: self.update('<','M'))
        self.ids.MonthBtn.ids.RightBtn.bind(on_release=lambda x: self.update('>', 'M'))
        self.ids.YearBtn.ids.LeftBtn.bind(on_release=lambda x: self.update('<', 'Y'))
        self.ids.YearBtn.ids.RightBtn.bind(on_release=lambda x: self.update('>', 'Y'))
        self.ids.MonthBtn.ids.MidBtn.bind(on_release=lambda x: self.update('M', 'm',self.ids.MonthBtn.ids.MidBtn))
        self.ids.YearBtn.ids.MidBtn.bind(on_release=lambda x: self.update('Y', 'm',self.ids.YearBtn.ids.MidBtn))

    def addTable(self):
        footer = BoxLayout(orientation='horizontal', size_hint=[1, .6])
        #footer.add_widget(Widget(size_hint=[.12, 1]))
        footer.add_widget(Table())
        footer.add_widget(Widget(size_hint=[.41, 1]))
        if not isPROJECT: footer.size_hint=[1,.5]
        self.add_widget(footer)

    def update(self,direct,type, instance = None):
        plt.cla()
        global MONTH, YEAR, isYEAR
        if type == 'M':
            if direct== '<':
                id = MONTHS.index(MONTH)
                MONTH = MONTHS[id-1]
            elif direct== '>':
                id = MONTHS.index(MONTH)
                MONTH = MONTHS[id+1]
        elif type == 'Y':
            if direct== '<':
                y=int(YEAR)-1
                YEAR = str(y)
            elif direct== '>':
                y = int(YEAR) + 1
                YEAR = str(y)
        elif type == 'm':
            if direct == 'Y':
                self.ids.MonthBtn.ids.MidBtn.background_color = [.9,.9,.9, 1]
                instance.background_color = [.06, .70, .99, 1]
                isYEAR = True
            elif direct == 'M':
                self.ids.YearBtn.ids.MidBtn.background_color = [.9,.9,.9, 1]
                instance.background_color = [.06, .70, .99, 1]
                isYEAR = False
        self.drawLines()
        plt.grid(linestyle="--", color=(.82, .82, .82))
        canvas.draw()
        self.remove_widget(self.children[0])
        self.addTable()
        self.changeData()

    def changeData(self):
        self.ids.MonthBtn.text=MONTH
        self.ids.YearBtn.text=YEAR


    def drawLines(self):
        db = DB()
        if isYEAR:
            month = None
            plt.xlim(0, 13)
            plt.xticks(range(0,13))

        else:
            month = str(MONTHS.index(MONTH) + 1)
            plt.xlim(0, 31)
            plt.xticks(range(0, 32))
            plt.ylim(0, 13)

        if (isPROJECT):
            set = db.GetLinesUsers(PROJECT, month, YEAR)
        else:
            set = db.GetLinesProjects(USER, month, YEAR)

        color = 0
        f = open('color.txt', 'r', encoding='utf-8')
        for item in set:
            i = 0
            if not isYEAR:
                while set[item][0][i] < set[item][0][-1]:
                    if set[item][0][i] == set[item][0][i + 1]:
                        i += 1
                        continue
                    if set[item][0][i] != set[item][0][i + 1] - 1:
                        set[item][0].insert(i + 1, set[item][0][i] + 1)
                        set[item][1].insert(i + 1, None)
                    i += 1

            if (isPROJECT):
                plt.plot(set[item][0], set[item][1], color=db.GetUserColor(item),
                         linestyle='-', linewidth=2, markersize=7, marker='.')
            else:
                try: col = prjColors[color]
                except:
                    col = list([float(x) for x in f.readline().replace('\n','')[1:-1].split(',')])
                    print(col)
                plt.plot(set[item][0], set[item][1], color=col,
                         linestyle='-', linewidth=2, markersize=7, marker='.')
                color += 1

class Swipe(BoxLayout):
    text = StringProperty()


class GraphApp(App):
    def build(self):
        global PROJECT, USER, isPROJECT
        try:
            PROJECT = sys.argv[2]
            USER = sys.argv[1]
            isPROJECT = sys.argv[3]
        except: pass
        if isPROJECT=='True':
            isPROJECT = True
            Window.size = (1220, 590)
        elif isPROJECT == 'False':
            isPROJECT = False
            Window.size = (1220, 500)
        Window.clearcolor = (1, 1, 1, 1)
        scr = SCREEN()
        return scr

if __name__ == "__main__":
    GraphApp().run()