import datetime

import pymysql

class DB():
    config = open('CONFIG.txt').readlines()
    print(config)
    ip = config[0].split('=')[1].replace('\n','')
    user = config[1].split('=')[1].replace('\n','')
    password = config[2].split('=')[1].replace('\n','')
    db= config[3].split('=')[1].replace('\n','')
    connect = pymysql.connect(ip, user, password, db, charset='utf8')
    # def __init__(self):
    #     self.connect = pymysql.connect('localhost', 'root', 'root', 'lptv', charset='utf8')

    def GetProjects(self, type, year):
            cur = self.connect.cursor()
            if type == 'act':
                cur.execute("SELECT name, square, level FROM project WHERE isDone = 0 ORDER BY level desc, name;")
            if type == 'arc':
                cur.execute("SELECT name, square, level FROM project WHERE isDone = 1 "
                            "AND YEAR(startdate)='"+str(year)+"' ORDER BY level desc, name;")
            if type == 'all':
                cur.execute("SELECT name, square, level FROM project ORDER BY level desc, name;")
            rows = cur.fetchall()
            return rows
    def GetProjectsGantt(self, year):
        cur = self.connect.cursor()
        cur.execute("SELECT name, MONTH(startdate), MONTH(MAX(datestamp))-MONTH(startdate) FROM project JOIN main ON (main.projectId=project.id) "
                    "WHERE YEAR(datestamp) = '"+year+"' GROUP BY name;")
        return cur.fetchall()
    def GetFullName(self,name):
        cur = self.connect.cursor()
        cur.execute("SELECT name FROM user WHERE name like UPPER('"+name+"%')")
        return cur.fetchone()[0]
    def getProjectSqr(self,name):
        cur = self.connect.cursor()
        cur.execute("SELECT square FROM project WHERE name = '"+name+"';")
        rows = cur.fetchone()
        return rows[0]
    def GetProjectState(self,name):
        cur = self.connect.cursor()
        cur.execute("SELECT isDone FROM project WHERE name = '" + name + "';")
        rows = cur.fetchone()
        print(rows[0])
        if rows[0] == 1: return True
        else: return False
    def GetUsers(self):
            cur = self.connect.cursor()
            cur.execute("SELECT name FROM user;")
            rows = cur.fetchall()
            return rows

    def GetUserColor(self, name):
        cur = self.connect.cursor()
        cur.execute("SELECT color FROM user WHERE name like '"+name+"%';")
        row = cur.fetchone()
        if row==None: return [.9,.9,.9,1]
        return list(map(lambda x: float(x),row[0].split(',')))

    def GetUserColorById(self, id):
            cur = self.connect.cursor()
            cur.execute("SELECT color FROM user WHERE id = '"+str(id)+"';")
            row = cur.fetchone()
            return list(map(lambda x: float(x),row[0].split(',')))

    def GetProjectID(self, name):
            cur = self.connect.cursor()
            cur.execute("SELECT id FROM project WHERE name like '"+name+"';")
            row = cur.fetchone()
            return row[0]

    def GetStageID(self, name):
            cur = self.connect.cursor()
            cur.execute("SELECT id FROM stage WHERE name like '%"+name[:2]+"%';")
            row = cur.fetchone()
            return row[0]

    def GetUserID(self, name):

            cur = self.connect.cursor()
            cur.execute("SELECT id FROM user WHERE name like '"+name+"';")
            row = cur.fetchone()
            return row[0]

    def AllUsers(self, project):
        cur = self.connect.cursor()
        cur.execute("SELECT distinct user.name FROM main JOIN user ON (user.id = main.userId)"
                    "WHERE projectId = (SELECT id FROM project WHERE name = '"+project+"') ORDER BY user.name;")
        res = cur.fetchall()
        return list(item[0].split(' ')[0] for item in res)

    def InsertReport(self, settings):

            cur = self.connect.cursor()
            cur.execute("INSERT INTO main (userId, projectId, stageId, dateStamp, hours) VALUES "
                        "({0},{1},{2},'{3}',{4})".format(self.GetUserID(settings['user']),
                                                self.GetProjectID(settings['project']),
                                                self.GetStageID(settings['stage']),
                                                datetime.datetime.strptime(settings['date'],'%Y-%m-%d').date(),
                                                settings['hours']))
            self.connect.commit()

    def DeleteReport(self, settings):

            cur = self.connect.cursor()
            cur.execute("DELETE FROM main WHERE userId = {0} AND projectId = {1} "
                        "AND stageId = {2} AND dateStamp = '{3}'"
                        .format(self.GetUserID(settings['user']),
                        self.GetProjectID(settings['project']),
                        self.GetStageID(settings['stage']),
                        datetime.datetime.strptime(settings['date'],'%Y-%m-%d').date()))
            self.connect.commit()

    def GetLevel(self,project):
        cur = self.connect.cursor()
        cur.execute("SELECT level FROM project WHERE name = '"+project+"';")
        return cur.fetchone()[0]
    def GetDeadlines(self,project):
        cur = self.connect.cursor()
        print(project)
        cur.execute("SELECT finishdate FROM projectstage "
                    "WHERE projectId = (SELECT id FROM project WHERE name = '"+project+"');")
        return [item[0] for item in cur.fetchall()]
    def UpdateReport(self, settings):

            cur = self.connect.cursor()
            cur.execute("UPDATE main SET hours = {4} WHERE userId = {0} AND projectId = {1} "
                        "AND stageId = {2} AND dateStamp = '{3}'"
                        .format(self.GetUserID(settings['user']),
                        self.GetProjectID(settings['project']),
                        self.GetStageID(settings['stage']),
                        datetime.datetime.strptime(settings['date'],'%Y-%m-%d').date(),
                        settings['hours']))
            self.connect.commit()

    def loadReports(self, stage, project, month):
            cur = self.connect.cursor()
            string = "SELECT userId, projectId, stageId, dateStamp, hours FROM main " \
                  "WHERE stageId ="+str(stage)+" AND projectId = "+str(self.GetProjectID(project))+" "\
                  "and month(datestamp) = '"+str(month)+"';"
            cur.execute(string)

            rows = cur.fetchall()
            return rows

    def hoursSum(self, project):
        prj = self.GetProjectID(project)
        cur = self.connect.cursor()
        cur.execute("SELECT SUM(hours) FROM main WHERE projectId = "+str(prj)+";")
        row = cur.fetchone()
        res = str(row[0])
        print(res)
        if(res=='None'): res = '0'
        return res

    def GetLinesUsers(self, project, month, year):
        cur = self.connect.cursor()
        WHERE = "AND MONTH(dateStamp) = '"+str(month)+"' "
        GROUP = ""
        SELECT = "SELECT DAY(dateStamp), hours FROM main "
        if month is None:
            WHERE = ''
            SELECT = "SELECT MONTH(dateStamp), SUM(hours) FROM main "
            GROUP = "GROUP BY MONTH(dateStamp) "
        result = {}
        cur.execute("SELECT distinct user.name FROM main JOIN user ON (user.id = main.userId) "
                    "WHERE projectId = (SELECT id FROM project WHERE name = '"+project+"') "
                    +WHERE+
                    "AND YEAR(dateStamp) = '"+year+"' ")

        users = cur.fetchall()
        for user in users:
            cur.execute(SELECT+
                        "WHERE projectId = (SELECT id FROM project WHERE name = '"+project+"') "
                        "AND userId = (SELECT id FROM user WHERE name = '"+user[0]+"') "
                        +WHERE+
                        "AND YEAR(dateStamp) = '" + year + "' "
                        +GROUP+
                        "ORDER BY dateStamp;")
            res = cur.fetchall()
            result[user[0]]=([item[0] for item in res],[item[1] for item in res])
        return result

    def GetLinesProjects(self, user, month, year):
        cur = self.connect.cursor()
        result = {}
        WHERE = "AND MONTH(dateStamp) = '" + str(month) + "' "
        GROUP = ""
        SELECT = "SELECT DAY(dateStamp), hours FROM main "
        if month is None:
            WHERE = ''
            SELECT = "SELECT MONTH(dateStamp), SUM(hours) FROM main "
            GROUP = "GROUP BY MONTH(dateStamp) "
        if month is None: WHERE = ''
        cur.execute("SELECT distinct project.name FROM main JOIN project ON (project.id = main.projectId) "
                    "WHERE userId = (SELECT id FROM user WHERE name = '"+user+"') "
                    +WHERE+
                    "AND YEAR(dateStamp) = '"+year+"';")
        prjs = cur.fetchall()
        for prj in prjs:
            cur.execute(SELECT+
                        "WHERE userId = (SELECT id FROM user WHERE name = '"+user+"') "
                        "AND projectId = (SELECT id FROM project WHERE name = '"+prj[0]+"') "
                        +WHERE+
                        "AND YEAR(dateStamp) = '" + year + "' "
                        +GROUP+
                        "ORDER BY dateStamp ")

            res = cur.fetchall()
            result[prj[0]]=([item[0] for item in res],[item[1] for item in res])
        return result

    def GetUserStats(self, project, month, year):
        cur = self.connect.cursor()
        WHERE = "AND MONTH(dateStamp) = '" + str(month) + "' "
        if month is None: WHERE = ''
        cur.execute("SELECT distinct user.name FROM main JOIN user ON (user.id = main.userId) "
                    "WHERE projectId = (SELECT id FROM project WHERE name = '" + project + "') "
                    +WHERE+
                    "AND YEAR(dateStamp) = '" + year + "';")
        users = cur.fetchall()
        cur.execute("SELECT name FROM stage")
        stages= cur.fetchall()
        result = [['',],[],[],[],[],[],[],['',]]
        for user in users: result[0].append(user[0])
        result[0].append('ИТОГО ')
        sums = []
        for user in users:
            stageId = 0
            for stage in stages:
                cur.execute("SELECT sum(hours) FROM main JOIN stage ON (stage.id = main.stageId) "
                            "JOIN user ON (user.id = main.userId) "
                            "WHERE projectId = (SELECT id FROM project WHERE name = '" + project + "') "
                            +WHERE+" AND YEAR(dateStamp) = '" + year + "' "
                            "AND user.name like '"+user[0]+"%' AND stage.name like '"+stage[0]+"%' "
                            "GROUP BY stageId;")
                res = cur.fetchone()
                if res is None: res=(0,)
                result[stageId+1].append(res[0])
                stageId += 1

            cur.execute("SELECT sum(hours) FROM main JOIN user ON (user.id = main.userId) "
                        "WHERE projectId = (SELECT id FROM project WHERE name = '" + project + "') "
                        +WHERE+" AND YEAR(dateStamp) = '" + year + "' "
                        "AND user.name like '"+user[0]+"%' "
                        "GROUP BY projectId")
            sums.append(cur.fetchone()[0])
        i = 0
        for item in result[1:-1]:
            item.append(sum(item))
            item.insert(0,stages[i][0])
            i+=1
        for item in sums:
            result[-1].append(item)
        result[-1].append(sum(sums))
        return result

    def GetProjectStats(self,user, month, year):
        cur = self.connect.cursor()
        WHERE = "AND MONTH(dateStamp) = '" + str(month) + "' "
        if month is None: WHERE = ''
        cur.execute("SELECT distinct project.name FROM main JOIN project ON (project.id = main.projectId) "
                    "WHERE userId = (SELECT id FROM user WHERE name = '" + user + "') "
                    +WHERE+
                    "AND YEAR(dateStamp) = '" + year + "';")
        prjs = cur.fetchall()
        result = []
        for prj in prjs:
            cur.execute("SELECT sum(hours) FROM main JOIN project ON (project.id = main.projectId) "
                        "WHERE userId = (SELECT id FROM user WHERE name = '" + user + "') "
                        "AND projectId = (SELECT id FROM project WHERE name like '"+prj[0]+"') "
                        +WHERE+
                        "AND YEAR(dateStamp) = '" + year + "' "
                        "GROUP BY projectId;")
            res = cur.fetchone()[0]
            result.append([prj[0],res])
        return result

    def GetResult(self, where,year):
        cur = self.connect.cursor()
        cur.execute("SELECT pr.name, pr.square, user.name, sum(hours) FROM main "
                    "JOIN project pr ON (pr.id=main.projectId) JOIN user ON(user.id=main.userId) "
                    +where+
                    " AND YEAR(datestamp)='"+str(year)+"' GROUP BY user.name, pr.name ORDER BY projectId")
        res = cur.fetchall()
        return res

    def GetAllStages(self):
        cur = self.connect.cursor()
        cur.execute("SELECT name FROM stage;")
        return [item[0] for item in cur.fetchall()]

    def InsertProject(self, name, level, sqr, stages):
        cur = self.connect.cursor()
        try:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            cur.execute("INSERT INTO project (name, level, square, startdate, isDone) VALUES "
                        "('"+name+"',"+level+","+sqr+",'"+str(date)+"',0);")

            id = cur.lastrowid
            for i in range(0,len(self.GetAllStages())):
                cur.execute("INSERT INTO projectstage (projectId, stageId, finishdate) VALUES "
                            "("+str(id)+","+str(i+1)+", '"+stages[i]+"');")

            self.connect.commit()
            return True
        except:
            self.connect.rollback()
            return False

    def UpdateProject(self,oldname, name, level, sqr, stages,isDone):
        cur = self.connect.cursor()
        if isDone: isDone=1
        else: isDone =0
        try:
            cur.execute("SELECT id FROM project WHERE name = '"+oldname+"';")
            id = cur.fetchone()[0]
            cur.execute("UPDATE project SET "
                        "name = '"+name+"',level = "+level+",square="+sqr+",isDone="+str(isDone)+""
                        " WHERE id = "+str(id)+"")

            for i in range(0,len(self.GetAllStages())):
                cur.execute("UPDATE projectstage SET finishdate='"+stages[i]+"' WHERE "
                            "projectId="+str(id)+" AND stageId="+str(i+1)+";")
            self.connect.commit()
            return True
        except:
            self.connect.rollback()
            return False

    def UpdateUsers(self,set):
        cur = self.connect.cursor()
        i=1
        for item in set:
            color = ','.join([str(round(float(c.replace(' ',''))/255,2)) for c in item[1:4]])
            color+=',1'
            cur.execute("UPDATE user SET name = '"+item[0]+"', color = '"+color+"' "
                        "WHERE id ="+str(i))
            self.connect.commit()
            i+=1
    def InsertUser(self,name,rgb):
        cur = self.connect.cursor()
        for i in range(0,3):
            if rgb[i].replace(' ','')=='': rgb[i]='255'
        color = [str(round(int(item.replace(' ',''))/255,2)) for item in rgb]
        cur.execute("INSERT INTO user (name, color) VALUES ('"+name+"','"+','.join(color)+",1');")
        self.connect.commit()



