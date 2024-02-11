import asyncio
import configparser
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from graph import Graph


import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from summarizer import Summarizer


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
    
    # Load settings
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    azure_settings = config['azure']

    graph: Graph = Graph(azure_settings)   

    token = await graph.get_user_token()
    print('User token:', token, '\n')

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
   
    result = results[0]   
    myLink = "<A href='https://setelab.sharepoint.com/Shared%20Documents/Forms/AllItems.aspx?id=%2FShared%20Documents%2Fdocument%2F" + result["metadata_spo_item_name"] + "&parent=%2FShared%20Documents%2Fdocument&p=true&ga=1'>" + result["metadata_spo_item_name"] + "</A>"          

    print(result["@search.reranker_score"])

    captions = result["@search.captions"]
    if captions:
        caption = captions[0]
        if caption.highlights:
            print(f"Caption: {caption.highlights}\n")
            myCaption = caption.highlights
        else:
            print(f"Caption: {caption.text}\n")
            myCaption = caption.text

    print(myCaption)


    model = AutoModelForSeq2SeqLM.from_pretrained('t5-base')
    tokenizer = AutoTokenizer.from_pretrained('t5-base')


    tempOutput = "" 
    i = 0        
    for result in results:
        tempContent = result["content"]    
        tempContent = tempContent[0:500]  
        tempOutput = tempOutput + result["metadata_spo_item_name"] + ";;" + str(round(result["@search.reranker_score"],2)) + ";;" + tempContent + ",,"
        
    #        bert_model = Summarizer()
    #        ext_summary = bert_model(tempContent, ratio=0.5)


    myRows = tempOutput.split(",,")      

    myTable = '<!doctype html><head><title>Azure Semantic Search</title><link rel="stylesheet" href="static/bootstrap/css/bootstrap.min.css"><link rel="icon" href="static/favicon.ico"></head>'
    myTable += "<style>table, th, td {border: 1px solid black;border-collapse: collapse;}</style>"        
    myTable += "<TABLE><TH>File Name</TH><TH>Score</TH><TH>Contents</TH>"
    for myRow in myRows:
        myTable += "<TR>"  
        myCells = myRow.split(";;")

        for i in range(len(myCells)):
            if i == 0:
                myTable += "<TD><A href='https://setelab.sharepoint.com/Shared%20Documents/Forms/AllItems.aspx?id=%2FShared%20Documents%2Fdocument%2F" + myCells[i] + "&parent=%2FShared%20Documents%2Fdocument&p=true&ga=1'>" + myCells[i] + "</A></TD>"                                       
            else:
                myTable += "<TD>" + myCells[i] + "</TD>"

        myTable += "</TR>"   
    myTable += "</TABLE>"         

    myOutput = ""
    myOutput += "<style>.aligncenter{text-align: center;}</style>"
    myOutput += '<div class="px-4 py-3 my-2 text-center">'
    myOutput += '<P class="aligncenter"><img class="d-block mx-auto mb-4" src="static/images/azure-icon.svg" alt="Azure Logo" width="192" height="192"/></P>'
    myOutput += "<P>" + myCaption + "</P>"
    myOutput += "<P>" + myLink + "</P>"
    myOutput += "<P><a href='http://127.0.0.1:5000/' class='btn btn-primary btn-lg px-4 gap-3'>Back home</a></P>"           
    myOutput += "<P>" + myTable + "</P>"
    myOutput += '</div>'



    if name:
        print('Request for hello page received with name=%s' % name)
        #return render_template('templates/hello.html', name = name)
        return myOutput
        
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
