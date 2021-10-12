import datetime
import subprocess
import sys
import traceback
from kivy import Config
from kivy.properties import ListProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput

from kivy.animation import Animation
from kivy.uix.checkbox import CheckBox
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from threading import Thread
from DB import DB

USER = 'Алексей Лаптев'
DropUser = None
SM = ScreenManager()
COLOR = [1, .85, 0, 1]
userBtn=None
Update = False
Project = ''
PrjForm = None
YEAR = datetime.datetime.now().year

class SCREEN(BoxLayout):
    pass
class MainScreen(Screen):
    pass
class YearBtn(BoxLayout):
    text = StringProperty()
class AddUserScreen(Screen):
    def AddUsers(self):
        set = []
        for item in self.ids.box.children[-3:1:-1]:
            if item.ids.red.text == '': item.ids.red.text = '0'
            if item.ids.green.text == '': item.ids.green.text = '0'
            if item.ids.blue.text == '': item.ids.blue.text = '0'
            row=[item.ids.name.text, item.ids.red.text,item.ids.green.text,item.ids.blue.text]
            set.append(row)
        db=DB()
        db.UpdateUsers(set)

        if self.ids.box.children[1].ids.name.text!='':
            name = self.ids.box.children[1].ids.name.text
            rgb = [self.ids.box.children[1].ids.red.text,
                   self.ids.box.children[1].ids.green.text,
                   self.ids.box.children[1].ids.blue.text]
            print(rgb)
            db.InsertUser(name, rgb)
        SM.current='main'

    def __init__(self, **kwargs):
        super(AddUserScreen, self).__init__(**kwargs)
        db = DB()
        users = db.GetUsers()
        self.ids.box.add_widget(
            Cell(text='КОМАНДА LPTV', size_hint=[1, .06], font_size='28dp', font_name='src/futural'))
        self.ids.box.add_widget(Cell(color=COLOR, size_hint=[1, .005]))
        i=1
        for user in users:
            Row = UserRow(text=user[0])
            color = db.GetUserColor(user[0])
            color = list([round(item * 255) for item in color])
            Row.ids.red.text = str(color[0])
            Row.ids.green.text = str(color[1])
            Row.ids.blue.text = str(color[2])
            self.ids.box.add_widget(Row)
            i+=1
        self.ids.box.add_widget(UserRow(text=''))

        self.ids.box.add_widget(
            Button(text='СОХРАНИТЬ', padding=[50, 2], background_normal='', background_down='src/btnPress.png',
                   size_hint=[1, .08], color=[0, 0, 0, 1], on_release=lambda x: self.AddUsers(),
                   background_color=COLOR))
        self.ids.general.add_widget(Cell(size_hint=[1, .6]))


class UserRow(BoxLayout):
    text = StringProperty('')
    color = ListProperty([.5, .5, .5, 1])

    def colorChange(self, instance):
        try:
            if int(instance.text) > 255:
                instance.text = '255'
            elif int(instance.text) < 0:
                instance.text = '0'
        except:
            instance.text = ''
        try:
            rgb = [instance.parent.children[2],instance.parent.children[1],instance.parent.children[0]]
            col = [round(int(item.text) / 255, 2) for item in rgb]
            col.append(1)
        except:
            col = [.5, .5, .5, 1]
        instance.parent.ids.ex.color = col


class AddProjScreen(Screen):
    def __init__(self, **kwargs):
        super(AddProjScreen, self).__init__(**kwargs)
        db = DB()
        if not Update:
            Title = 'НОВЫЙ ПРОЕКТ'
            Level = '5'
            Name = Project
            Hint = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month) + '-01'
            Btn = 'ВНЕСТИ'
            sqr = ''
        else:
            Title = 'РЕДАКТИРОВАТЬ'
            Level = db.GetLevel(Project)
            Name = Project
            Hint = db.GetDeadlines(Project)
            Btn = 'ОБНОВИТЬ'
            sqr = db.getProjectSqr(Project)
            isDone = db.GetProjectState(Project)
        stgs = db.GetAllStages()
        name = BoxLayout(orientation='horizontal', size_hint=[1, .1], padding=[0, 2])
        name.add_widget(Cell(text=Title, font_size='29dp', font_name='src/futural', size_hint=[.6, 1]))
        name.add_widget(TextInput(text=str(Level), font_size='23dp',
                                  size_hint=[.08, 1], background_normal='', background_active='src/btnPress.png',
                                  background_color=[.9, .9, .9, 1], halign='center'))
        name.add_widget(Widget(size_hint=[.3, 1]))
        self.ids.box.add_widget(name)
        title = BoxLayout(orientation='horizontal', size_hint=[1, .09], spacing=5)
        title.add_widget(MyInput(bcolor=COLOR, size_hint=[.8, 1], hint_text='Имя проекта',
                                 background_active='', halign='left', text=Name))
        title.add_widget(
            MyInput(size_hint=[.16, 1], text=str(sqr), hint_text='m²', background_color=[.9, .9, .9, 1],
                    bcolor=[.9, .9, .9, 1]))
        self.ids.box.add_widget(title)
        stages = BoxLayout(orientation='vertical', size_hint=[1, .7])
        i = 0
        for stg in stgs:
            if Update:
                stages.add_widget(StageSelect(text=stg, hint=str(Hint[i])))
                i += 1
            else:
                stages.add_widget(StageSelect(text=stg, hint=Hint))
        self.ids.box.add_widget(stages)
        self.ids.box.add_widget(
            Button(text=Btn, padding=[50, 2], background_normal='', background_down='src/btnPress.png',
                   size_hint=[1, .1], color=[0, 0, 0, 1], on_release=lambda x: self.AddProject(old=Project),
                   background_color=COLOR))
        if Update:
            finish = BoxLayout(orientation='horizontal',size_hint=[1,.085], spacing = 10)
            finish.add_widget(Widget(size_hint=[.6,1]))
            finish.add_widget(Cell(text=' ЗАВЕРШИТЬ',font_size='16dp',color=[.95,.95,.95,1],size_hint=[.3,1]))
            finish.add_widget(CheckBox(size_hint=[.07,1], background_checkbox_down='src/checkOn.png',
                                       background_checkbox_normal='src/checkOff.png', active= isDone))
            self.ids.box.add_widget(finish)
        else:
            self.ids.box.add_widget(Cell(size_hint=[1, .08]))
        self.ids.general.add_widget(Cell(size_hint=[1, .4]))
        self.Form = self.ids.box

    def AddProject(self, old=None):
        db = DB()
        global Update, Project
        isDone= False
        level = self.Form.children[-1].children[1].text
        name = self.Form.children[-2].children[-1].text.upper()
        sqr = self.Form.children[-2].children[0].text
        if Update:
            isDone = self.Form.children[0].children[0].active
        stages = []

        for item in self.Form.children[-3].children:
            stages.insert(0, item.children[0].text)
        if level == '' or name == '' or sqr == '' or int(level) > 5 or 1 > int(level):
            self.Form.children[0].children[0].text = 'Не все поля заполнены корректно!'
            return

        if not Update:
            e =db.InsertProject(name, level, sqr, stages)
        else:
            e =db.UpdateProject(old, name, level, sqr, stages,isDone)
        if not e:
            self.Form.children[0].children[0].text = 'Поля заполнены некорректно!'
            return
        self.Form.children[0].children[0].text = ''
        Update = False
        Project = ''
        SM.current = 'main'


class AddButton(Button):
    def addProj(self):
        global PrjForm
        if PrjForm is not None:
            SM.remove_widget(PrjForm)
        AddPrj = AddProjScreen(name='AddPrj')
        PrjForm = AddPrj
        SM.add_widget(AddPrj)
        SM.current = 'AddPrj'
        SM.current = 'AddPrj'


class MyInput(TextInput):
    bcolor = ListProperty([.4, .4, .4, .8])


class DropButton(Button):
    pass


class StageSelect(BoxLayout):
    text = StringProperty('')
    hint = StringProperty(str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month) + '-01')


class DropBox(DropDown):
    data = ListProperty(['Текущие проекты', 'Архивные проекты', 'Все проекты'])


class Cell(BoxLayout):
    text = StringProperty()
    source = StringProperty('')
    color = ListProperty([1, 1, 1, 1])
    font_name = StringProperty('Roboto')
    font_size = StringProperty('12dp')
    halign = StringProperty('center')


class DropUserBox(DropDown):

    def select(self, data):
        super(DropUserBox, self).select(data)

    def __init__(self, **kwargs):
        super(DropUserBox, self).__init__(**kwargs)
        db = DB()
        userList = db.GetUsers()
        for item in userList:
            self.add_widget(DropButton(text=item[0], on_release=lambda x: self.select(x.text)))
        self.add_widget(
            DropButton(text='[b][color=#757575]Настройки[/color][/b]', background_color=[.9, .9, .9, 1], markup=True,
                       on_release=lambda x: self.select(x.text)))


class PROJECT(BoxLayout):
    levelColor = ListProperty([.25, .25, .25, 1])

    def UpdateClick(self):
        global Update, Project
        db = DB()
        Update = True
        Project = self.ids.projectBox.text
        global PrjForm
        if PrjForm is not None:
            SM.remove_widget(PrjForm)
        AddPrj = AddProjScreen(name='AddPrj')
        PrjForm = AddPrj
        SM.add_widget(AddPrj)
        SM.current = 'AddPrj'


    def onClickProj(self, instance):
        PROJ=instance.parent.ids.projectBox.text
        # subprocess.run([sys.executable, 'C:/Users/ekosh/Desktop/artemkens/LPTV/dist/LPTV/Calendar.exe', USER,
        #                 instance.parent.ids.projectBox.text], shell=True)
        #subprocess.call(['C:/Users/ekosh/Desktop/artemkens/LPTV/dist/LPTV/Calendar.exe',USER,PROJ])
        def startFork( PROJ):
            subprocess.run([sys.executable, "calendarForm.py", USER, PROJ], shell=True)
        T_proj = Thread(target=startFork, args=(PROJ,))
        T_proj.start()
        #subprocess.run([sys.executable,"calendarForm.py",USER,PROJ], shell=True)

    def onClickProjStat(self, instance):
        # subprocess.call(['graphic.exe', '',
        #                 instance.parent.ids.projectBox.text, 'True'])
        def startFork(instance):
            subprocess.call(['graphic.exe', '', instance.parent.ids.projectBox.text, 'True'])
        T_projStat = Thread(target=startFork, args=(instance,))
        T_projStat.start()

    def onClickUserStat(self, instance):
        db = DB()
        if instance.text == '': return
        name = db.GetFullName(instance.text)

        def startFork(instance):
            subprocess.call(['graphic.exe', name, instance.parent.parent.ids.projectBox.text, 'False'])

        T_userStat = Thread(target=startFork, args=(instance,))
        T_userStat.start()

    def __init__(self, name, sqr, level, **kwargs):
        super(PROJECT, self).__init__(**kwargs)
        db = DB()
        self.levelColor = level
        self.ids.projectBox.text = name
        wrkrList = db.AllUsers(self.ids.projectBox.text)
        if len(wrkrList) < 5:
            for i in range(5 - len(wrkrList)): wrkrList.append('')
        self.ids.hoursBox.text = db.hoursSum(name)
        self.ids.squareBox.text = '[color=#606060]' + str(sqr) + ' m²[/color]'
        if len(wrkrList)>5: self.height += 15
        for item in wrkrList:
            self.ids.workersBox.add_widget(
                Button(text=item.upper(), background_color=[1, 1, 1, 1], background_normal='', color=[0, 0, 0, 1],
                       font_size='12dp', on_release=self.onClickUserStat))
        # T.start()


class SCROLL(ScrollView):
    levels = {1: [.75, .75, .75, 1], 2: [.65, .65, .65, 1], 3: [.5, .5, .5, 1],
              4: [.30, .30, .30, 1], 5: [.15, .15, .15, 1]}

    def playAnim(self, instance):
        anim = Animation(pos=[instance.pos[0] - 10, instance.pos[1]], duration=0.1) + \
               Animation(pos=[instance.pos[0], instance.pos[1]], t='out_back') + \
               Animation(pos=[instance.pos[0], instance.pos[1]], duration=0.3)
        anim.start(instance)
        # sleep(0.15)
        # anim = Animation(pos=[instance.pos[0] + 10, instance.pos[1]], t='out_back')
        # anim.start(instance)

    def update(self, type):
        for item in self.ids.Scroller.walk(restrict=True):
            self.ids.Scroller.remove_widget(item)
        db = DB()
        prjList = db.GetProjects(type=type, year=YEAR)
        for item in prjList:
            prj = PROJECT(name=item[0], sqr=item[1], level=self.levels[item[2]])
            self.ids.Scroller.add_widget(prj)
        self.ids.Scroller.add_widget(AddButton())
        self.playAnim(self.ids.Scroller)

    def __init__(self, type, **kwargs):
        super(SCROLL, self).__init__(**kwargs)
        db = DB()
        prjList = db.GetProjects(type=type, year=YEAR)
        for item in prjList:
            prj = PROJECT(name=item[0], sqr=item[1], level=self.levels[item[2]])
            self.ids.Scroller.add_widget(prj)
        self.ids.Scroller.add_widget(AddButton())
        T = Thread(target=self.playAnim, args=(self.ids.Scroller,))
        T.start()


class MainApp(App):
    mainbutton = Button()
    projectList = None
    Form = None

    def setFilter(self, instance, text):
        self.mainbutton.text = text
        instance.select(self.mainbutton.text)
        if 'Текущ' in text:
            self.projectList.update(type='act')
        elif 'Архивные' in text:
            self.projectList.update(type='arc')
        elif 'Все' in text:
            self.projectList.update(type='all')

    def colorize(self, name):
        db = DB()
        color = db.GetUserColor(name)
        return color

    def setUser(self, root, text):
        global USER, COLOR
        if 'Настройки' in text:
            global PrjForm
            PrjForm = AddUserScreen(name='AddUser')
            SM.add_widget(PrjForm)
            SM.current = 'AddUser'
            return
        root.text = text
        USER = text
        COLOR = self.colorize(text)
        root.background_color = self.colorize(text)
        f = open('user.txt','w',encoding='utf-8')
        f.write(USER)
        f.close()
    def ShowStat(self,instance):
        subprocess.call(['Statistic.exe', str(YEAR)])
    def changeYear(self,instance):
        global YEAR
        if instance.text == '>':
            YEAR+=1
        else:
            YEAR-=1
        instance.parent.ids.year.text = str(YEAR)

    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (668, 775)
        Window.shape_mode = 'default'
        Window.shape_color_key = (.5, .0, .5, 1)
        global USER
        db = DB()
        try:    USER = open('user.txt',encoding='utf-8').readline()
        except:
            open('user.txt','w',encoding='utf-8').write(db.GetUsers()[0][0])
            USER = db.GetUsers()[0][0]
        global SM, Update, YEAR
        Main = MainScreen(name='main')
        Screen = SCREEN()
        DropFilter = DropBox()
        self.mainbutton = Button(text='Текущие проекты'.upper(), height=28, width=304, size_hint_y=None,
                                 size_hint_x=None, padding=[13, 10],
                                 background_normal='src/dropBtn.png'
                                 , color=[.2, .2, .2, 1], text_size=[223, 27], halign='left', valign='center',
                                 background_down='src/dropBtnDown.png'
                                 , font_size=16)
        self.mainbutton.bind(on_release=DropFilter.open)
        Screen.ids.Top.add_widget(self.mainbutton)
        Screen.ids.Top.add_widget(Widget(size_hint=[.14, 1]))
        DropUser = DropUserBox()
        UserBox = Button(text=USER, height=28, width=181, size_hint_y=None, size_hint_x=None, padding=[13, 2],
                         background_normal='src/userBtn.png', background_down='src/userBtnDown.png'
                         , color=[.2, .2, .2, 1], text_size=[185, 27], halign='left', valign='center',
                         background_color=db.GetUserColor(USER)
                         , font_name='src/Noah-Bold', font_size=17)
        UserBox.bind(on_release=DropUser.open)
        Screen.ids.Top.add_widget(UserBox)
        DropFilter.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x.upper()))
        DropUser.bind(on_select=lambda instance, x: self.setUser(UserBox, x))
        self.projectList = SCROLL(type='act')
        Screen.add_widget(self.projectList)
        Footer = BoxLayout(height=44, width=668, padding=[5, 0, 36, 0], size_hint_y=None, size_hint_x=None,
                           orientation='horizontal')
        Footer.add_widget(Cell(size_hint=[.4, 1]))
        Footer.add_widget(YearBtn(text=str(YEAR), size_hint=[.1,1]))

        Footer.add_widget(Button(text='СТАТИСТИКА', size_hint_y=None, size_hint_x=None,
                                 background_normal='src/userBtn.png', background_down='src/userBtnDown.png'
                                 , color=[.1, .1, .1, 1], halign='right', valign='center', text_size=[121, 20]
                                 , font_size=13, height=28, width=181, on_release=self.ShowStat))
        Screen.add_widget(Footer)
        Main.add_widget(Screen)
        SM.add_widget(Main)
        Window.bind(on_key_up=self._keyup)

        SM.current = 'main'
        return SM

    def _keyup(self, *args):
        if args[-1] == 41:
            if SM.current != 'main':
                global Update, Project
                SM.current = 'main'
                SM.remove_widget(PrjForm)
                Update = False
                Project = ''
            else:
                Window.close()


if __name__ == "__main__":
    try:
        MainApp().run()
    except Exception as e:
        e_type, e_val, e_tb = sys.exc_info()
        traceback.print_exception(e_type, e_val, e_tb, file=open('log.txt', 'a'))
