import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


load_dotenv()


def db_connection():
    """
    A function to return a connection to the database
    Returns
    -------
    connection:
        A database connection object

    """
    db_name = os.getenv('POSTGRES_DB')
    db_host = os.getenv('POSTGRES_HOST')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_port = os.getenv('POSTGRES_PORT', 5432)
    return psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)


def query_db(port, date):
    """Queries the database and returns

    Parameters
    ----------
    port : str
        the primary key of the departure port
    date : str
        string representation of the flight departure date

    Returns
    -------

    """
    date_ = f"'{date}'"
    query_string = f'SELECT * FROM app_flight WHERE app_flight.departure_port_id = {port} AND app_flight.departure_date = DATE {date_};'
    with db_connection().cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query_string)
        results = cur.fetchall()

    json_output = json.dumps(results, default=str)
    return bytes(json_output, encoding='utf8')


class ServerHandler(SimpleHTTPRequestHandler):
    """ A class that implements handlers for various operations of the HTTP server"""
    def do_GET(self):
        """
        implements the GET operation of the HTTP server

        Returns
        -------
        None
        """
        path_params = self.path[1:].split('/')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        msg = query_db(path_params[0], path_params[1])
        self.wfile.write(msg)


def server(server_class=HTTPServer, handler_class=ServerHandler):
    """Creates a http server

    Parameters
    ----------
    server_class :
        The HTTPServer class used to instantiate the server
    handler_class :
        The class that implements handling of the http request methods

    Returns
    -------
    None

    """
    recommendations_host = os.getenv('RECOMMENDATIONS_HOST', 'localhost')
    server_address = (recommendations_host, 8100)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    server()
