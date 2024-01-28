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

   text = """New York (CNN Business)Netflix is synonymous with streaming, but its competitors have a distinct advantage that threatens the streaming leader's position at the top.
    Disney has Disney+, but it also has theme parks, plush Baby Yoda dolls, blockbuster Marvel movies and ESPN. Comcast (CMCSA), Amazon (AMZN), ViacomCBS (VIACA), CNN's parent company WarnerMedia and Apple (AAPL) all have their own streaming services, too, but they also have other forms of revenue.
    As for Netflix (NFLX), its revenue driver is based entirely on building its subscriber base. It's worked out well for the company — so far. But it's starting to look like the king of streaming will soon need something other than new subscribers to keep growing.
    The streaming service reported Tuesday it now has 208 million subscribers globally, after adding 4 million subscribers in the first quarter of 2021. But that number missed expectations and the forecasts for its next quarter were also pretty weak.
    That was a big whiff for Netflix — a company coming off a massive year of growth thanks in large part to the pandemic driving people indoors — and Wall Street's reaction has not been great.
    The company's stock dropped as much as 8% on Wednesday, leading some to wonder what the future of the streamer looks like if competition continues to gain strength, people start heading outdoors and if, most importantly, its growth slows.
    "If you hit a wall with [subscriptions] then you pretty much don't have a super growth strategy anymore in your most developed markets," Michael Nathanson, a media analyst and founding partner at MoffettNathanson, told CNN Business. "What can they do to take even more revenue out of the market, above and beyond streaming revenues?"
    Or put another way, the company's lackluster user growth last quarter is a signal that it wouldn't hurt if Netflix — a company that's lived and died with its subscriber numbers — started thinking about other ways to make money.
    An ad-supported Netflix? Not so fast
    There are ways for Netflix to make money other than raising prices or adding subscribers. The most obvious: selling advertising.
    Netflix could have 30-second commercials on their programming or get sponsors for their biggest series and films. TV has worked that way forever, why not Netflix?
    That's probably not going to happen, given that CEO Reed Hastings has been vocal about the unlikelihood of an ad-supported Netflix service. His reasoning: It doesn't make business sense.
    "It's a judgment call... It's a belief we can build a better business, a more valuable business [without advertising]," Hastings told Variety in September. "You know, advertising looks easy until you get in it. Then you realize you have to rip that revenue away from other places because the total ad market isn't growing, and in fact right now it's shrinking. It's hand-to-hand combat to get people to spend less on, you know, ABC and to spend more on Netflix."
    Hastings added that "there's much more growth in the consumer market than there is in advertising, which is pretty flat."
    He's also expressed doubts about Netflix getting into live sports or news, which could boost the service's allure to subscribers, so that's likely out, too, at least for now.
    So if Netflix is looking for other forms of near-term revenue to help support its hefty content budget ($17 billion in 2021 alone) then what can it do? There is one place that could be a revenue driver for Netflix, but if you're borrowing your mother's account you won't like it.
    Netflix could crack down on password sharing — a move that the company has been considering lately.
    "Basically you're going to clean up some subscribers that are free riders," Nathanson said. "That's going to help them get to a higher level of penetration, definitely, but not in long-term."
    Lackluster growth is still growth
    Missing projections is never good, but it's hardly the end of the world for Netflix. The company remains the market leader and most competitors are still far from taking the company on. And while Netflix's first-quarter subscriber growth wasn't great, and its forecasts for the next quarter alarmed investors, it was just one quarter.
    Netflix has had subscriber misses before and it's still the most dominant name in all of streaming, and even lackluster growth is still growth. It's not as if people are canceling Netflix in droves.
    Asked about Netflix's "second act" during the company's post-earnings call on Tuesday, Hastings again placed the company's focus on pleasing subscribers.
    "We do want to expand. We used to do that thing shipping DVDs, and luckily we didn't get stuck with that. We didn't define that as the main thing. We define entertainment as the main thing," Hastings said.
    He added that he doesn't think Netflix will have a second act in the way Amazon has had with Amazon shopping and Amazon Web Services. Rather, Netflix will continue to improve and grow on what it already does best.
    "I'll bet we end with one hopefully gigantic, hopefully defensible profit pool, and continue to improve the service for our members," he said. "I wouldn't look for any large secondary pool of profits. There will be a bunch of supporting pools, like consumer products, that can be both profitable and can support the title brands."""

 #  bert_model = Summarizer()
 #  ext_summary = bert_model(text, ratio=0.5)

 #  print(ext_summary)

   tokens_input = tokenizer.encode("summarize: " + text,
                                return_tensors='pt',
                                max_length=tokenizer.model_max_length,
                                truncation=True)


   summary_ids = model.generate(tokens_input, min_length=80, 
                            max_length=150, length_penalty=15, 
                            num_beams=2)
   summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

   print(summary)











   tempOutput = "" 
   i = 0        
   for result in results:
        tempContent = result["content"]    
        tempContent = tempContent[0:1000]  

        tempOutput = tempOutput + result["metadata_spo_item_name"] + ";;" + str(round(result["@search.reranker_score"],2)) + ";;" + tempContent + ",,"


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
