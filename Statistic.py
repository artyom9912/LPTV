import datetime
import sys
from kivy.core.window import Window
from kivy.app import App
from kivy import Config
from kivy.properties import ListProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy_garden.graph import Graph, MeshLinePlot, LinePlot, SmoothLinePlot
from kivy.uix.boxlayout import BoxLayout
import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from DB import DB
YEAR = datetime.datetime.now().year
MONTHS = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
prjColors=[[],[.45,.11,.75,1], [.87,0,.52,1], [.97,.36,.16,1], [1,.90,0,1], [.21,.95,.80,1],
           [.27,.78,.78,1], [.36,.39,.45,1],[1,.18,.39,1], [.81,.81,.91,1], [.98,.82,.29,1],
           [.77,1,0,1], [.51,.96,0,1],[0,1,0,1],[.96,.78,1,1], [.91,.85,.58,1],[.83,0,0,1],
           [.71,.86,1,1],[1,.71,.67,1],[1,.75,.45,1],[1,.45,.47,1],[.45,1,.95,1],[.49,.38,.50,1],
           [.48,.64,.49,1],[0,.32,.92,1],[.20,0,.92,1],[0,.40,.25,1]]

class Cell(BoxLayout):
    text = StringProperty()
    source = StringProperty('')
    color = ListProperty([1, 1, 1, 1])
    font_name = StringProperty('Roboto')
    font_size = StringProperty('12dp')
    halign = StringProperty('center')
    fcolor = ListProperty([0,0,0,1])

class BoxTable(BoxLayout):
    orientation = 'vertical'
    padding = [10,10,10,10]
    def __init__(self, name, where, **kwargs):
        super(BoxTable, self).__init__(**kwargs)
        self.add_widget(Cell(text = name, size_hint=[1,.08], font_name='src/Noah-Regular',
                             font_size='13dp'))
        self.add_widget(Table(where))

class Table(GridLayout):
    cols = 4
    def __init__(self,where, **kwargs):
        super(Table, self).__init__(**kwargs)
        Head = ['S','ДИЗАЙНЕР','ЧАСЫ']
        db = DB()
        set = db.GetResult(where,YEAR)
        if len(set)==0:
            return
        self.add_widget(
            Cell(text='ПРОЕКТ', fcolor=[1, 1, 1, 1], color=[.3, .3, .3, 1], size_hint=[.4, 1], halign='left'))
        for item in Head:
            self.add_widget(
                Cell(text=item, fcolor=[1, 1, 1, 1], color=[.3, .3, .3, 1], size_hint=[.15, 1], halign='center'))
        temp = ''
        switch = True
        for item in set:
            i = 0
            item = list(item)
            if item[0]==temp:
                temp = item[0]
                item[0] = ''
                item[1] = ''
            else:
                switch = not switch
                temp = item[0]
            if switch:
                color = [.9, .9, .9, 1]
            else:
                color = [.8, .8, .8, 1]

            for subitem in item:
                size = [.25,1]
                align = 'center'

                if i == 2: subitem=subitem.split(' ')[0].upper()
                elif i == 0:
                    size=[.4,1]
                    align='left'
                self.add_widget(Cell(text=str(subitem), color = color, size_hint=size, halign =align))
                i+=1


class StatApp(App):
    def build(self):
        global YEAR
        try:
            YEAR = sys.argv[1]
        except:
            pass
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (1200, 740)
        db = DB()
        Wheres = ['WHERE isDone = 0', 'WHERE isDone = 1', 'WHERE isDone=1 and YEAR(startdate) =\''+str(YEAR)+'\'']
        SCREEN = BoxLayout(orientation='vertical')
        SCREEN.add_widget(Cell(size_hint=[1,.01], color = [.5,.5,.5,.8]))
        SCREEN.add_widget(Cell(size_hint=[1,.10], fcolor =[0,0,0,1], font_size = '25dp',
                               text = 'СТАТИСТИКА  [font=src/Noah-Bold][color=#686868]'+str(YEAR)+'[/color][/font]', font_name='src/futural', padding =[20,2,0,0]))
        BODY = BoxLayout(orientation='horizontal', spacing = 15, padding = [10,2],size_hint=[1,.5])
        BODY.add_widget(BoxTable(str(YEAR)+' - ТЕКУЩИЕ ПРОЕКТЫ', Wheres[0]))
        BODY.add_widget(BoxTable(str(YEAR)+' - ЗАВЕРШЕННЫЕ ПРОЕКТЫ',Wheres[1]))
        BODY.add_widget(BoxTable(str(YEAR)+' - НАЧАТЫЕ И ЗАВЕРШЕННЫЕ ПРОЕКТЫ',Wheres[2]))
        SCREEN.add_widget(BODY)

        FOOTER = BoxLayout(size_hint=[1,.5], orientation='vertical', padding =[30,5,2,0])
        fig, ax = plt.subplots()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_facecolor((.96, .96, .96))
        plt.tight_layout(pad=1)
        ax.yaxis.set_tick_params(width=3,length=1)
        plt.subplots_adjust(left=0.11)
        set = db.GetProjectsGantt(str(YEAR))
        i = 1
        PRJS = []
        f = open('color.txt', 'r', encoding='utf-8')
        for item in set:
            item = list(item)
            if len(item[0]) > 14:
                item[0] = item[0][0:13]
            try:
                color = prjColors[i]
            except:
                color = list([float(x) for x in f.readline().replace('\n', '')[1:-1].split(',')])
            ax.barh(i, width=item[2], align='center', left=item[1]-1, facecolor=color)
            PRJS.append(item[0])
            i += 1

        PRJS.insert(0, '')
        plt.yticks(range(0, len(PRJS)), PRJS)
        plt.ylim(0, len(PRJS))
        plt.xticks(range(0, len(MONTHS)), MONTHS)
        plt.xlim(0, 12)
        plt.draw()
        #plt.xticks(MONTHS)
        canvas = FigureCanvasKivyAgg(plt.gcf())
        FOOTER.add_widget(canvas)
        FOOTER.add_widget(Widget(size_hint=(1,.1)))
        SCREEN.add_widget(FOOTER)
        return SCREEN

if __name__ == "__main__":
    StatApp().run()