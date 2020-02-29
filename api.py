from flask import Flask, jsonify, Response, make_response
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS, cross_origin
import sqlite3
import os
from threading import Timer
import mimetypes


parser = reqparse.RequestParser()
parser.add_argument('title', type=str)
parser.add_argument('content', type=str)

app = Flask(__name__)
CORS(app)
api = Api(app)


LOCK_STATUS = {}

def lock(tid):
    print("lock " + str(tid))
    LOCK_STATUS[tid] = True

def unlock(tid):
    print("unlock " + str(tid))
    LOCK_STATUS[tid] = False

def is_locked(tid):
    return tid in LOCK_STATUS and LOCK_STATUS[tid]

class Text(Resource):
    def get(self, tid):
        sql = "select * from demo where tid = ? "
        res = query_db(sql, [tid], True)
        print(res)

        if not res:
            abort(404, message="Text tid:{} doesn't exist".format(tid))
        else:
            global LOCK_STATUS
            tid = res["tid"]
            isLock = is_locked(tid)

            print("isLock: ", isLock, " tid: ", tid)
            if isLock:
                return jsonify({"isLock": True})
            else:
                lock(tid)
                t = Timer(60.0, unlock, [tid])
                t.start()
                return jsonify(res)

    def put(self, tid):
        args = parser.parse_args()
        text = {'tid': tid, 'title': args['title'], 'content:': args['content']}
        # TEXTS[tid] = text
        sql = 'insert or replace into {0} ({1}) values ({2})'.format('demo', 'tid, title, content', '?, ?, ?')
        values = tuple(text.values())
        insert_db(sql, values)
        return text, 201

def get_conn():
    conn = sqlite3.connect("demo.db")
    cur = conn.cursor()
    exist = cur.execute("pragma table_info('demo')").fetchone()
    if not exist:
        os.system('sqlite3 demo.db ".read demo.sql"')
    return conn

def query_db(sql, args=(), one=False):
    conn = get_conn()
    cur = conn.execute(sql, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    res =  (rv[0] if rv else None) if one else rv
    conn.commit()
    conn.close()
    return res


def insert_db(sql, values):
    print(sql)
    print(values)
    conn = get_conn()
    cur = conn.execute(sql, values)
    conn.commit()
    conn.close()


class TextList(Resource):
    def get(self):
        sql = "select * from demo"
        res = query_db(sql, "")
        if not res:
            abort(404, message="No Result")
        else:
            return jsonify(res)
            # return res

    def post(self):
        args = parser.parse_args()
        print(args)
        text = {'title': args['title'], 'content:': args['content']}
        sql = 'insert or replace into {0} ({1}) values ({2})'.format('demo', 'title, content', '?, ?')
        values = tuple(text.values())
        insert_db(sql, values)
        return values, 201



@app.route('/download/<string:tid>')
def download_file(tid):
    print("download file >>>>>>>>>" + tid)
    sql = "select * from demo where tid = ? "
    res = query_db(sql, [tid], True)
    response = make_response(res["content"])
    response.headers['Content-Type'] = "text/plain"
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(res["title"] + ".txt")
    return response


api.add_resource(TextList, '/texts')
api.add_resource(Text, '/text/<tid>')


if __name__ == '__main__':
    app.run(debug=True, port=8080)






















