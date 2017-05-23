#-*- coding=utf-8 -*-
import MySQLdb


conn=MySQLdb.connect('localhost','root','cyx210210','web')
cursor=conn.cursor()

forums={
    '7':'a',
    '8':'b',
    '16':'c',
    '20':'d',
    '21':'e',
    '22':'f',
    '2':'g',
    '17':'h',
    '15':'i',
    '18':'j',
    '4':'k',
    '19':'l',
    '5':'m',
    '24':'n'
}

for key in forums.keys():
    forum=forums[key]
    sql='''select count(*) from clposts where forum='%s';'''%forum
    cursor.execute(sql)
    posts_num=int(cursor.fetchall()[0][0])
    if posts_num>2000:
        sql='''delete from clposts where forum='%s' order by id asc limit %d;'''%(forum,(posts_num-2000))
        n=cursor.execute(sql)
        print 'forum %s delete %d posts'%(forum,n)
conn.commit()
conn.close()
    

