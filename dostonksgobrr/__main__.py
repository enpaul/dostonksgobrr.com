"""Development server stub entrypoint

Flask comes with a built-in development server. This entrypoint allows ``dostonksgobrr``
to be run directly to run the development server and expose some simple config options
for ease of access. Run the below command to start the server:

::

  python -m dostonksgobrr

.. warning:: As the development server will tell you on startup, do not use this for
             production deployments.
"""
import argparse

from dostonksgobrr.application import APPLICATION


# pylint: disable=invalid-name
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bind", help="Host to listen on", default="127.0.0.1")
    parser.add_argument(
        "-p", "--port", help="Port to listen on", default=5000, type=int
    )
    parser.add_argument("-d", "--debug", help="Run in debug mode", action="store_true")
    args = parser.parse_args()
    APPLICATION.run(host=args.bind, port=args.port, debug=args.debug, load_dotenv=True)
