import os
import json
import logging
import tornado.options
import tornado.log
import tornado.web
from tika import parser
from dotenv import load_dotenv
import tika
import dropbox
from elasticsearch import Elasticsearch


class App(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super().__init__(handlers, **kwargs)

        load_dotenv()

        self.dbx = dropbox.Dropbox(
            os.getenv('DROPBOX_ACCESS_TOKEN'))
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        if not self.es.indices.exists(index="text_content"):
            self.es.indices.create(index="text_content")
        tika.initVM()


class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, obj, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(obj))


class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html", title="Borneo Python Demo", results=[])


class SearchHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        queryString = str(self.get_argument("q", None, True))
        print("Query String: " + queryString)
        # check if files are downloaded & download if not downloaded
        self.updateLocalFiles()
        # parse downloaded files
        self.parseLocalFiles()
        # query elasticsearch
        query_body = {
            "query": {
                "match": {
                    "content": queryString
                }
            }
        }
        result = self.application.es.search(
            index="text_content", body=query_body)
        name = []
        for hit in result["hits"]["hits"]:
            name.append(hit["_source"].get('name'))
        self.render("index.html", results=name)

    def updateLocalFiles(self):
        for entry in self.application.dbx.files_list_folder('').entries:
            if (isinstance(entry, dropbox.files.FileMetadata) and (entry.is_downloadable) and not os.path.isfile("./files/"+entry.path_lower)):
                path = self.remove_suffix("", '/') + "files/" + \
                    self.remove_prefix(entry.path_lower, "/")
                try:
                    os.makedirs(os.path.dirname(os.path.abspath(path)))
                except:
                    1+1
                self.application.dbx.files_download_to_file(
                    path, entry.path_lower)

    def parseLocalFiles(self):
        for file in os.listdir("./files/"):
            parsed = parser.from_file("./files/"+file)
            data = {"name": os.fsdecode(file), "content": parsed["content"]}
            query_name = {
                "query": {
                    "match": {
                        "name": os.fsdecode(file)
                    }
                }
            }
            result = self.application.es.search(
                index="text_content", body=query_name)
            if not len(result["hits"]["hits"]):
                res = self.application.es.index(
                    index="text_content", body=data)

    def remove_prefix(text, prefix):
        return text[text.startswith(prefix) and len(prefix):]

    def remove_suffix(text, suffix):
        return text[:-(text.endswith(suffix) and len(suffix))]


def make_app(options):
    return App([
        (r"/", MainHandler),
        (r"/search", SearchHandler),
    ], static_path=os.path.join(os.path.dirname(__file__), "static"), debug=options.debug)


if __name__ == "__main__":
    # Define settings / options for the web app
    # Specify the port number to start the web app on(default value is port 8888)
    tornado.options.define("port", default=8888)
    # Specify whether the app should run in debug mode
    # Debug mode restarts the app automatically on file changes
    tornado.options.define("debug", default=True)

    # Read settings / options from command line
    tornado.options.parse_command_line()

    # Access the settings defined
    options = tornado.options.options

    # Create web app
    app = make_app(options)
    app.listen(options.port)
    logging.info("Starting listing service. PORT: {}, DEBUG: {}".format(
        options.port, options.debug))

    # Start event loop
    tornado.ioloop.IOLoop.current().start()
