import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)


@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   from azure.core.credentials import AzureKeyCredential
   from azure.search.documents import SearchClient

   service_endpoint = "https://ken-cog-search-svc.search.windows.net"
   index_name = "sharepoint-index"
   key = "quRm9N9F4y4vGhgZBFvNtRs86VqLugIBVVeyC0drYaAzSeDm86cn"
   
   credential = AzureKeyCredential(key)
   client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)
   results = list(
        client.search(
            search_text=name,
            query_type="semantic",
            semantic_configuration_name="ken-semantic-config",
            query_caption="extractive",
        )
   )   
   print(results)

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
